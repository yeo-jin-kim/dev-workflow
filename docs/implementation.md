# Controller separation implementation record

> Current W1 status: the bounded recovery pilot reached `ready_for_merge_approval` at CoRA `81b1e21`: actual worker, checks, Chrome, independent review, automatic commit/push, exact-head push CI and report all passed. The original 3600-second/five-cycle grant consumed two cycles. Frozen W1 evaluation passed 18/18 and independent milestone review passed all 12 criteria; no PR or merge.

> Historical status before the 60-minute trial: implementation candidate; the owner-authorized additional 30-minute/three-cycle trial also stopped incomplete. All three candidates passed 31 focused, 21 quality, 484 full tests and real Chrome/frozen F1 validation, but independent review rejected documentation provenance. Six actual cycles are preserved in total. W01/W17 remain incomplete; no PR or target merge. Earlier entries below are historical.

## 2026-11-05 — independent repository

Migrated the original local runner, schemas, automation tests and CoRA milestone
contracts from the CoRA working tree. No CoRA cognitive source code or runtime
package is copied or imported. CoRA's domain decision ledger remains in its own
`docs/implementation/decisions.json`; project-specific configuration references it.

The controller accepts an explicit `--project`, resolves target location from that
configuration, executes worker/check/review processes in the target, and uses its
own schemas/contracts/state outside the target. The configuration supplies the
project's documentation/decision paths to task context. Documentation review is
mandatory and cannot be overridden by a contract.

Added rejection of overlapping controller/target trees and state under the target;
added controller-version/target identity checks for resume and a target-level lock
across milestone directories. Fingerprints cover controller code, project/contract
configuration, schemas and controller guidance. Historical logs were moved to
ignored `.local/archive/cora/development-loop`; migration.json records SHA-256
checksums. Original absolute paths in old state are retained as historical data,
not active resume instructions.

## Validation

- Controller: `python3 -m unittest discover -s tests -q`: **15 passed**.
- Tests exercise external schemas and process target root, external run state,
  target/controller overlap rejection, documentation/completion gates, decision
  waiting, locks, contract changes and source-version invalidation.
- CoRA independently: **453 passed in 31.40 seconds**. Its prior 465 count included
  12 controller tests; those moved here and gained 3 separation cases.
- `status --project projects/cora.json`: Not started for the current F1 goal.
- Archive file contents were checked against migration SHA-256 hashes; `.local/`
  is excluded from Git. No new live Codex development run was started.
- Link/format validation and Git whitespace checks completed after documentation.

## Remaining limits

Path separation and workspace-write/read-only CLI modes do not prove hostile
process isolation. Trusted check commands still run with the user's permissions.
No external scheduler, notification loop, monetary budget, protected-test service
or OS security boundary is added. The independent repository was initially local-only. It is now connected to
GitHub; the later owner instruction requires parent commit/push each delivery,
without automatic merge/deployment. Historical notes are retained
under docs/original-runner-notes.md; README is the current operating guide.

## F1 contract preparation — 2026-11-05

Expanded contracts/cora/F1-distance-decay.json to revision 2 with baseline,
allowed/forbidden scope, candidate hop-distance/max-product decay, query relevance
requirements, numerical/stopping semantics, route parity, public synthetic
kernel/integration cases, decision boundaries and target documentation obligations.
Added a Korean task brief and external evaluator fixture; evaluator content is
embedded in the execution contract with a file hash for consistency. Labels are
agent-proposed, not user-certified empirical gold. The mandatory documentation
criterion remains controller-injected. No controller or CoRA runtime changed.
No isolated checkout/live run was provisioned; the current original target must
not be launched directly for this pilot before its execution preflight.

Validation: JSON/fixture hash, criterion IDs and references checked; controller
unit suite re-run and result recorded below. No CoRA feature tests were run
because this delivery only prepares the external contract and documents.

Contract-preparation validation result: **15 controller tests passed**. Contract/evaluator JSON, embedded fixture equality/hash, unique IDs, links and whitespace checks passed.

## F1 pilot started

User authorized F1 development. Prepared isolated sibling cora-f1 from all tracked/nonignored original CoRA working files; source content/mode digest matched before execution. Snapshot baseline and original source digest/status are retained in ignored preflight artifacts. No source private databases copied. Test Python and Node are available; explicit 3-cycle/1800-second pilot uses projects/cora-f1.json. Acceptance criteria/evaluation labels are unchanged.

