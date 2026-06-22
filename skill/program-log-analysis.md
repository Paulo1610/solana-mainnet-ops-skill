# Program Log Analysis

Use this file for transaction logs, custom errors, Anchor constraints, CPI chains, compute usage, and account validation failures.

## Log Reading Order

1. Identify top-level program and instruction.
2. Walk CPI calls in order.
3. Record the first failing program, not only the outer wrapper.
4. Capture consumed compute units and compute budget.
5. Decode custom errors using IDL, source code, Anchor error map, or documented program errors.
6. Map each account index in the failing instruction to its key, owner, mutability, signer status, and expected type.

## Anchor-Specific Checks

- `ConstraintSeeds`: recompute PDA seeds and bump.
- `ConstraintOwner`: verify the account owner program.
- `ConstraintSigner`: verify wallet or PDA signer path.
- `ConstraintMut`: check account is writable in the instruction.
- `ConstraintTokenMint`, `ConstraintTokenOwner`, `ConstraintAssociated`: verify mint, authority, associated token derivation, and token program.
- `AccountDidNotDeserialize`: check schema version, discriminator, account initialization, and wrong cluster.

## Runtime Checks

- Account lock contention: hot writable account, repeated retries, queue concurrency.
- Compute exhaustion: CPI depth, loops over account vectors, token extension hooks, heavy deserialization.
- Rent/account creation: payer SOL, ATA creation, account size.
- Transaction size: too many accounts or missing address lookup table.
- Missing required signature: fee payer or authority mismatch.

## Custom Error Workflow

1. Convert hex to decimal if needed.
2. Search local IDL and source for the error code or enum.
3. If the program is external, load the protocol skill/docs when available.
4. Explain the domain meaning, not only the numeric code.
5. Give the exact account/state mismatch likely to produce it.

## Deliverable

```text
Failing program: <program id/name>
Failing instruction/CPI: <instruction path>
Decoded error: <name/code/domain meaning>
Relevant accounts: <keys and expected roles>
Why it failed: <state mismatch>
Fix: <client/program/config/retry>
Test: <unit/integration/simulation case>
```
