# Reviewable delivery workflow design

**Status, 2026-11-05:** Planned W1 revision 2; owner approved branch/report delivery with PR optional and disabled by default. No new runtime, browser backend,
publisher or scheduler is implemented by this document. The contract and frozen
acceptance scenarios are in `contracts/dev-workflow/W1-reviewable-delivery.*`.

## Existing behavior and proposed boundary

`tools/development_loop.py` already runs bounded worker/check/reviewer cycles,
locks a target, injects documentation review and rejects overlapping controller/
target trees. It records external logs and detects some target/control changes.
Its budgets reset per invocation, control fingerprints enumerate specific files,
and `complete` means local checks/review rather than remote publication readiness.
`tools/evaluate_f1.py` checks F1 evidence after a parent supplies actual browser
results; it is project-specific and does not provide a general browser driver.

W1 extends these mechanisms without importing target source or moving orchestration
into CoRA. The worker edits task files; the read-only reviewer judges fixed
criteria; a controller-owned verifier records observations; a separate publisher
handles authorized Git/GitHub side effects. This is a process/ownership boundary,
not proof of OS isolation from hostile code. Trusted local checks remain trusted
code; unattended use does not grant extra filesystem or network permissions.

## Evidence identity

Capture run/project/contract IDs; target root, repository identity, base/head refs
and commits; tracked/nonignored content/modes; relevant configuration, dependency
locks, generated runtime and fixture hashes; controller and protected-evaluator
versions; check argv/cwd/environment; timestamps/deadlines/exit codes; raw artifacts.
Keep Git commit identity distinct from content/tree identity. A commit does not
by itself prove all nonignored working files were tested or reviewed.

Every check/browser/review/publication/remote-check observation references its
input manifest. Evidence is append-only by attempt; invalidation creates a new
observation, never rewrites the old attempt to pass. Define dependencies explicitly:
source/runtime/fixture changes rerun affected execution; doc changes require final
doc review; acceptance/control changes stop for decision. Reuse unchanged evidence
only with verified input equality and recorded rationale. Before publication,
confirm the reviewed content is exactly the candidate, with no hidden/unrelated
staged files. Before owner handoff, verify exact head and relevant target/merge
state match the successful remote checks. Target movement requires fresh integration
review/validation where affected, never a blind merge or force push.

Evidence files remain outside targets and are excluded from publication by default.
The publisher uses explicit reviewed task paths and retains unrelated original
checkout contents. Owner-facing reports and optional public PR descriptions contain concise validation summaries,
not private raw sources or full execution logs.

## Default delivery and owner handoff

`branch_report` is the default. PR support may be opted into explicitly; it is
not required to complete W1 and is not automatically activated on missing gates.
The report binds repository, source and target refs/SHAs, comparison link and
summary, local/browser/review/remote evidence, limits, unresolved findings and
proposed merge action. Report generation is durable and retryable. Updating it
creates a new version; it does not silently carry approval over to a new source
or target commit. The real pilot must demonstrate zero PR creation/update calls
in default mode, while preserving all independent-review and CI requirements.

## Proposed phase machine

Names below describe W1; existing state formats are not silently migrated.

| Phase / outcome | Required transition |
| --- | --- |
| `preflight` | Freeze inputs/authorization, prepare isolated baseline, probe required check/browser/GitHub capabilities and time allocation. |
| `implementing` | Worker follows fixed task and prior failure evidence; no contract changes or publication. |
| `checking` | Execute trusted task checks; deterministic failure returns to implementation within cumulative budget. |
| `browser_verifying` | Run project harness in actual supported browser and collect bound raw observations. |
| `reviewing` | Independent reviewer inspects actual diff, negative cases, records and docs. Rejection returns to implementation. |
| `locally_accepted` | All local required evidence and review correspond to the current candidate. This does not mean published or merge-ready. |
| `publishing` | Idempotent commit/push and version-bound report; confirm repo/base/head and side-effect receipts. |
| `remote_checking` | Observe required named gates on exact revision and integration state; failure returns logs to repair. |
| `ready_for_merge_approval` | Validated pushed branch, merge-decision report and successful current required push gates; actual merge requires owner authorization. |
| `decision_required` | Persist question/options/impact/recommendation and explicit authorization requirement. |
| `capability_blocked` | Required tool/environment unavailable after bounded recovery; include reproducible diagnostic and next action. |
| `budget_exhausted` | Preserve cumulative usage and all attempts; do not implicitly replenish on restart. |
| `publication_blocked` | Safe file scope/remote identity or credentials unavailable; retain local artifacts, no unsafe push. |
| `incomplete_published` | Safe reviewed task changes saved on a dedicated branch with version-bound report, failed/missing gates visibly retained. |

