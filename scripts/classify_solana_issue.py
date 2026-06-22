#!/usr/bin/env python3
"""Classify Solana production errors from logs or support text.

This script is deterministic by design. It gives an agent a reliable first pass,
not a final diagnosis.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    name: str
    domain: str
    severity: str
    pattern: str
    hypothesis: str
    next_check: str


RULES: tuple[Rule, ...] = (
    Rule(
        "production_user_impact",
        "incident_impact",
        "sev1",
        r"\bSEV1\b|outage|core .* unavailable|many users|[2-9]\d% (?:of )?.*fail|launch .*fail|mint attempts fail|users .*cannot|users .*can't",
        "A production user path appears materially degraded.",
        "Set an incident owner, estimate blast radius, choose a mitigation, and start a time-boxed update cadence.",
    ),
    Rule(
        "blockhash_expired",
        "transaction_lifecycle",
        "sev2",
        r"BlockhashNotFound|TransactionExpiredBlockheightExceeded|blockhash.*expired|last valid block height",
        "The transaction likely expired before landing.",
        "Measure time from blockhash fetch to signature and confirmation; rebuild with a fresh blockhash on retry.",
    ),
    Rule(
        "account_lock_contention",
        "runtime_accounts",
        "sev2",
        r"AccountInUse|account.*already.*in use|WouldExceedMaxAccountCostLimit",
        "Writable account contention or hot-account retries may be blocking execution.",
        "Group failures by writable accounts and inspect worker concurrency/retry behavior.",
    ),
    Rule(
        "compute_exhausted",
        "runtime_compute",
        "sev2",
        r"ComputationalBudgetExceeded|exceeded maximum number of instructions|consumed .* of .* compute units",
        "The transaction may need a higher compute limit or a less expensive instruction path.",
        "Compare simulated compute usage with the configured compute unit limit and CPI depth.",
    ),
    Rule(
        "insufficient_funds",
        "balances_and_fees",
        "sev2",
        r"insufficient funds|Attempt to debit an account but found no record|0x1\b",
        "The fee payer or token source account may not have enough SOL/token balance or rent.",
        "Check fee payer SOL, ATA creation rent, token account balance, and cluster.",
    ),
    Rule(
        "anchor_constraint",
        "program_validation",
        "sev2",
        r"Constraint[A-Za-z]+|A seeds constraint was violated|AnchorError",
        "An Anchor account constraint failed before instruction logic completed.",
        "Decode the exact constraint, then verify PDA seeds, owner, signer, mutability, mint, and token program.",
    ),
    Rule(
        "custom_program_error",
        "program_error",
        "sev2",
        r"custom program error: (0x[0-9a-fA-F]+|\d+)",
        "A program-defined error was returned.",
        "Decode the error with the program IDL/source and map it to the failing account or state.",
    ),
    Rule(
        "slippage_or_route_stale",
        "defi_route",
        "sev2",
        r"SlippageToleranceExceeded|slippage|ExactOutAmountNotMatched|route.*stale|price impact|quote.*expired|out amount",
        "The quote or route may have gone stale before execution.",
        "Refresh the quote close to signing and compare expected vs actual out amount/liquidity.",
    ),
    Rule(
        "jupiter_swap_path",
        "defi_route",
        "sev2",
        r"Jupiter|Ultra API|Metis|swap transaction|route plan|shared accounts route|dynamic slippage",
        "The failing path appears to involve a Jupiter swap or route construction flow.",
        "Check quote freshness, route plan, slippage, token accounts, priority fee settings, and Jupiter response errors.",
    ),
    Rule(
        "token_2022_or_extension",
        "token_program",
        "sev2",
        r"Token-2022|Token2022|transfer hook|TransferHook|confidential transfer|memo required|immutable owner|extension",
        "The token may use Token-2022 extensions or transfer-hook behavior that the client path did not account for.",
        "Fetch the mint and token account owners/extensions, then verify the transaction includes required hook or memo accounts.",
    ),
    Rule(
        "rpc_throttle_or_provider",
        "rpc_provider",
        "sev2",
        r"\b429\b|Too Many Requests|\b503\b|Service Unavailable|rate limit|Node is behind|Block not available",
        "The RPC provider may be throttling, unhealthy, or lagging.",
        "Compare slot lag and error rate across providers; separate read/write traffic and apply backoff.",
    ),
    Rule(
        "unsupported_transaction_version",
        "client_rpc_compatibility",
        "sev2",
        r"UnsupportedTransactionVersion|maxSupportedTransactionVersion|VersionedTransaction",
        "The client or RPC path may not support versioned transactions or address lookup tables.",
        "Confirm v0 transaction support in every RPC/client path and verify ALT availability.",
    ),
    Rule(
        "signature_or_signer_mismatch",
        "wallet_signing",
        "sev2",
        r"Signature verification failed|missing required signature|unknown signer|not enough signers",
        "The transaction signers, fee payer, or serialized message may not match what the wallet signed.",
        "Verify required signers, fee payer, wallet adapter path, and post-signature transaction mutation.",
    ),
    Rule(
        "transaction_too_large",
        "message_size",
        "sev2",
        r"Transaction too large|packet too large|encoded solana_sdk::transaction::versioned::VersionedTransaction too large",
        "The message may exceed Solana transaction size limits.",
        "Use address lookup tables, reduce accounts, or split the workflow into multiple transactions.",
    ),
    Rule(
        "webhook_or_indexer_lag",
        "indexing_webhooks",
        "sev3",
        r"webhook|delivery failed|queue lag|indexed slot|stale balance|missing event|duplicate event",
        "The chain transaction may be fine while product data is stale or duplicated.",
        "Compare confirmed chain slot to indexed slot and inspect webhook delivery/replay/idempotency.",
    ),
    Rule(
        "security_red_flag",
        "security_incident",
        "sev0",
        r"drain|exploit|compromised|leaked key|seed phrase|unexpected upgrade|authority changed|malicious",
        "There may be a security incident or privileged authority compromise.",
        "Preserve evidence, stop amplification, verify authorities, and require human approval for privileged actions.",
    ),
)


SIGNATURE_PATTERN = re.compile(
    r"\b(?:signature|sig|tx|transaction)\s*[:=]\s*([1-9A-HJ-NP-Za-km-z]{64,88})\b",
    flags=re.IGNORECASE,
)
PROGRAM_PATTERN = re.compile(
    r"\b(?:program|program id|program_id)\s*[:=]\s*([1-9A-HJ-NP-Za-km-z]{32,44})\b",
    flags=re.IGNORECASE,
)


def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    return sys.stdin.read()


def classify(text: str) -> dict[str, object]:
    matches = []
    domains: dict[str, int] = {}
    severity_order = {"sev3": 1, "sev2": 2, "sev1": 3, "sev0": 4}
    max_severity = "sev3"

    for rule in RULES:
        found = re.findall(rule.pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if not found:
            continue
        domains[rule.domain] = domains.get(rule.domain, 0) + len(found)
        if severity_order[rule.severity] > severity_order[max_severity]:
            max_severity = rule.severity
        matches.append(
            {
                "signal": rule.name,
                "domain": rule.domain,
                "severity": rule.severity,
                "matches": len(found),
                "hypothesis": rule.hypothesis,
                "next_check": rule.next_check,
            }
        )

    likely_domains = sorted(domains.items(), key=lambda item: (-item[1], item[0]))
    return {
        "severity": max_severity if matches else "unknown",
        "likely_domains": [{"domain": domain, "score": score} for domain, score in likely_domains],
        "signals": matches,
        "artifacts": extract_artifacts(text),
        "suggested_workflow": build_workflow(matches, likely_domains),
        "summary": build_summary(matches, likely_domains),
    }


def extract_artifacts(text: str) -> dict[str, list[str]]:
    signatures = sorted(set(SIGNATURE_PATTERN.findall(text)))
    programs = sorted(set(PROGRAM_PATTERN.findall(text)))
    return {
        "signatures": signatures,
        "programs": programs,
    }


def build_workflow(matches: Iterable[dict[str, object]], likely_domains: list[tuple[str, int]]) -> list[str]:
    matches = list(matches)
    if not matches:
        return [
            "Collect transaction signature, full logs, RPC provider, slot, commitment, deploy SHA, and first bad time.",
            "Run signature status and compare direct RPC state with product/indexer state.",
        ]

    steps = [
        "Set severity and user impact before changing production systems.",
        "Preserve signatures, logs, RPC responses, release SHA, and provider dashboard evidence.",
    ]
    top_domain = likely_domains[0][0] if likely_domains else ""
    if top_domain == "security_incident":
        steps.append("Switch to the security incident workflow before any privileged action.")
    elif top_domain == "incident_impact":
        steps.append("Open the active incident workflow, assign owners, and publish an internal update cadence.")
    elif top_domain == "rpc_provider":
        steps.append("Compare provider slot lag, 429/503 rate, send success, and confirmation latency across RPCs.")
    elif top_domain == "indexing_webhooks":
        steps.append("Compare confirmed chain slot with indexed slot and webhook delivery/replay state.")
    elif top_domain in {"program_error", "program_validation", "runtime_compute"}:
        steps.append("Fetch full transaction logs, identify the first failing program/CPI, and decode custom or Anchor errors.")
    elif top_domain in {"defi_route", "token_program"}:
        steps.append("Refresh route/token account evidence and separate quote construction failure from on-chain execution failure.")
    elif top_domain == "transaction_lifecycle":
        steps.append("Measure blockhash age, wallet signing latency, retry policy, and expiration handling.")
    steps.append("Return immediate mitigation, durable fix, verification check, owner, and next update time.")
    return steps


def build_summary(matches: Iterable[dict[str, object]], likely_domains: list[tuple[str, int]]) -> str:
    matches = list(matches)
    if not matches:
        return "No known Solana production issue signals detected. Gather signature status, logs, RPC errors, and recent deploy/config changes."
    top = likely_domains[0][0] if likely_domains else "unknown"
    names = ", ".join(str(match["signal"]) for match in matches[:4])
    return f"Detected {len(matches)} signal(s). Top domain: {top}. Signals: {names}."


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Solana production issue text.")
    parser.add_argument("path", nargs="?", help="Optional log file. Reads stdin when omitted.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    args = parser.parse_args()

    text = read_input(args.path)
    result = classify(text)
    if args.format == "markdown":
        print(to_markdown(result))
    else:
        print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0


def to_markdown(result: dict[str, object]) -> str:
    lines = ["# Solana Issue Classification", ""]
    lines.append(f"Severity: `{result['severity']}`")
    lines.append("")
    lines.append(f"Summary: {result['summary']}")
    lines.append("")

    artifacts = result.get("artifacts", {})
    if isinstance(artifacts, dict):
        signatures = artifacts.get("signatures") or []
        programs = artifacts.get("programs") or []
        if signatures or programs:
            lines.append("## Artifacts")
            for signature in signatures:
                lines.append(f"- Signature: `{signature}`")
            for program in programs:
                lines.append(f"- Program: `{program}`")
            lines.append("")

    lines.append("## Likely Domains")
    domains = result.get("likely_domains") or []
    if domains:
        for item in domains:
            lines.append(f"- `{item['domain']}` score {item['score']}")
    else:
        lines.append("- No known domain detected")
    lines.append("")

    lines.append("## Signals")
    signals = result.get("signals") or []
    if signals:
        for item in signals:
            lines.append(f"- `{item['signal']}` ({item['severity']}): {item['hypothesis']}")
            lines.append(f"  Next check: {item['next_check']}")
    else:
        lines.append("- No known signal detected")
    lines.append("")

    lines.append("## Suggested Workflow")
    for step in result.get("suggested_workflow") or []:
        lines.append(f"- {step}")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
