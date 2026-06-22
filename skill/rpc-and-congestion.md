# RPC, Congestion, and Confirmation Health

Use this file when transactions are delayed, dropped, inconsistently confirmed, throttled, or only failing through one provider.

## Diagnose Provider vs Network vs Client

| Symptom | Likely domain | Check |
| --- | --- | --- |
| One provider has high errors, another works | Provider health or rate limit | Compare `getHealth`, slot, block height, send rate, 429/503 logs |
| All providers slow, high priority fees | Network congestion/hot accounts | Check priority fees by writable accounts, confirmation latency |
| Simulation ok but send fails with expiry | Client signing/retry/blockhash lifecycle | Measure time from blockhash to send and confirm |
| Reads stale but writes confirm | Indexer/cache lag | Compare direct RPC account fetch vs indexer/API |
| Websockets drop but HTTP works | Subscription path | Reconnect policy, heartbeat, provider websocket status |

## Minimum Metrics

- Send success rate by provider.
- Simulation failure rate by instruction.
- Confirmation latency p50/p95/p99.
- Slot lag by provider.
- RPC HTTP status codes and error codes.
- Priority fee paid vs estimated by writable accounts.
- Blockhash age at signing and send time.
- Retry count and duplicate signature rate.

## Priority Fee Guidance

Priority fees should be based on the transaction's writable accounts, current network conditions, and user value at risk. Avoid one global magic fee.

Recommended agent behavior:

1. Simulate to estimate compute units.
2. Add bounded compute headroom.
3. Estimate micro-lamports per compute unit using recent priority fees for writable accounts.
4. Cap the total fee by product policy.
5. Show high-fee states to users before they sign when material.

## RPC Provider Strategy

- Use separate providers or keys for reads, writes, webhooks, and backfills where possible.
- Use quorum or fallback reads for user-visible balances and critical settlement state.
- Avoid retry storms: exponential backoff with jitter and idempotency.
- Prefer durable queues for backend senders.
- Record provider, endpoint class, request id, slot, commitment, and elapsed time in logs.

## Confirmation Strategy

- Track last valid block height for every signed transaction.
- Stop polling when the blockhash expires; rebuild and re-sign when safe.
- Distinguish "not found yet" from "expired" from "landed failed".
- Never claim success from frontend optimistic state alone.

## Incident Mitigations

- Route writes to a healthier provider.
- Temporarily raise priority fee caps for high-value flows.
- Disable non-critical write paths to reduce account contention.
- Degrade stale reads with a visible "syncing" state.
- Pause workers that are producing duplicate sends or hot-account contention.
