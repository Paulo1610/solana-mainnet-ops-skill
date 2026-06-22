# Transaction Failure Triage

Use this file for failed sends, simulations, confirmations, wallet errors, swap failures, token account issues, and program errors.

## Decision Tree

1. Did the user sign?
   - No: wallet adapter, mobile deep link, permissions, unsupported transaction version, session expiry.
   - Yes: continue.
2. Is there a signature?
   - No: send/raw transaction, RPC throttling, blockhash expiry before send, frontend/backend exception.
   - Yes: fetch signature status and logs.
3. Did the transaction land?
   - No: blockhash expiry, insufficient priority fee, dropped by RPC, leader/network issue.
   - Yes but failed: decode logs and error.
4. Did simulation fail the same way?
   - Yes: deterministic program/runtime/account issue.
   - No: state changed between simulation and execution, slippage, account locks, priority fee, blockhash, or route freshness.

## Common Signals

| Signal | Likely domain | Next check |
| --- | --- | --- |
| `BlockhashNotFound`, expired blockheight | Blockhash lifecycle | Confirm blockhash age, wallet signing latency, retry strategy |
| `AccountInUse` | Parallel writes/account lock contention | Identify hot accounts, queues, retries, batching |
| `ComputationalBudgetExceeded` | Compute budget too low or route too complex | Compare CU consumed, set compute unit limit, reduce CPI depth |
| `insufficient funds` | SOL rent/fee/token balance | Check fee payer SOL, token account balance, ATA creation rent |
| `custom program error: 0x...` | Program-defined error | Decode with IDL, Anchor error map, or program source |
| `ConstraintSeeds`, `ConstraintOwner`, `ConstraintToken*` | Anchor account validation | Check PDA seeds, token program, ATA, mint, owner |
| `SlippageToleranceExceeded`, route out amount changed | Market movement/liquidity | Refresh quote, route, slippage, exact-in/out mode |
| `UnsupportedTransactionVersion` | RPC/client compatibility | Confirm v0 support and address lookup table availability |
| `Signature verification failed` | Wallet/signers mismatch | Check required signers, fee payer, serialized transaction mutation |
| `Transaction too large` | Message size/ALT issue | Use address lookup tables, split instructions |
| `Attempt to debit an account but found no record of a prior credit` | Missing funded account | Confirm account existence, payer, rent, cluster |
| `InvalidAccountData` | Wrong account type or stale client assumption | Fetch account owner/data length, compare IDL/schema |

## Checks

Use whichever tools are available:

```bash
solana confirm -v <SIGNATURE>
solana transaction-history <ADDRESS> --limit 20
solana account <ACCOUNT>
solana logs <PROGRAM_ID>
```

If an RPC or Helius MCP is configured, fetch:

- Signature status with commitment levels.
- Full transaction logs.
- Parsed account changes.
- Priority fee estimate around the failing accounts.
- Enhanced transaction classification.

## Mitigation Patterns

- Blockhash expiry: fetch blockhash late, shorten signing path, retry with fresh blockhash, surface wallet delay to user.
- Compute exhaustion: set compute unit limit from simulation plus headroom; investigate CPI growth before blindly raising caps.
- Priority fee underpricing: estimate fees from writable accounts, cap by user/value-at-risk, expose fee state in UI.
- Slippage: refresh quotes close to signing; never silently widen user slippage.
- Account locks: serialize writes for hot accounts, split queues by account key, avoid retry storms.
- ATA/rent failures: preflight fee payer and associated token account creation path.
- Versioned tx failures: verify RPC supports v0 transactions and address lookup tables.

## Output Format

```text
Likely cause: <domain> (<confidence>)
Evidence: <logs/status/signature facts>
Immediate user-safe mitigation: <action>
Engineering fix: <code/config/runbook change>
Verification: <command/dashboard/metric>
Residual risk: <what may still fail>
```
