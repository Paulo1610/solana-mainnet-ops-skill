# Solana Mainnet Ops Skill

Production operations, incident response, and launch-readiness workflows for Solana builders using Claude Code, Codex, or other agentic coding environments.

## Why this exists

Solana teams can usually find help for writing programs, building frontends, or running audits. The harder recurring problem starts after launch: transactions fail in production, RPCs throttle, priority fees spike, webhooks drift, indexers lag, users report wallet errors, and teams need a calm incident workflow fast.

`solana-mainnet-ops-skill` turns a coding agent into a Solana production operations partner. It helps founders and engineers triage incidents, classify transaction failures, choose the right observability checks, prepare launch war rooms, draft postmortems, and harden systems before mainnet traffic arrives.

## What it covers

- Transaction failure triage across Solana runtime, wallet, RPC, priority-fee, blockhash, compute, account-lock, Anchor, Token-2022, Jupiter, and custom program errors
- RPC, congestion, and confirmation-health diagnosis
- Indexer, webhook, websocket, and data freshness checks
- Program log and custom-error analysis
- Security incident first response for leaked keys, suspicious authority changes, malicious upgrades, drain attempts, and oracle/indexer anomalies
- Mainnet launch readiness checklists, war-room roles, rollback criteria, SLOs, and postmortem templates
- A deterministic CLI classifier for logs, support tickets, and pasted error output

## Repository structure

```text
solana-mainnet-ops-skill/
|-- README.md
|-- LICENSE
|-- install.sh
|-- install.ps1
|-- skill/
|   |-- SKILL.md
|   |-- triage.md
|   |-- transaction-failures.md
|   |-- rpc-and-congestion.md
|   |-- indexing-and-webhooks.md
|   |-- program-log-analysis.md
|   |-- security-incident.md
|   |-- launch-readiness.md
|   `-- resources.md
|-- agents/
|   |-- solana-incident-commander.md
|   |-- solana-reliability-engineer.md
|   `-- solana-postmortem-writer.md
|-- commands/
|   |-- triage-mainnet.md
|   |-- launch-readiness.md
|   `-- postmortem.md
|-- scripts/
|   `-- classify_solana_issue.py
|-- examples/
|   |-- production-incident-input.txt
|   |-- jupiter-swap-failure-input.txt
|   |-- rpc-throttling-input.txt
|   |-- webhook-lag-input.txt
|   `-- production-incident-output.md
`-- tests/
    |-- fixtures/
    |   `-- sample-errors.txt
    `-- test_skill_structure.py
```

## How it works

The skill uses progressive loading:

1. `skill/SKILL.md` classifies the user's problem and routes the agent to one focused workflow.
2. The focused workflow tells the agent what evidence to gather, what failure modes to distinguish, and how to format the answer.
3. Optional agents and commands provide reusable incident, reliability, launch, and postmortem workflows.
4. `scripts/classify_solana_issue.py` gives the agent a deterministic first pass over noisy logs or support tickets.

This keeps the context small while still making the agent behave like a production Solana operator.

## Quick demo

Run the classifier against a realistic incident report:

```bash
python scripts/classify_solana_issue.py examples/production-incident-input.txt --pretty
```

Then compare with the expected agent-style output:

```bash
cat examples/production-incident-output.md
```

This shows the intended flow: detect signals, identify the likely failing layers, recommend immediate mitigation, then propose durable fixes and communication.

Additional realistic inputs are included:

```bash
python scripts/classify_solana_issue.py examples/rpc-throttling-input.txt --pretty
python scripts/classify_solana_issue.py examples/jupiter-swap-failure-input.txt --pretty
python scripts/classify_solana_issue.py examples/webhook-lag-input.txt --pretty
```

## Installation

Install to a project-level `.claude/skills/solana-mainnet-ops` directory:

```bash
git clone https://github.com/YOUR_ORG/solana-mainnet-ops-skill
cd solana-mainnet-ops-skill
./install.sh --project /path/to/your-solana-project
```

Install to user-level Claude Code skills:

```bash
./install.sh --user
```

Install for agent configs that use `.agents/` instead of `.claude/`:

```bash
./install.sh --project /path/to/your-solana-project --agents
```

On Windows PowerShell:

```powershell
.\install.ps1 -Project "C:\path\to\your-solana-project"
.\install.ps1 -User
.\install.ps1 -Project "C:\path\to\your-solana-project" -Agents
```

## Usage examples

```text
"Use solana-mainnet-ops to triage this failed transaction and tell me what to check next."
"Our swaps started failing after a traffic spike. Diagnose whether this is RPC, priority fees, slippage, or program failure."
"Create a mainnet launch readiness checklist for our Anchor program, Next.js frontend, Helius webhooks, and Jupiter swap path."
"Write a user-facing incident update and an internal postmortem from these logs."
```

## Classifier script

The bundled classifier is intentionally small and deterministic. It does not replace deeper analysis; it gives the agent a reliable first pass.

```bash
python scripts/classify_solana_issue.py tests/fixtures/sample-errors.txt
cat error.log | python scripts/classify_solana_issue.py
```

It emits JSON with detected signals, likely domains, severity, hypotheses, and next checks.

Markdown output is also available for quick reports:

```bash
python scripts/classify_solana_issue.py examples/production-incident-input.txt --format markdown
```

## Validation

```bash
python -m unittest discover -s tests
python scripts/classify_solana_issue.py tests/fixtures/sample-errors.txt
python scripts/classify_solana_issue.py examples/production-incident-input.txt --format markdown
```

On Windows, the PowerShell installer can be smoke-tested with:

```powershell
.\install.ps1 -Dest "C:\tmp\solana-mainnet-ops-test"
```

## Design principles

- Progressive loading: `skill/SKILL.md` routes to focused files only when needed.
- Production bias: every workflow ends in checks, mitigation, owner, user impact, and follow-up.
- Tool-agnostic: works with Solana CLI, Helius, Triton, QuickNode, custom RPCs, explorers, logs, dashboards, and MCP tools when available.
- Safety first: avoids key handling, signing, fund movement, upgrades, or authority changes without explicit human approval.

## Fit with Solana AI Kit

This skill complements the Solana AI Kit ecosystem by focusing on post-launch reliability rather than only build-time development. It can sit beside `solana-dev-skill`, Helius infra skills, Jupiter skills, security skills, and startup/GTM skills without duplicating them.

## Why it belongs in the standard kit

Most Solana skills help builders write code, integrate protocols, or audit programs. Builders still need help when the product is live and the failure crosses domains: wallet UX, blockhash expiry, RPC capacity, priority fees, account locks, indexer freshness, webhooks, support tickets, and incident communication.

This skill fills that operational gap. It gives any agent a repeatable production workflow: classify severity, preserve evidence, isolate the failing layer, choose a safe mitigation, explain user impact, and turn the incident into durable runbook improvements.

## License

MIT. See [LICENSE](LICENSE).
