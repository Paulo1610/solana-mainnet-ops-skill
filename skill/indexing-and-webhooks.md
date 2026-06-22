# Indexing, Webhooks, and Data Freshness

Use this file when users see stale balances, missing NFTs, delayed activity, duplicate events, webhook gaps, or data mismatches between the chain and product UI.

## Source of Truth Order

1. Chain state at a specific slot and commitment.
2. RPC account or transaction response.
3. Provider-enhanced APIs such as DAS/enhanced transactions.
4. Internal indexer database.
5. Cache/CDN/frontend state.

Always name which layer produced each claim.

## Common Failure Modes

| Symptom | Likely cause | Next check |
| --- | --- | --- |
| Transaction confirmed but UI still pending | Indexer lag or webhook gap | Compare confirmed slot to indexed slot |
| Duplicate activity rows | Retry or idempotency bug | Check event unique key and webhook delivery ids |
| Missing NFT/token metadata | DAS/API lag, cache, wrong owner/mint | Direct account fetch, metadata account, owner token accounts |
| Webhooks delayed or missing | Provider delivery, endpoint 5xx, queue backlog | Delivery log, endpoint logs, retry count |
| Balance mismatch | Commitment mismatch, stale cache, token extension behavior | Fetch account with same commitment and token program |
| Backfill corrupts live state | Non-idempotent replay | Check checkpointing and upsert semantics |

## Webhook Consumer Requirements

- Verify provider signature if available.
- Persist raw delivery id, signature, slot, event type, and received time.
- Process idempotently by `(provider, delivery_id)` and domain-specific event key.
- Separate ingestion from processing with a durable queue.
- Make replay safe.
- Alert on delivery failures, queue age, and indexed-slot lag.

## Freshness Checks

Ask for or compute:

- Highest finalized/confirmed slot seen by RPC.
- Highest slot processed by indexer.
- Oldest unprocessed queue item age.
- Webhook delivery success rate.
- Cache age for affected endpoint.
- Number of events needing replay.

## Mitigation Patterns

- Show "syncing" rather than incorrect final state.
- Reconcile affected wallets or accounts from direct RPC.
- Replay webhooks from the last known good checkpoint.
- Temporarily bypass stale cache for affected product path.
- Disable non-idempotent backfills until duplicate handling is fixed.

## Output Format

```text
Truth layer checked: <chain/RPC/API/indexer/cache>
Freshness gap: <slots/time/events>
Affected objects: <wallets/mints/program accounts/routes>
Mitigation: <replay/bypass/degrade/pause>
Permanent fix: <idempotency/checkpoint/schema/alert>
```