## First F1 pilot outcome — 2026-11-05

The isolated worker produced an experimental implementation and stopped for a
browser surface it could not access. Parent supplied actual in-app browser kernel
execution and unrestricted loopback test execution, corrected two discovered
boundary defects with regression tests, and obtained independent read-only review.
Actual final full suite: 470 passed; browser/Python kernel comparison: 7 cases.
Independent review requested changes: unified fixture across all routes,
API/browser invalid-input coverage, explicit protected-evaluator execution, and
consistent current documentation. Parent reconciled status/history wording;
that final documentation update has not been independently re-reviewed.

F1 is NOT complete or merged. Original CoRA unchanged. Evidence and structured
outcome: ignored `.local/preflight/F1/final-status.json`; the initial controller
state and all failures remain historical, not rewritten to pass. Next iteration
must address review findings within a fresh bounded run. No owner conceptual
policy decision is currently pending; the remaining work is implementation and
verification. This pilot exposed the need for externally supplied browser/HTTP
evidence and phase-specific review time allocation before more unattended work.

## Per-delivery commit/push policy

Owner explicitly requested commit/push after every work delivery. Applied to
controller and target AGENTS.md and the F1 contract's parent-finalization policy.
Preserve incomplete review status on a dedicated target branch; do not merge,
force-push or include ignored private evidence. Automated workers remain unable
to redefine task criteria or publish themselves. This is an operating instruction
for the maintaining parent, not a new unattended Git executor in the loop.

## F1 second verification — 2026-11-05

`tools/evaluate_f1.py` checks the protected definition hash and all 13 case IDs,
actual browser DOM results, two shared graph queries at both recorded route seed
boundaries, false/missed activations and target source fingerprints. It imports
no CoRA packages. Target-owned `tests/f1_evaluation.py` exports synthetic domain
observations; the controller checks its artifacts. Evidence stays in ignored
`.local/preflight/F1-round2/`. This is executable synthetic case verification,
not an independent semantic oracle; the read-only review gate is separate.
Run the target exporter, serve its output locally, open it in an actual browser,
save `#results` as `browser-result.json`, then invoke
`python3 tools/evaluate_f1.py EVIDENCE --target TARGET`.
No protected case definition or acceptance threshold was changed.

Round-2 delivery result: CoRA 484 tests passed; controller 15 tests passed;
13 protected synthetic cases, four actual browser kernel comparisons and ten
browser invalid inputs passed. CoRA also rejects 13 tested invalid API inputs.
Independent read-only review initially requested three record corrections,
then passed all 12 acceptance/documentation criteria after rechecking the fixes
and recomputing the reviewed target digest. CoRA delivery: `6888c55` on
`codex/f1-distance-decay`. Final status notes record the review outcome only;
source/test fingerprints remain those evaluated. This remediation was directed
by the parent with separate CLI review; historical runner state was not rewritten
or presented as a fully autonomous browser-capable execution.


## F1 integration and W1 contract — 2026-11-05

F1 subsequently passed integration review and merged through CoRA PR #1 into
`codex/workflow-foundation` at `fe4aac5`. Integration candidate full suite: 484
passes; fresh browser comparisons: 4; invalid browser inputs: 10. A missing-pytest
CI prerequisite was repaired without weakening either quality gate; server quality
21/full484 tests passed. Earlier first-pilot incomplete statements above are
historical, not the latest F1 status. These steps included manual parent handoffs.

Defined W1 in `contracts/dev-workflow/W1-reviewable-delivery.{md,json}` and
`docs/01-reviewable-delivery-design.md`, with 18 fixed synthetic acceptance
scenarios, exact-version evidence, actual-browser adapter capability, bounded
repair/review, cumulative resume limits, publisher/CI recovery and owner handoff.
The real pilot is restricted to CoRA's actual state_type invariance regression
and affected documentation, with no runtime/semantic/evaluator changes. The
controller-as-target guard stays in place; bootstrap requires an isolated
implementation checkout and external owning protected inputs. W1 has no active
project configuration and is not yet implemented or running. The suggested
3-cycle/60-minute settings are specifications, not newly enforced CLI behavior.

