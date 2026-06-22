# Mainnet Launch Readiness

Use this file before launching or materially changing a Solana production app.

## Readiness Gates

| Gate | Pass criteria |
| --- | --- |
| Program safety | Audit or structured review complete, upgrade authority policy documented, emergency contacts known |
| Transaction UX | Simulation, priority fee, blockhash, retry, and error surfaces tested |
| RPC resilience | Separate read/write capacity, fallback plan, rate limits understood |
| Data freshness | Indexer/webhook lag monitored, replay procedure tested |
| Wallet coverage | Desktop, mobile, hardware, versioned transactions, unsupported paths handled |
| Observability | Logs include signature, wallet/session id, provider, slot, commitment, program id, release SHA |
| Runbooks | Known failure modes have owners and mitigations |
| Rollback | Feature flags, frontend rollback, backend queue pause, and config rollback tested |
| Comms | Internal war room, external status wording, support macros ready |

## War Room Roles

- Incident commander: owns severity, timeline, and decisions.
- Chain engineer: owns transaction/program/RPC diagnosis.
- Backend/indexer engineer: owns queues, webhooks, databases, workers.
- Frontend/wallet engineer: owns user flow, wallet adapter, release rollback.
- Comms/support owner: owns status page, social, tickets, internal updates.
- Security owner: on call for suspicious activity and privileged actions.

## Preflight Scenarios

Run tabletop tests for:

- Priority fee spike during launch.
- RPC provider 429/503 or websocket disconnects.
- Webhook endpoint down for 30 minutes, then replay.
- Failed transaction after user signs.
- Program custom error from stale frontend assumptions.
- Wallet mobile deep-link failure.
- Duplicate backend retries against hot writable accounts.
- Token account creation/rent failure.
- Suspicious admin action or leaked API key.

## Minimum Dashboards

- Transactions sent, landed, failed, expired.
- Failure rate by instruction and program.
- Confirmation latency p50/p95/p99.
- RPC error rate by provider.
- Priority fee paid and compute units consumed.
- Indexer slot lag and queue age.
- Webhook delivery success and retry count.
- Frontend error rate by release.

## Launch Decision Output

```text
Launch status: go | no-go | conditional go
Blocking risks: <list>
Accepted risks: <list with owner>
Rollback triggers: <metric/threshold>
War-room owners: <names/roles>
First-hour checks: <ordered list>
Customer/support notes: <known limitations>
```