An incomplete publication is a separate receipt from its originating decision,
capability or budget outcome: preserve both, rather than overwriting the reason
with a generic published status. Existing historical `complete` states retain their
old meaning; report legacy local acceptance explicitly instead of certifying new
publication gates retroactively. No automatic transition performs a target merge.

## Browser capability and adapter

Use a project-independent adapter protocol with explicit command/capability and
result schema. The target owns its test harness/fixture; the controller starts it,
launches a real available supported browser and saves results with input identity.
Probe a small actual execution during preflight. Do not assume app-only computer
use tools are exposed to a standalone CLI. Choose the concrete local backend from
verified installed capabilities during implementation; record optional prerequisites.
A manually copied DOM result can support a disclosed manual run, but cannot pass
W1's unattended pilot. Node-only JS or screenshots do not count as actual-browser
execution. Browser availability failure blocks required route completion honestly.

## Publication, remote repair and recovery

Bind publisher authorization to project/repository, remote identity, dedicated
head and expected base. Read-only credentials/status probes precede worker time.
Implementation workers never publish. A final controller check verifies reviewed
paths and current manifest, then records commit, push and report receipts separately (plus PR receipt only in opted-in mode).
Inspect the remote after ambiguous network outcomes before retrying: the operation
may already have succeeded. Preserve branch identity and versioned report history across repairs; no duplicate commits,
force push, deletion or unrelated staging. Existing owner per-delivery publication
policy also applies to incomplete work, with truthful failed/missing gate status.
Safe publication itself must be established before publishing incomplete changes.

Default mode requires configured push gates, with their exact head/integration
identities. No pull-request event or PR identity is needed. Optional PR mode must
be explicitly selected for a project/task. If the repository enforces PR-only
gates, return an actionable configuration decision without silently bypassing
the gate or creating a PR. Define required gate names/events in preflight. Never treat absent,
pending, cancelled or unknown gates as passed. A missing test dependency is a
routine repair within scope; changing the test's expectations is a protected
criterion decision. Remote failures feed the same bounded repair/review chain;
new commits invalidate older remote success. Poll at bounded intervals and retain
last known state at timeout. A timeout cannot cancel the need for remote evidence.

Checkpoint durable cumulative cycle/time use before phases and side effects.
Include worker, verification, browser, review, publication and remote waits, plus
restarts. Monotonic deadlines enforce a running phase; persisted usage and wall
timestamps conservatively account for downtime. Specify crash handling/clock
anomalies rather than resetting the allowance. Terminate local child process
groups on timeout and reserve time for review/finalization. Monetary/token metering
is not provided; do not imply the wall-clock limit is a monetary spending cap.

## Bootstrap, pilot and completion

The current controller cannot target itself. Preserve that guard. Maintain this
implementation in an isolated dev-workflow development checkout while the owning
contract/evaluator manifest and evidence stay outside worker control; freeze these
inputs before implementation. Do not enable a project configuration until actual
bootstrap/capability preparation exists. Fixed hashes detect accidental/unauthorized
changes; path separation alone is not a secure protected-test service.

Run fault scenarios W01-W18 in synthetic repositories/local bare remotes, preserving
mock/real distinctions. Then execute the constrained CoRA state-type invariance
regression task from the W1 contract, including actual browser evidence, checks,
independent review, real GitHub branch push/remote validation and report generation, without manual
stage handoffs. The existing CoRA checkout and source behavior remain unchanged.
Independent review assesses this design, final implementation, actual negative
runs and documentation. Missing capabilities or manual completion yield partial
implementation, not a claim of fully automatic delivery.