This delivery changes contracts/design/current-status documentation only. No
controller or CoRA source, acceptance labels from F1, execution state or live
service changed. Contract JSON/hash/criterion/scenario correspondence, referenced
files and documentation links are checked; existing controller tests are run to
confirm compatibility. Implementation work and W1 live/failure-scenario execution
remain required before any W1 completion claim.

W1 contract preparation validation: **15 existing controller tests passed**;
11 unique task criteria plus the reserved injected documentation gate, 18 unique
scenario IDs with criterion coverage, embedded evaluator/hash equality, all
referenced files/Markdown links and whitespace checks passed. No W1 scenario or
live pilot was executed; these remain acceptance requirements for implementation.


## W1 revision 2: optional PR, branch/report default — 2026-11-05

Owner approved removing mandatory PRs for solo development. Updated W1 contract
revision 2, evaluator v2, design, README and project guidance. Final delivery is
now a validated pushed branch and version-bound merge-decision report; required
push CI, independent review, documentation gates and explicit owner target-merge
authorization remain. Reports identify repository, exact source/target refs/SHAs,
diff, all verification evidence/limits and proposed merge. Target movement still
invalidates affected integration evidence/approval. No PR API capability, URL or
pull_request event is required by default. Optional PR mode is explicit; PR-only
required repository gates cause a decision request rather than a bypass or an
unsolicited PR. The live pilot must demonstrate zero PR creation/update calls.

This owner-authorized contract change revises W01/W11/W13/W17/W18 delivery/recovery
expectations and associated criteria, retaining all 18 scenario IDs and all
other checks. The embedded evaluation and external file hash are synchronized;
v1 remains in Git history, with prior hash/decision recorded in revision 2.
Earlier W1 preparation notes above describe revision 1. This remains planning:
no controller/runtime behavior, active project or W1 live execution was changed.

Revision-2 validation: **15 existing controller tests passed**. Confirmed 11 task
criteria plus preserved injected documentation gate, 18 stable scenario IDs,
only the five owner-authorized scenario changes, embedded evaluator/file SHA-256
agreement, prior revision/hash history, default branch_report configuration,
reference links and whitespace. No runtime, project configuration, schemas,
existing tests or historical CoRA evaluation definitions changed. The 18 W1
scenarios and live pilot are still specifications, not executed results.


## W1 implementation candidate — 2026-11-05

User requested implementation of revision 2. Development is isolated in
`codex/w1-reviewable-delivery`, with owning contract/evaluator/legacy-test hashes
snapshotted externally before implementation. Existing runner/tests and W1/F1
acceptance definitions are preserved. New modules and optional pilot config are
mapped in docs/01-reviewable-delivery-design.md. No target merge or PR is authorized.

Implemented actual headless Chrome harness execution, immutable source/environment
records, independent review-driven repair, cumulative resume limits, exact-path
controller publication, push-CI failure feedback and versioned merge reports.
Incomplete semantic work requires a separate publication-safety review; it never
becomes accepted just because it was pushed. Missing capabilities, unresolved
decisions and exhausted budgets preserve actionable state. New state version 2
is opt-in; legacy complete states are not retroactively certified or migrated.

Validation is in progress: synthetic fault rehearsals use fake model/GitHub
responses explicitly, real temporary bare remotes and actual Chrome. The real
CoRA pilot will run actual model worker/reviewer, project checks, Chrome, GitHub
push/CI and report collection without parent stage handoffs. Neither code presence
nor synthetic fixtures alone establish W1 milestone completion. Results and final
independent review must be recorded below after actual execution.

Bootstrap fault/recovery verification: existing plus new tests initially reached
41 passes. The first live CoRA trial passed 31 focused / 21 quality / 484 full
checks and actual Chrome 4 comparisons / 10 invalid inputs / protected13 cases.
It then stopped on a contradictory pass/nonempty-decision reviewer response;
publication safety timed out, so nothing was relabeled accepted or forcibly
published. A separate independent clarification confirmed no owner choice was
needed. New bounded format clarification, before/after generated-harness binding,
read-only probe retries and linked cumulative-budget revalidation are tested.
The revised live trial uses a new isolated CoRA checkout/branch with the same
frozen task, carrying all original deadline/cycle use; original failure remains
under external w1-live-pilot evidence. Results below must distinguish both trials.


