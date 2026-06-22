# Active Incident Triage

Use this file for active production incidents. Keep the loop short: state, evidence, mitigation, next check.

## Severity

| Severity | Definition | Default response |
| --- | --- | --- |
| SEV0 | Funds at risk, active exploit, irreversible loss, authority compromise | Freeze risky flows if possible, escalate security owner, preserve evidence, switch to [security-incident.md](security-incident.md) |
| SEV1 | Core production path unavailable or corrupt for many users | Assign incident commander, mitigation owner, comms owner, 15-minute updates |
| SEV2 | Important path degraded, workaround exists, limited scope | Owner plus 30-minute updates |
| SEV3 | Minor degradation, monitoring alert, single integration issue | Track to resolution, no public comms unless user-visible |

## First 10 Minutes

1. Name the incident: product path, start time, severity.
2. Freeze speculative changes. List recent deploys and config changes.
3. Preserve evidence: tx signatures, logs, RPC responses, dashboard screenshots, webhook delivery samples.
4. Identify affected cohorts: wallet, route, token, region, RPC provider, program instruction, frontend version.
5. Pick one immediate mitigation:
   - Disable only the failing route behind a feature flag.
   - Switch RPC provider or quorum reads.
   - Increase compute units or priority fee caps within safe bounds.
   - Raise slippage only if user explicitly controls or confirms it.
   - Degrade to read-only mode for risky write paths.
   - Pause a queue, webhook consumer, or retry worker if it is amplifying harm.
6. Send an internal update with owner, impact, hypothesis, mitigation, and next check.

## Evidence Matrix

| Evidence | What it distinguishes |
| --- | --- |
| Simulation logs | Program/runtime error before send |
| Confirmed failed transaction logs | On-chain execution failure |
| Missing signature on explorer | RPC send, blockhash, wallet, or propagation issue |
| Slot lag by provider | Provider/indexer freshness problem |
| Webhook delivery history | Producer vs consumer vs network issue |
| Error rate by release SHA | Frontend/backend deploy regression |
| Error rate by wallet | Wallet adapter or mobile deep-link issue |
| Error rate by route/token | AMM, liquidity, token account, transfer-hook, or oracle issue |

## Update Template

Internal:

```text
Status: investigating | mitigating | monitoring | resolved
Severity: SEV#
Impact: who is affected and what they cannot do
Started: timestamp and timezone
Current hypothesis: one sentence, include confidence
Mitigation: action underway or completed
Next check: exact command, dashboard, owner, ETA
```

External:

```text
We are investigating elevated failures for <product path> starting around <time>.
Funds are <safe/being assessed/do not claim yet>.
We are applying <mitigation in user-safe language> and will update again by <time>.
```

## Resolution Criteria

An incident is not resolved until:

- Error rate returns to baseline for at least two monitoring windows.
- Backlogs, retries, and webhook queues are drained or explicitly abandoned.
- Affected user state is reconciled.
- The team knows whether funds, balances, or user-visible state were impacted.
- A follow-up owner exists for the durable fix.
