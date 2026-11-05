> Historical pre-separation notes. Paths/commands below are obsolete; use ../README.md.

# CoRA development loop — first local version

This is an opt-in bounded runner, not a background daemon. No automatic merge,
publication, deployment, theory adoption or Knowledge approval is authorized.

## Run

From the repository root:

```sh
python3 tools/development_loop.py status
python3 tools/development_loop.py run --max-cycles 3 --total-seconds 1800
```

Requires an authenticated `codex` executable on PATH. The installed CLI's
`exec`, workspace-write/read-only sandbox, output-schema and final-message
options are used. No model override or approval bypass is supplied.
Implementation and review are separate fresh CLI sessions, run sequentially.
Run in a dedicated clean checkout; do not concurrently edit that checkout.
Private logs and durable state live in ignored `.local/development-loop/`.

## Contract and completion

A contract fixes goal, allowed scope, criterion IDs and check argument arrays.
Checks run directly, without a shell. Use only trusted contracts: commands execute
with the controller's local permissions. The initial pilot only creates a document
authority audit and proposals; it does not resolve policy conflicts itself.

A worker produces implementation results and any decision requests. The controller
runs every required check, then starts an independent read-only reviewer. Completion
requires every criterion exactly once with a pass and concrete evidence, no blocking
findings, no decision requests, all checks successful, and an unchanged source digest
between checks and review. Digests cover tracked and nonignored untracked files,
deletions, symlinks and modes. Workflow controls are checked for changes too.

A failed check or review feeds the next bounded implementation attempt. Process
errors, malformed output, timeouts, source changes and policy changes never complete.
An exclusive local lock prevents overlapping runners. Logs and attempts survive restart;
interrupted work restarts with a fresh attempt rather than resuming partial processes.
A completed run is reusable only while its source digest remains identical.
Limits apply per invocation; there is no monetary budget metering in this version.
Timeout/interruption terminates the subprocess group. Do not use a shell around
this runner that retries indefinitely.

## Human decisions

Adopted owner decisions are recorded in `workflow/decisions.json` and the relevant
authoritative document. Consult that ledger before repeating an old decision request;
old run states are historical records, not evidence that a resolved decision is pending.

Decisions include conceptual changes, acceptance/evaluation label changes, changing
empirical support requirements, broadening scope, and major cost/quality tradeoffs.
A decision request must describe evidence, alternatives, recommendation and blocked work.
`decision_required` cannot automatically resume. A human response is recorded in a
revised contract, with a new state directory and a reference to the prior decision.
Never interpret no reply as consent. Other milestones can run separately if independent.

## Limits and rollout

Instruction following and semantic review remain fallible: a pass is not proof of
scientific correctness. The controller detects final control-file changes, but it is
not a tamper-proof security boundary against a malicious worker. A production setup
should keep controller/contracts and protected evaluation outside worker write access,
use a separate checkout per task, enforce path scope and protected tests externally,
and add CI/human policy enforcement. Presently allowed paths are reviewer-enforced,
not an OS-level allowlist. Ignored local data changes are outside the source digest.

No automatic next-milestone selection, scheduling, notifications, GUI, spend metering,
or live private-data experiment is included yet. Validate this pilot before adding them.
For later Knowledge goals, require actual generation/negative/abstention evaluations;
the runner's own unit tests alone are not a Knowledge quality gate.

## Mandatory documentation completion gate — 2026-11-05

Every effective contract receives reserved criterion `documentation_sync` from
`tools/development_loop.py`, regardless of task-supplied criteria. Worker and
reviewer must follow [the documentation rule](implementation.md).
Implementation records and related design status must be updated together;
missing/failed documentation review prevents completion. Documentation-only
or genuinely unaffected scope requires an evidence-based explanation. This is
an explicit review gate, not automatic proof of semantic consistency or a Git hook.