## Current W1 delivery: implementation candidate, real acceptance incomplete

The actual trials consumed the fixed three cumulative cycles. Trial 1 passed
checks/browser but produced a contradictory pass/no-decision review; the original
stop is preserved, with independent format clarification recorded separately.
Linked trial 2 retained the same original deadline/cycle usage and started from
a fresh CoRA baseline. Its worker renamed K01, breaking the protected exporter's
public function lookup. Regular 31/21/484 tests passed but protected validation
failed. The next worker received only a generic browser-failure message and did
not repair that compatibility error. The controller stopped at cycle3; it did
not discard the failure, relax labels, create PRs, merge or restart the budget.
Publication-safety review timed out, so no autonomous branch push was claimed.
The original CoRA checkout/target branch remain unchanged.

Fixed the controller diagnosis gap: browser failure feedback now provides exact
logs/records/project observations and explicitly asks workers to inspect them
before editing public test/helper names. Also addressed independent source-review
findings: effective environment/executable/dependency identities, current binding
checks, per-poll CI-state persistence, deterministic orphan-report recovery, and
ready-after-report ordering. Added negative-review acceptance invalidation and
single-allocation parent-budget receipts. No frozen W1/F1 acceptance definition,
legacy runner or original 15 tests changed. Code/design details are synchronized
in docs/01-reviewable-delivery-design.md.

Actual final local validation: **54 tests passed in 51.348 seconds** using
`python3 tools/evaluate_delivery.py --pilot-state .../w1-live-pilot-v2/state.json
--output .../w1-bootstrap/evaluation-reviewed.json`. All model/GitHub fault
fixtures are explicitly synthetic; temporary Git/bare-remote operations and
installed Chrome execution are real. The evaluator reports **INCOMPLETE**:
16 mapped scenarios pass, W01/W17 fail due missing successful real end-to-end
publication/CI. Source/input/environment evidence is preserved outside targets.
An independent follow-up review of the source fixes is required before delivery.

Remaining owner decision: authorize an additional bounded real trial after these
controller fixes. This is a budget expansion under the W1 contract, not permission
to weaken tests or merge anything. No further actual pilot has been launched.
Contract creation metadata is preserved historically; the implementation record
and design above describe current progress. The W1 milestone is not complete.


### Final source-review correction and delivery boundary

The follow-up reviewer found one further linked-allocation crash window. Fixed
it with an atomically exposed allocation journal containing the original initial
state, input bindings, run ID and inherited budget. State persistence precedes
activation; a crash recovers the same child rather than losing or replenishing
its allowance. Changed external protected inputs block recovery. Two new fault
cases verify crash recovery and refusal to adopt changed external policy.

Current exact-source local evaluation: **56 tests passed in 54.131 seconds**,
with `evaluation-final-source.json` reporting 16 mapped cases passed and W01/W17
still INCOMPLETE. No additional real trial was launched. Final source re-review
checks this last correction; actual end-to-end acceptance still requires an
explicit new trial budget, not a different state directory or renamed test label.

Per-delivery preservation: the parent inspected the stopped CoRA candidate's
four-file scope and saved/pushed it as explicitly incomplete WIP `efb5740` on
`codex/w1-state-type-pilot-v2`. Only stop-status documentation was added after
the failed trial; src/tests hashes match the actual failed exporter observations.
This was manual parent finalization, NOT autonomous publication, CI acceptance,
or W1 success. No PR or target merge occurred. All original failed states and
raw records remain unchanged; `manual-incomplete-publication.json` records the
separate receipt. A green ordinary CI cannot replace the failed protected gate.

Final journal-window verification: both pre-state and post-state/pre-activation
recovery now compare the same original bindings. Controls are persisted and
verified before activation, and bindings are checked again immediately before
activation. Injected crashes prove unchanged recovery preserves controls and
budget; changed external policy is rejected without activating the journal.

Latest exact-code evaluation: 58 tests passed in 58.669 seconds.
The external evaluation-durable-final.json remains INCOMPLETE: W01/W17 false,
16 mapped scenarios true. No further real CoRA trial ran. Only documentation
was updated after testing; implementation/test/contract inputs are unchanged.
Final narrow source re-review checks this fix; new trial budget is an owner decision.

