# Security Incident First Response

Use this file when there may be an exploit, leaked key, suspicious authority change, malicious upgrade, drain, oracle manipulation, webhook spoofing, or data-integrity incident.

## Safety Rules

- Do not ask the user to paste private keys, seed phrases, mnemonic words, production API secrets, or signing payloads.
- Do not recommend fund movement, authority rotation, program upgrade, freeze, pause, or allowlist changes as executable steps unless a human explicitly approves.
- Preserve evidence before changing state.
- Distinguish containment from recovery.

## First Response

1. Classify the threat:
   - Funds at risk
   - Authority compromise
   - Program exploit
   - Frontend/domain compromise
   - Oracle/data manipulation
   - RPC/indexer spoofing or stale-state risk
   - Webhook/API secret compromise
2. Preserve evidence:
   - Signatures, slots, account snapshots, upgrade authority, deploy SHA, DNS records, CDN config, logs.
3. Stop amplification:
   - Disable risky frontend calls, pause bots/workers, stop retries, revoke non-critical API keys, switch UI to warning/read-only state.
4. Decide containment options with explicit human approval:
   - Rotate API keys.
   - Change upgrade authority or multisig policy.
   - Freeze or pause protocol-specific functionality.
   - Move treasury or hot-wallet funds.
   - Upgrade or close vulnerable program paths.
5. Communicate only verified facts externally.

## Evidence Checklist

- Program id, upgrade authority, program data account.
- Relevant token mints, authorities, freeze authorities, transfer-hook programs.
- Treasury/hot wallet addresses and recent outgoing transfers.
- Admin actions from multisig, governance, or deployer.
- Frontend deploy SHA and DNS/CDN history.
- RPC/provider responses from at least two sources.
- Webhook delivery ids and request signatures.

## Red Flags

- Unknown upgrade to production program.
- Authority changed outside multisig process.
- Drain-like repeated transfers to new addresses.
- Oracle price divergence affecting liquidations or swaps.
- Frontend transaction contains unexpected instruction or account.
- Webhook events accepted without verification.
- User signatures requested for unrelated programs.

## Post-Containment

- Reconcile affected accounts from chain state.
- Write a timeline with UTC timestamps.
- Identify the failed control.
- Add monitoring for the exact abuse path.
- Prepare a user-safe disclosure with known impact and next update time.
