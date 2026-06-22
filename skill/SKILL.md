---
name: solana-mainnet-ops
description: Production operations and incident response for Solana apps. Use for mainnet launch readiness, failed transaction triage, RPC/congestion diagnosis, priority fees, confirmation issues, indexer/webhook drift, program log analysis, wallet/user-impact incidents, security first response, postmortems, and operational hardening. Complements solana-dev, Helius, Jupiter, Trail of Bits, and infrastructure skills.
user-invocable: true
---

# Solana Mainnet Ops

Use this skill when a Solana app is preparing for mainnet, failing in production, or needs an operational reliability workflow. Focus on diagnosis, mitigation, communication, and follow-up, not only code changes.

## Core Rules

1. Stabilize first: identify user impact, current blast radius, and immediate mitigation before deep refactors.
2. Do not request or handle private keys, seed phrases, raw signing authority, or privileged production credentials.
3. Do not move funds, rotate authorities, upgrade programs, pause markets, or change allowlists without explicit human approval.
4. Prefer evidence over guesses: transaction signatures, program logs, RPC status, slot lag, dashboard screenshots, webhook delivery logs, deploy SHA, and recent config changes.
5. Separate user-facing certainty from internal hypotheses.
6. Every incident deliverable must include owner, severity, current state, mitigation, next check, and follow-up.

## Operating Procedure

1. Classify the work:

| User need | Load |
| --- | --- |
| Active outage or production incident | [triage.md](triage.md) |
| Failed transaction, simulation, wallet, blockhash, compute, Anchor, token, Jupiter, or program error | [transaction-failures.md](transaction-failures.md) |
| RPC throttling, confirmation delays, congestion, priority fees, websocket instability | [rpc-and-congestion.md](rpc-and-congestion.md) |
| Indexer lag, stale balances, webhook gaps, DAS/API freshness, data mismatch | [indexing-and-webhooks.md](indexing-and-webhooks.md) |
| Program logs, custom error decoding, Anchor constraints, CPI chains | [program-log-analysis.md](program-log-analysis.md) |
| Exploit suspicion, leaked key, suspicious authority, drain attempt, malicious upgrade | [security-incident.md](security-incident.md) |
| Pre-launch readiness, war room, SLOs, rollback criteria, runbooks | [launch-readiness.md](launch-readiness.md) |
| Canonical links, tools, and ecosystem references | [resources.md](resources.md) |

2. Gather minimum incident facts:

- Environment: mainnet-beta, devnet, local validator, fork, or staging.
- First bad time and last known good time with timezone.
- Affected product path: swap, mint, claim, deposit, withdraw, login, webhook, balance view, program instruction.
- Error artifacts: signatures, logs, screenshots, RPC responses, deploy SHA, release notes.
- Scope: percentage of users, wallets, regions, assets, routes, or programs affected.
- Recent changes: deploys, IDL, RPC provider, priority-fee config, program upgrade, feature flag, token account migration, webhook endpoint, indexer schema.

3. If logs are pasted or available in a file, run the classifier when possible:

```bash
python scripts/classify_solana_issue.py path/to/log.txt
```

4. Deliver in this order:

- Severity and current user impact.
- Most likely domain and confidence.
- Immediate mitigation options with tradeoffs.
- Exact next checks and commands/tools.
- User-facing update if users are affected.
- Durable fix and postmortem follow-up.

## Agent Routing

| Task type | Suggested agent |
| --- | --- |
| Active incident coordination, severity, mitigation, communication | `solana-incident-commander` |
| Deep technical diagnosis, observability, dashboards, RPC/provider analysis | `solana-reliability-engineer` |
| Incident review, postmortem, action items, customer-facing summary | `solana-postmortem-writer` |

## Commands

| Command | Purpose |
| --- | --- |
| `/triage-mainnet` | Run a structured incident triage from logs, signatures, screenshots, and current state |
| `/launch-readiness` | Produce a mainnet launch readiness checklist and war-room plan |
| `/postmortem` | Convert timeline and evidence into a clean postmortem |

## Delegate Rather Than Duplicate

- Program implementation: use `solana-dev-skill`.
- Security audit depth: use Trail of Bits or Solana auditor skills, then return here for incident response and operational follow-through.
- Helius RPC, DAS, webhook, and enhanced transaction details: use Helius tools or MCP if configured.
- Jupiter route or swap integration specifics: use Jupiter skills, then return here for production failure handling.
- Cloudflare/Vercel deployment behavior: use infra skills, then return here for incident coordination.