Final independent narrow re-review confirmed the source-level allocation/policy
crash defects closed and documentation accurate. Its overall verdict remains
changes_requested solely because W01/W17 lack successful post-fix real execution
and the required additional trial budget is not yet authorized. Do not describe
this as full W1 acceptance or merge readiness. The next request is an explicit
bounded trial allowance, not permission to alter criteria or merge branches.


### Owner-authorized additional trial and documentation provenance correction

Owner explicitly approved an additional maximum 1800 seconds / three repair
cycles, keeping the same completion criteria and preserving previous failures.
`projects/cora-w1-approved-trial.json` records this new allowance, prior run paths,
and the exact K01 caller failure. It is not an automatic budget renewal.
Historical configurations above retain their exhausted allowances.

The actual run at `.local/w1-approved-trial/state.json` consumed three cycles
and stopped `budget_exhausted`. Every candidate passed focused 31, quality 21,
full 484 tests, diff check, real Chrome, and frozen F1 evaluation (13 protected
cases, four browser boundary comparisons, ten invalid inputs). The worker
restored the original public K01 name without weakening state_type/path checks.
Independent reviewers rejected documentation: first pending results, then references
to prior attempt digests. Thus no accepted candidate, autonomous publication,
exact-head push CI, or successful W01/W17 report was produced. Publication-safety
review timed out; the final incomplete report and all raw failures are preserved.
The prior three cycles plus the new three cycles remain visible, not reset.

This exposed a circular protocol: embedding a candidate digest/current results in
its own documents changes that candidate and prompts another review demanding
another document update. The controller now supplies stable run/attempt/report
locations and explicitly separates historical observations in target documentation
from final exact-candidate results in external evidence/report. Workers must not
claim prior digests certify current source; reviewers must still independently
validate current manifests/checks/browser evidence and reject misleading claims,
missing documentation, and semantic blockers. A clearly historical citation alone
must not cause another self-referential rewrite. The reserved documentation
criterion, protected contracts/evaluators, acceptance labels and legacy runner
remain unchanged. This is a prompt/provenance correction, not proof the AI will
always interpret it correctly. No fourth actual cycle is authorized or launched.

Regression evaluation and independent correction review are recorded externally;
current W1 remains incomplete until a separately authorized actual run passes.

Post-correction regression: **58 tests passed in 60.262 seconds**; frozen W1
evaluation remains INCOMPLETE (16 mapped scenarios pass, W01/W17 false).
`evaluation-approved-trial.json` binds tested source; only reporting documentation
is finalized afterward. The parent separately inspected and saved CoRA's four-file
candidate as **0d28c04**, explicitly incomplete WIP; this manual preservation does
not satisfy autonomous publication or current exact-candidate acceptance. The
external `manual-approved-trial-preservation.json` distinguishes that receipt.

Independent narrow correction review (`provenance-review.json`) passed all four
criteria: correction integrity, historical truth, explicit budget authorization,
and documentation synchronization, with no blockers/decisions. Its scope is the
source/provenance fix, not W1 acceptance; actual W01/W17 remain incomplete.


### Approved 60-minute/five-cycle trial: phase-timeout recovery

Owner authorized a new bounded maximum 3600 seconds / five cycles. The new
`cora-w1-approved-trial-60m` profile preserves all six prior cycles separately.
Its first candidate passed actual checks and Chrome, but the independent review
hit the old 240-second per-command cap without a final result. This was wrongly
classified as total budget exhaustion despite time and cycles remaining. The
publication-safety review also timed out; source was manually preserved unchanged
as incomplete WIP a037b1b. No semantic acceptance or target merge occurred.

Review now has a 600-second cap within the original cumulative deadline. A review
phase timeout yields missing-review feedback for another bounded repair cycle;
actual total expiry still stops. Narrow linked recovery of the historical timeout
requires no final review or owner decisions, protected timeout/input records,
unchanged source, and remaining original time/cycles. Existing exclusive durable
allocation journals prevent fan-out or renewed allowances. The recovery profile
copies the original deadline and consumed cycle; it never grants another hour or
five additional cycles. Genuine negative decisions and completed reviews cannot
use this missing-review recovery path. Four regression cases cover these
boundaries, cumulative linkage, fan-out rejection and total expiry.

