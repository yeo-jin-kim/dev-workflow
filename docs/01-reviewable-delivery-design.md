# Reviewable delivery workflow design

**Status, 2026-11-05:** W1 revision 2 implementation candidate exists in the separate development checkout. Actual Chrome adapter, durable evidence/state and branch publisher are implemented as a candidate. The real pilot exhausted three cumulative cycles and remains unaccepted; an additional authorized trial is required. PR creation and scheduler are not implemented or activated. The contract and frozen
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
| `reporting` | Atomically create/recover the deterministic versioned report; ready state is persisted only after report receipt succeeds. |
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


## Implementation candidate anchors — 2026-11-05

- `tools/delivery_evidence.py`: canonical content manifests, external raw command
  records, cumulative persisted deadline/cycles, actual Chrome headless execution
  of a loopback project harness, runtime/fixture/result/version bindings.
- `tools/delivery_loop.py`: explicit schema-version-2 opt-in runner, original
  self-target guard, preflight probes, worker/check/browser/read-only review,
  stale-evidence invalidation and safe incomplete-delivery handling.
- `tools/delivery_publish.py`: exact-path staging, crash-aware commit/push receipts,
  candidate-only base integration followed by revalidation, exact-head named push
  CI and append-only external JSON/Markdown merge-decision reports.
- `schemas/publication.schema.json`: independent incomplete-publication safety
  review, separate from failed semantic acceptance. Time exhaustion cannot grant
  extra review budget; if safe publication cannot be established it stays blocked.
- `projects/cora-w1-pilot.json`, `contracts/cora/W1-state-type-pilot.json`: narrow
  authorized real trial. Existing W1/F1 protected definitions remain unchanged.
- `tests/test_delivery_loop.py`: real temporary Git/bare-remote operations,
  explicit synthetic model/GitHub faults, and actual Chrome execution where
  available. Synthetic fixtures are not the real-pilot evidence.

Existing legacy CLI/tests are unchanged. Controller core remains Python 3.9+
standard library; adapters require installed Chrome, Codex CLI, gh and task test
Python dependencies. Chrome is an actual headless browser, with separate fresh
profile and loopback harness; no OS/browser sandbox weakening flags are used.
No app-only computer-use interface is assumed. PR mode is optional in the
contract but not implemented here; selecting it returns a decision request and
cannot silently activate PR creation. Automatic target merge stays absent.

Each run pins the complete controller manifest and owning protected files, so
controller edits require a new linked run rather than silently adopting new
policy. Reports/command/browser artifacts remain in the explicitly external
state directory. Final source/docs changes invalidate acceptance; report generation
itself is external and does not create a source-review feedback loop. Published
branches are incomplete until required push gates succeed and the exact base/head
are reconfirmed. Pending remote gates/clock anomalies exhaust or block the run
honestly, preserving all attempts and any safe incomplete publication receipt.

### Bootstrap corrections and linked validation

The first actual pilot produced an internally inconsistent reviewer output:
all criteria/verdict passed, but decision_requests contained a statement saying
there was no new decision. The controller correctly withheld completion, then
publication-safety review timed out; no pass was fabricated. An independent
format-only clarification returned the same semantic findings with an empty
decision list. Original stopped state/logs remain unchanged.

The implementation now treats contradictory pass/blocker/decision output as
invalid formatting and requests one independent clarification, preserving both
artifacts. It never retries a valid negative semantic judgment merely to obtain
pass, removes decisions itself, or treats generated text as owner authorization.
Malformed result types fail rather than throwing an unhandled acceptance error.
Browser harness hashes are compared before/after actual execution; mutation
invalidates results. Read-only remote probes have one durable infrastructure
retry; writes rely on side-effect identity inspection, not blind retry.

A separate explicitly linked bootstrap revalidation profile preserves the exact
pilot task contract and copies the original cumulative deadline/cycle usage.
Linking is allowed only from accepted runs, or a contradictory-pass stop with
independently corrected review bound to unchanged original reviewed contents.
Genuine unresolved decisions cannot be bypassed. Both prior state and resolution
are pinned; old states are not rewritten, budgets not replenished, and the new
isolated pilot still performs its own full worker/check/browser/review/publication
chain. `projects/cora-w1-pilot-v2.json` records this concrete linked validation;
its absolute evidence paths are host-specific, not a portable default.


### Source-review fixes and current verification boundary

A separate code reviewer requested stronger environment binding, retention of
pending CI at timeout and crash-idempotent reports. Command records now contain
the inherited environment fingerprint (no credential values), resolved executable
content identity and deterministic project dependency probes. Review/publication
compare the current environment/dependency binding. Browser failures carry exact
raw log, execution-record and project-observation paths back to the worker.
This corrects the missing diagnosis context found in the real trial.

CI saves its last known result on every poll. Report IDs derive from immutable
run/source/target/review/CI identity; orphan JSON/Markdown receipts are recovered
without duplicate versions. Reports include change goal, task summaries, all
verification references, cumulative budget and linked failure history. A failed
report cannot persist a ready status. Starting new implementation/review clears
previous acceptance; the publisher independently rejects a current negative
review even if an old digest survives. Parent-budget allocation also has an
exclusive sidecar receipt, preventing new state directories from multiplying the
same allowance; original histories stay untouched.

Latest local evaluation: 58 tests passed, including real Chrome and real temporary
Git/bare-remotes with explicitly synthetic model/GitHub fault responses. W02-W16
and W18 currently pass those mapped rehearsals; W01/W17 remain incomplete because
the actual CoRA task never reached accepted publication/push CI. A new directory
or fabricated pass cannot resolve that. No PR or target merge was performed.


Linked allowance claims use a fully written, atomically linked journal containing
initial state and source/controller/project/external-policy bindings. A crash
before child persistence can restore that exact run ID and budget; activation
occurs only after state persistence. Once active, missing/deleted state is not
a license to regenerate allowance. Distinct child directories cannot reuse the
same parent grant. Current acceptance remains incomplete at the exhausted live
trial; manual parent WIP preservation does not satisfy autonomous publication.

Both sides of child-state persistence use one original journal-binding function.
Controls are durable and guarded before activation, with a final binding recheck.
Tests cover unchanged recovery and changed-policy rejection after persistence.
Latest local verification is 58 passed; live W01/W17 remain incomplete.

Final independent re-review found the corrected source crash/binding paths
sound under the recorded tests. Overall W1 acceptance is still blocked by the
missing successful real pilot and explicit owner authorization for further trial.
