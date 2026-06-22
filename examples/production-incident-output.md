# Example Agent Output

## Severity

SEV1 until proven otherwise. A core launch path is failing for a material share of users. No direct fund-loss signal is shown, but the team should verify whether any users paid fees for failed attempts and whether any successful mints are missing from the UI.

## Likely Failing Layers

1. RPC/provider throttling and transaction lifecycle
   Evidence: `RPC 429 Too Many Requests` and `TransactionExpiredBlockheightExceededError`.
   Hypothesis: the shared RPC key is throttling sends or delaying confirmation long enough for blockhashes to expire.

2. Program/account validation
   Evidence: `AnchorError` and `ConstraintSeeds` on `vault`.
   Hypothesis: at least one client path is deriving the wrong PDA or using stale launch config after the frontend deploy.

3. Indexer/webhook freshness
   Evidence: webhook delivery failure and indexed-slot lag.
   Hypothesis: some landed transactions may be missing from the product UI even if they succeeded on-chain.

## Immediate Mitigation

- Route write traffic to a dedicated healthy RPC key/provider and reduce retry storms.
- Disable or slow only the failing mint path if retries are amplifying account contention.
- Compare successful and failed mint transactions for vault PDA derivation and frontend release SHA.
- Put the UI into a "confirming on-chain state" mode for affected users instead of showing final failure from stale indexer state.
- Pause webhook worker scale-up if duplicate or failing deliveries are increasing queue lag.

## Next Checks

1. Fetch full logs for the listed signature and identify whether it landed failed or expired before landing.
2. Compare slot lag and 429 rate between the old and new RPC write endpoints.
3. Recompute the `vault` PDA from the deployed frontend config and the current program IDL.
4. Compare confirmed chain state with indexed slot for affected wallets.
5. Check whether the webhook consumer is idempotent and whether replay is safe from the last healthy checkpoint.

## Internal Update

Status: mitigating  
Severity: SEV1  
Impact: around 38% of launch mint attempts are failing or appearing stuck since 2026-06-19 14:05 UTC.  
Current hypothesis: the incident combines RPC throttling/blockhash expiry with a possible stale frontend PDA derivation and webhook lag.  
Mitigation: move writes to dedicated RPC capacity, reduce retries, verify PDA derivation, and reconcile affected wallets from direct chain state.  
Next update: 15 minutes or sooner if the RPC switch changes failure rate.

## Durable Fixes

- Add blockhash-age telemetry from blockhash fetch to wallet signature to send.
- Add per-provider send success, 429/503, slot lag, and confirmation-latency dashboards.
- Validate launch config and PDA derivation in CI against the deployed IDL/program ID.
- Make webhook replay idempotent and alert on indexed-slot lag.
- Add a launch rollback trigger for mint failure rate and RPC throttling.