Status during correction: first cycle incomplete; recovery source is independently
reviewed before resuming within the owner's original 3600-second/five-cycle grant.

Timeout-recovery regression: **62 tests passed in 62.248 seconds**. The frozen
W1 evaluator still reports 16 passing mapped scenarios and incomplete W01/W17;
a missing review is never a successful actual pilot.

The first narrow recovery review rejected path-only historical evidence checks.
Recovery now pins the exact parent-state and raw timeout/input SHA-256 values in
the independently reviewed recovery profile before allocation; changed or omitted
hashes reject recovery. The historical parent did not capture hashes at timeout,
so this is explicitly a maintaining-controller recovery attestation of inspected
original records, not a retrospective parent signature. The durable journal binds
that profile and original parent bytes; subsequent mutation is rejected. A fifth
regression case covers rewritten and unpinned raw evidence.

Pinned-evidence recovery re-review passed all five criteria with no blockers or
decisions; 63 regression tests passed. This authorizes no new allowance and makes
no live acceptance claim. Recovery resumes only under the original fixed deadline.


### Actual bounded recovery pilot reached the handoff gate

The recovery reused the original start/deadline (3600 seconds / max five cycles),
including the first timed-out review; it completed at cumulative cycle **2**.
The child started from manually preserved incomplete WIP a037b1b. Bootstrap
controller repair and WIP preservation preceded this final child; they are not
claimed as unattended work. Within the child, the controller performed actual
worker → focused 31 / quality 21 / full 484 / diff check → real Chrome/frozen F1
(13 protected, four boundary comparisons, ten invalid inputs) → independent
five-criterion pass → commit/push **81b1e217606ea78252b93d132660c1ca0102f4f0** →
exact-head push `Test/test` CI **42126115535** → immutable report →
`ready_for_merge_approval`, with no manual stage handoff or copied result.
Current full base-to-head scope remains the allowed test and affected docs;
the final child refined docs around the already preserved K01 implementation.

Report: `.local/w1-approved-trial-60m-recovery/reports/d52f50ed2f008ea47546c325de4dba9472e8831708191a548309f67d2e10559c.json`.
Its target is unchanged foundation **fe4aac5**, source is **81b1e21**, and
proposed merge is an owner decision. All historical failures remain unchanged.
No PR was created; neither CoRA target nor dev-workflow main was merged.
Final W1 scenario evaluation and independent milestone audit remain separate
from the CoRA task reviewer; their observed results are recorded below.

Final frozen W1 evaluator: **PASS, 18/18 scenarios, 63 tests passed in
57.855 seconds** (`evaluation-60m-final.json`). W01/W17 use the actual final
child, not synthetic model/GitHub fixtures. Independent final milestone review
is separate and remains pending until its final response is recorded. Only
reporting docs changed after evaluation; controller/tests/contracts are unchanged.


Final independent W1 milestone audit (`60m-milestone-review.json`) passed **all
12 criteria**, with zero blockers/decisions. It inspected the frozen contract,
actual source/diff, prior failures and repair records, final source/environment
bindings, browser, exact-head CI, immutable report, cumulative budget and explicit
bootstrap/manual boundaries. W1 revision 2 is implemented and verified within
this constrained pilot scope. General semantic reliability, complete UI coverage,
OS isolation and monetary measurement are not established. CoRA **81b1e21** and
controller implementation remain on dedicated branches awaiting owner merge
authorization; neither main nor CoRA foundation moved. No further live cycles
were used or allowance renewed after cycle two completed.


## W2 approved sequential queue

Current W2 status: implementation and final 94-test regression passed; independent
review outcomes are recorded chronologically below. Branch `codex/w2-approved-queue`, based on
verified W1 without merging either source/target branch. User authorized W2
implementation; live CoRA goal selection, new approvals, scheduling and merges
are not inferred from that instruction.

New `tools/approved_queue.py` records operator-supplied approvals of exact queue
and authority hashes, validates DAG/worktree/head boundaries, reserves persistent
queue/repository/task time/cycle budgets, and dispatches the existing W1 engine.
W1 publication, checks, browser, semantic/doc review and remote gates remain
unchanged. Completed receipts are checked against current source, report identity,
checks/browser/review/CI and remote head/base before delivered status. Dependencies
order verified deliveries and do not imply merged/integrated code.

Durable dispatch precedes engine execution; an interrupted parent reconciles a
complete receipt, while ambiguous/missing child evidence stops without replay.
Target locks and a queue-identity allocation lock block duplicate/fan-out runs;
deleted allocated state does not renew allowance. No refund of unused reservations
or automatic new window. Clock rollback/expired windows stop new dispatch.

The example is intentionally unconfigured, with no real owner approval receipt.
No W2 live Codex/GitHub/CoRA trial was launched. New fault tests use real temporary
Git/bare remotes and W1 engine, with clearly synthetic model/CI/browser responses;
existing W1 actual Chrome tests remain separate. Operator approval receipts are
a local trust convention, not identity authentication or OS isolation. A foreground
queue drain is implemented; scheduler installation, notifications, automatic goal
selection/contract generation, integration and money metering remain future work.

W2 final regression: **24 queue tests passed; all 87 controller tests passed in
68.607 seconds**, including original W1/legacy coverage and the existing actual
Chrome check. Additional queue cases cover CLI allocation/deleted state, concurrent
queue locks, changed reapproved inputs vs stale loaded tasks, damaged bindings,
remote probe failure and remote movement. Evidence is external (`w2-verification.json`,
`w2-regression-final.log`); independent source review remains separate. A successful
fixture is not a live AI/GitHub queue operation.


### W2 independent audit corrections

Initial independent review requested changes; the original verdict is preserved
in external `w2-review.json`. Corrections: reject unsafe state locations before
creating directories; never initialize from empty/partial started state; pin
initial run/binding/deadline in the exclusive CLI allocation; reject existing
state without that allocation. Preapproval attention is separate and grants no
budget. Approval also pins clean target HEAD/content/branch and remote base SHA.
Pending tasks recheck them while locked before dispatch.

Queue now holds ordered target locks through dispatch, dependency verification,
receipt checking and persistence, and revalidates all delivered jobs before final
handoff. Remote refs cannot be atomically locked: timestamps and explicit freshness
limits require revalidation at actual owner-authorized merge. No guarantee against
uncooperative external Git/filesystem writers or future remote changes is made.
Browser acceptance now verifies engine/version, generated-harness hashes, raw DOM
result, result hash, prepare/version/DOM/validator execution records and report
verification observations. Trusted-local-record consistency is not a signed
execution attestation or proof against filesystem adversaries.

Historical intermediate verification: thirty revised queue tests passed
(18.753 seconds). At that point a final additional deleted-
allocation case is included in the full rerun; final observed result and independent
re-review follow below. Previous 21/24 and 84/87 test results above are historical.


### W2 final observed regression and source-review boundary

Final source regression **94 tests passed in 91.071 seconds**, including all
**31 W2 cases**, 63 existing cases and the original 15 legacy tests. Observed
terminal lines are in `w2-release-tests.log` (Ran 94 / OK), not inferred from
partial test progress. The preceding `w2-final-regression.log` also terminated
with 94 passed in 77.037 seconds. These supersede earlier stage counts/pending
notes above. The final source adds strict object/version rejection for malformed
state; the existing corrupt-state test covers those cases.

The independent re-review accepted all seven source/behavior criteria after the
six corrections, but withheld documentation_sync/overall approval because it read
an earlier incomplete regression snapshot and the design header still named 87.
`w2-rereview.json` preserves that verdict. Current design/header now names the
observed final 94-test result; this final evidence/docs correction is independently
checked next. Source code/tests are unchanged after the final 94-test execution.
No live W2 model/GitHub/CoRA operation, scheduler installation or merge is claimed.


Final independent W2 review (`w2-final-review.json`) passed all **8 criteria**,
with no blockers or owner decisions. It accepted the seven corrected source/
behavior criteria and the fresh 94-test terminal result/documentation update.
Earlier negative reviews are preserved. Final validation is **31 W2 tests + 63
existing tests = 94 passed in 91.071 seconds**. Only reporting documentation was
finalized after that run; source/tests match `w2-final-observations.json` hashes.
W2 implementation is complete on its dedicated branch; an actual owner-approved
live queue and any scheduler/merge remain separate, unperformed operations.
