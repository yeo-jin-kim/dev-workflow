<!-- document-language: en -->
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


## English-first documentation with Korean translation

User requested all documents in English first with Korean translation below.
Converted all eight tracked Markdown documents, including full historical entries,
contracts and operating guidance. Existing English originals and Korean contract
originals remain verbatim in their respective language sections. Commands, paths,
identifiers, hashes, criteria and historical outcomes are preserved. JSON contracts,
schemas, frozen evaluations and immutable external run artifacts are unchanged.
AGENTS/README require synchronized complete translations for future documents.

Future generated merge-decision Markdown reports use bilingual fixed prose and
quote original task/diagnostic/policy machine fields in both sections, preserving
raw evidence without introducing model translation or new execution cost. The
canonical JSON report identity, publication/review gates, existing report files
and execution behavior are unchanged. A renderer regression verifies language
order, exact revision/evidence fields and preserved raw payloads. Documentation
structure, source preservation, links and controller regression are checked;
observed final validation is recorded below. No new target execution or merge.

The W1 phase context also conveys this owner-approved language policy to future
workers and independent reviewers, limited to allowed task documentation paths.

Bilingual verification: all eight documents preserve their original-language text;
heading structure, command blocks, links and numeric coverage passed. Final
controller regression: **95 tests passed in 117.796 seconds**, including the new
report renderer case. Machine-readable JSON files remain unchanged. Independent
translation/presentation review is recorded separately after its final response.

Independent bilingual review passed all five criteria with no blockers or owner
decisions: translation fidelity, full coverage, renderer integrity, future policy
and documentation synchronization (`bilingual-review.json`). Only this bilingual
result note was added after review/testing; runtime code is unchanged.

---


## Review JSON intake — 2026-11-06

Implemented `tools/review_intake.py`, disabled policy/project examples and a trusted
repair template. The adapter freezes original/selected evidence, binds exact
reviewed source/authority, generates one W2 task with existing W1 gates and a
trusted replay check, preserves duplicate/dispatch history and returns
`awaiting_human_retest`. Policy/model ambiguity and stale/missing inputs stop.
Existing W1 incomplete branch publication may still preserve WIP; it is not acceptance.
No scheduler, CoRA dependency, live policy or actual new CoRA repair was activated.
Actual supplied-review read-only preflight detected `911127c` vs `cc820de` and
refused dispatch. Tests use real Git/W2/W1 with synthetic AI/browser/CI/replay.
Final regression: **123 tests passed in 91.014 seconds**; the new intake/replay
subset passed **28 tests in 12.673 seconds**. Tests include the real W2/W1/Git
handoff with synthetic AI/browser/CI/replay observations. Initial independent
source review identified an authority-capture race and insufficient replay
evidence binding. Both were fixed: prepared inputs must agree with original
authority, dispatch rechecks that original authority, and the replay gate requires
a fresh observation bound to the actual question/settings, source, review,
snapshot and graph version. Regression tests cover both findings and do not
weaken existing gates. An early mock fixture missed production's __pycache__
ignore rule after importing the gate helper; it was corrected and the final
suite passed. Historical logs remain private under ignored .local/.
Final independent read-only review passed all five criteria with no blocking
findings or owner decision requests (review-intake-final-review.json). It inspected
actual source/tests/documents and the recorded tests; this is not a live CoRA
repair or general semantic proof. After review, only these final observations
were added; implementation/checks were unchanged. Commit/push publishes a branch
candidate; policy activation, owner retest and merge remain separate.
See [design and operations](03-review-json-intake.md) for scope and limits.

## Data quality trials — 2026-11-12

Implemented tools/quality_workflow.py and [data-quality workflow](data-quality-workflow.md). W1 unaccepted safety publication/push CI now precede semantic review; transport changes do not invalidate runtime evidence, while genuine runtime changes trigger bounded revalidation. Current tests and limits are recorded in the guide; no new live nested-agent success is claimed.

## Review request intake — 2026-11-15

An opt-in same-origin review-note intake is implemented in tools/quality_intake.py.
Serve an existing review with `--policy projects/.local/quality-intake.json`.
The policy must enable intake, reference contracts/cora/data-quality-removal.json,
declare its exact repair_mode in the trial command, and have no repair_project.
This first intake executes a fixed domain repair; arbitrary code editing from
browser notes is deliberately unsupported. Existing optional W1 CLI repair is
unchanged. See projects/cora-quality-intake.example.json (disabled by default).

GET /api/session provides an ephemeral token. POST /api/requests requires that
token, exact loopback Host and Origin, JSON content type and a bounded body. Only
schemaVersion=1 / changes_requested / matching planDigest / a nonempty reason are
accepted. Unknown command/path/budget fields confer no authority. Cross-site
requests are rejected; no permissive CORS is enabled. The service binds 127.0.0.1.
The token is not OS-user authentication and local processes are not isolated.

Before allocation the saved plan digest, selected node, graph audit binding,
snapshot hash, target manifest and policy/contract are checked. Execution checks
the graph again before any trial. A durable per-plan/policy/contract key prevents
repeated or edited notes from dispatching again. A single queue worker records
queued/running/final state and the original cumulative deadline (at most 3600s).
Interrupted running requests become decision_required on service restart; expired
queued work does not gain a fresh allowance. Pending requests resume only within
the preserved deadline. Multiple service instances are rejected by a service lock.

GET /api/requests/ID (token required) exposes progress and a result link; the page
polls it and retains the request ID across reload in sessionStorage. Result routes
serve only HTML, plan, checks and comparison; source DBs, quarantine archives and
logs are never exposed. HTML adds controls at request time without rewriting the
old archived review. Export notes remains a local file action. approve_proposal
cannot trigger execution or application. A failed comparison is shown as failure,
not acceptance. Notes and request histories remain private under .local/.

The owner-selected removal contract preserves every evidence reference, splits
confirmed threads, hides unavailable-source evidence and verifies rollback on
copies. Strict domain mode still blocks all missing sources. Original graph
installation, merge, scheduled monitoring, general/local-LLM semantic acceptance
and broad browser-to-code repair intake are deferred. Tests exercise real HTTP
CSRF/rebinding/token/content guards, stale graph/snapshot/plan rejection, durable
deduplication, fixed-policy dispatch, no deadline reset, restart handling and file
allowlists; domain tests cover deletion/quarantine/evidence/rollback and owner conflicts.


## Recall-centered repair review — 2026-11-15

Request controls moved out of the data-quality diagnostic page into CoRA's
existing Real-data Recall review. The generic optional CoRA loopback relay forwards
JSON to this controller without importing it. The controller still enforces token,
Host/Origin, fixed policy, deadline and duplicate rules. Intake now accepts a bounded
reviewRecord with matching snapshot/graph sequence and stores its actual question,
answer, options, issue labels and reason privately. Explicit mixed_node scope uses
the removal contract; recall_answer feedback is durably recorded for scope review
with no worker execution. Duplicate mixed-node requests attach fresh review context
without restarting the old repair or resetting its deadline.

Session/status responses provide the plan digest and latest request ID. Pending
scope feedback has a readable receipt, while actual trial results have their own
links. Exports remain usable offline. Bare legacy notes remain supported by the
API but the diagnostic page no longer injects request controls. Body limit is
256 KiB; oversized records must use private export rather than silent truncation.
Serve with `--review-url http://127.0.0.1:8773/` for a return link. The optional
presentation cache `.local/quality-views/HASH` uses SHA-256 of the JSON-encoded
absolute trial directory, with matching view-binding.json plan digest. It shows
new read-only CoRA explanations without replacing immutable archived HTML/JSON.

For new configured domain comparisons add `--review-request {run}/repair-request.json`
to the trusted compare argv. This adds the submitted question as human review data,
not an acceptance oracle; it cannot change fixed checks or request LLM generation.
Historical requests that predate question capture explicitly have no original-query
replay. None of these changes enables generic code editing, identity-conflict
resolution, production application or merge. Live user judgments remain necessary.



## Review transport correction — 2026-11-15

Real Recall traces can exceed the previous 256 KiB intake limit. Both optional relay and external intake now accept bounded JSON requests up to 8 MiB, preserving the complete review record. Relay failures return JSON; the UI reports non-JSON service responses without discarding the current judgment. Scope, authorization and original-graph restrictions are unchanged. Regression checks cover a 300 KB synthetic review and JSON relay rejection; these do not establish model answer accuracy.


## Answer/retrieval development contract — 2026-11-15

Added `contracts/cora/recall-answer-repair.json` with its bilingual guide and disabled `projects/cora-recall-answer-{repair,intake}.example.json` configuration templates. It uses the existing private review intake and W2/W1 code-development pipeline, distinct from fixed graph removal. Criteria require exact-baseline reproduction, justified expected behavior, synthetic baseline failure/candidate pass, negative neighbors, original-case before/after replay, independent review, documentation, human retest and exact-head CI. The Me omission report does not itself establish that Me belongs in the answer.

`execution_limits` freeze 3600 seconds/five cycles; both review-policy loading and direct W1 initialization reject excess before new state. Historical contracts without these fields retain prior behavior. Replay binding now includes conversation metadata. This delivery adds a contract and executable guard behavior, not a live CoRA repair: web answer reports still stage for scope review, disabled examples do not dispatch, and a concrete pinned real-data replay adapter remains required. Existing requests, mixed-node policy, prior budgets and original graphs are untouched. See `contracts/cora/recall-answer-repair.md`.


Validation for this delivery: 146 controller tests passed in 117.236 seconds. Focused tests cover capped intake, direct W1 rejection before state creation, malformed limits and conversation-loss rejection. Contract paths/criteria and English/Korean sections were inspected; whitespace checks passed. No actual coding worker, local LLM, browser or remote CoRA CI run was started for this contract delivery.


## Web answer-development dispatch — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json` optionally enables answer/retrieval dispatch alongside the unchanged fixed mixed-node policy. The additional policy must pass `review_intake.policy_inputs` and name `cora-recall-answer-repair-v1`. It is pinned separately, so enabling the route does not alter the old removal policy hash, authorize old staged reports or renew their budgets. New completed, clean/version-bound reports are dispatched through `answer_dispatch.py` to the existing W2/W1 engine in an operator-provisioned isolated checkout. The web caller cannot choose commands, paths or budget. Duplicate case identity ignores export/transport/response IDs and preserves the original deadline even after another export; changed authority requires a decision.

The dispatcher first invokes a trusted replay through `review_replay_gate.py`, pins that private baseline observation into the task, then prepares/runs the frozen development contract. `cora_review_replay.py` launches CoRA's native copy-only replay command from the target checkout, wraps source/review bindings and imports no target package. The outer execution deadline includes preflight/replay and terminates the process group on timeout; internal W1 cycles remain capped at five. Interrupted jobs are not automatically restarted. Stable graph content is checked when exported. Missing history or verified local-model identity blocks rather than changing settings or claiming correction.

Status and the private feedback page show development state. Only a successfully reviewed W1 candidate with a bound replay for its accepted digest exposes an after-answer; the original reviewed answer and reason remain visible. Human retest, semantic ambiguity, merge and production installation remain separate decisions. The browser retains review state; refreshing does not turn an old record into current authorization. A replay observation alone is not semantic acceptance. Current integration tests use synthetic worker/browser/CI fixtures; a real-data native replay probe is separate from an actual autonomous repair. No actual coding worker or original graph modification was started in this integration delivery.


Final integration validation (2026-11-18): 149 controller tests passed in 124.938 seconds; the earlier run (136.511 seconds) is archived. CoRA passed 533 tests and exact-head CI at 1dd7608. HTTP dispatch/W2/W1/after-answer fixtures use synthetic workers and CI; native copy-only replay used real data. No actual coding worker or answer correction is claimed. Changed graph versions require a fresh shared-intake review binding.


## Stale-answer revalidation and bounded continuation — 2026-11-19

Answer policy may explicitly enable `allow_stale_revalidation` with a pinned `revalidation_binding` plan under ignored `.local/`. The plan fingerprint joins policy authority. The original review is retained; trusted native replay must match its snapshot, sequence and the plan's semantic graph digest. It emits a separate current context/response, which inherits the reported issue but is not a new human judgment. Current source is checked before W1 preparation. LLM-enabled requests remain LLM-enabled with explicit provider/model settings; absent historical identity is disclosed, not invented. Model identity is configuration/file metadata, not full weight attestation. The worker must establish whether the issue persists before changing code.

`tools/continue_answer_request.py --review REVIEW_FOLDER --policy QUALITY_POLICY --answer-policy ANSWER_POLICY --request REQUEST_ID --authorization OWNER_REFERENCE` explicitly continues only a stopped preflight with no W1 preparation/dispatch. It preserves the old failure and links a child request, subtracts previous execution time from the original 3600-second allowance, and reuses the same child on repeats. Already dispatched work requires its existing cumulative state; this command cannot reset it. The separate five-cycle ceiling remains unchanged. No automatic renewal or production merge is authorized. The web status/receipt follows the linked continuation and displays current replay and actual worker phases.

Validation includes stale-source refresh through synthetic W2/W1, immutable original review, trusted binding, and continuation allowance/idempotency/refusal after dispatch. Final full controller suite: 151 passed in 139.071 seconds; live worker outcomes are reported separately. Synthetic worker fixtures do not prove a real answer correction.


## Publication-audit sequencing clarification — 2026-11-19

A live answer-repair trial reproduced the original omission and produced a candidate whose real-data answer includes the evidenced owner. The candidate passed 537 controller-run tests, copy-only replay and the browser harness, but was not semantically accepted or published. Publication safety first identified newly added private absolute evidence links; those were redacted without changing original evidence. A second audit confused uncommitted WIP publication with semantic acceptance/merge authorization. The candidate and both rejection records remain private; no allowance was renewed. One operator documentation correction used the same W1 state and counted as the second cycle. This trial is not a fully autonomous successful repair.

The publication-audit prompt now explicitly describes its position before commit/CI and the existing trusted authorization to publish an UNACCEPTED dedicated branch. Pending CI, independent semantic review, human retest and withheld merge do not themselves indicate unsafe publication. Actual privacy/scope findings still block, and a passing safety audit still grants no semantic acceptance. This clarification has not yet been validated by another live reviewer. Focused delivery tests: 48 passed in 68.517 seconds. These mechanical tests do not prove model adherence.

## Development review handoff — 2026-11-26

The external controller now provides `tools/handoff_server.py`, a loopback console
for queued request progress and revision-bound before/after comparisons. It shows
the captured question, correction reason, original/candidate answers, returned
graph subsets, claims, paths and evidence. Graph layouts are presentation only;
missing candidate evidence is displayed explicitly. Existing queue/runner state
is polled every three seconds without dispatching or replenishing its allowance.

Successful answer dispatch automatically registers a private immutable handoff
from the verified publication report and matching replay. The report must pass
independent review and exact-head/base CI; replay request, source digest, snapshot
and available graph-content identity must match. Changed artifacts invalidate the
handoff. Browser retest notes are version-bound and append-only, with a latest-note
projection. They are local unauthenticated notes, not merge authority.

`tools/delivery_handoff.py merge` is an explicit operator action, requiring a
passing retest, an owner authorization reference and trusted check argv arrays.
It requires a clean target checkout, matching repository and exact local/remote
base and remote candidate. It merges the recorded commit, checks tree equality,
runs post-merge checks (600 seconds each, 3600 seconds overall), checks for dirty
or moved revisions, then uses an ordinary non-force push. A failed or interrupted
merge attempt remains recorded and cannot silently restart. Failed checks preserve
the local merge for inspection and do not push; recovery is an operator decision.
The web server exposes no merge, command execution or worker restart endpoint.

An owner may preserve explicit required/forbidden claim IDs after a passing retest.
Cases and data bindings remain private. Future matching candidate replay is checked
against these assertions before handoff; different requests/snapshots are explicitly
not applicable. The standalone regression command executes a trusted replay in a
fresh external folder and verifies source/request/data identity and assertions.
Cases are not an automatically generated gold answer or general accuracy proof.
Read-only `inspect` records Git ancestry for work already merged outside this helper;
it does not invent a new approval or rewrite the historical delivery report.

```sh
python3 tools/handoff_server.py --port 8780
python3 tools/delivery_handoff.py register --report REPORT.json --review REVIEW.json --observation REPLAY.json
python3 tools/delivery_handoff.py inspect --packet PACKET.json --target TARGET_CHECKOUT
python3 tools/delivery_handoff.py retest --packet PACKET.json --decision pass --reason 'What was tested'
python3 tools/delivery_handoff.py preserve --packet PACKET.json --required claim:STATE_ID
python3 tools/delivery_handoff.py merge --packet PACKET.json --target TARGET_CHECKOUT --approval projects/.local/merge-approvals/PACKET_ID.json
python3 tools/delivery_handoff.py regression --case CASE.json --target TARGET_CHECKOUT --command TRUSTED_REPLAY_ARGV.json --expected-head CURRENT_FULL_SHA --output .local/NEW_REGRESSION
```

All packet/report/review/replay paths must remain under controller `.local/`.
The checks file contains JSON arrays of argv arrays; the replay file contains one
argv array with `{output}` for fresh artifacts and must write `review-replay.json`.
No shell command text is accepted from browser notes. Source/review/CI checks still
belong to the existing bounded runner. This adds neither a background scheduler,
monetary metering nor arbitrary next-goal selection. No CoRA code or original data
is changed by this delivery. Private evidence is accessible to the local user;
this is loopback/session protection, not multi-user authentication or OS isolation.
The console covers answer-repair handoffs; domain graph repair retains its existing
copy-only results and separate apply policy. Preserve that boundary.

### Trust and validation details

Registration reuses the replay gate's complete observation validator, including
the exact selected-record bytes, response query/settings, trace and graph version.
It also checks the immutable report identity against controller state, raw
source-bound check/review receipts and the pinned project/contract criteria and CI
gates, including browser evidence when configured. The same proof files are pinned
in the handoff. A freely constructed success-shaped JSON is insufficient.

The operator first records an actual owner decision with `authorize`; this writes
an immutable, revision/target/check-bound approval under trusted `projects/.local/`.
`merge` consumes that file, not arbitrary authorization prose, and rechecks the
controller and protected task inputs before changing the target. It is operator
attestation, not authentication of the human: review text and web notes cannot
create it, and operators must not invent owner approval. Git calls have a 60-second
timeout; post-merge checks retain their per-check and cumulative limits.

```sh
python3 tools/delivery_handoff.py authorize --packet PACKET.json --target TARGET_CHECKOUT --reference 'Actual owner decision reference' --checks TRUSTED_CHECKS.json
python3 tools/delivery_handoff.py merge --packet PACKET.json --target TARGET_CHECKOUT --approval projects/.local/merge-approvals/PACKET_ID.json
```

Regression cases intentionally run on future revisions rather than requiring the
origin commit forever. Their origin SHA/digest is preserved, while each fresh run
requires `--expected-head CURRENT_FULL_SHA`, a clean checkout, unchanged source,
exact review bytes and a traced replay. Trusted replay argv must include both
`{review}` and `{output}`. Current-source identity is checked against the fresh
observation, not substituted with the old case's source identity.

Optional `handoff_console_url` in the trusted quality intake policy supplies the
loopback console origin. The existing feedback page links to it; its relative
result URL remains compatible with the CoRA relay. The disabled example includes
this option. This delivery does not renew old execution grants or replace their
policies. Start an explicitly configured intake for a new authorized scope.

`register --historical-only` imports a past comparison without granting retest,
regression-case acceptance or merge authority. It records any raw-proof failure
and remains read-only even when Git shows the source was merged. The live EMNLP
comparison uses this mode: its historical browser harness no longer matches the
recorded file inventory. No historical report/evidence or acceptance was rewritten.

### Delivery validation — 2026-11-26

Implemented candidate. Final local suite: **165 tests passed in 129.383 seconds**;
13 focused handoff tests cover real disposable Git merges/pushes, failed-check
push prevention, changed revisions/approvals, replay faults and HTTP boundaries.
Live CUA checks rendered the actual captured EMNLP comparison; a separately labeled
synthetic browser fixture verified saving a test, selecting/preserving a regression
assertion and restoring it after reload. This is not a new real-data repair run.
Independent re-review confirmed the initial binding/authority findings fixed;
the final focused review passed after rejecting symlinked replay evidence.
The added push CI workflow repeats the suite on the published revision.
No CoRA implementation, original graph or prior execution grant was changed.

Remote CI uses Ubuntu 22.04 for Python 3.9. The initial Ubuntu 26.04 image
could not install Python 3.9 and never ran tests; its failed run is preserved.
Only the runner image was pinned; the complete test command remains unchanged.

## Automatic quality improvement implementation — 2026-11-26

Implemented experimental controller components: `quality_improvement.py` (durable
phase/cycle/deadline state and gates), `quality_agent_stage.py` (installed agent
roles with controller-owned schemas) and `quality_topic_evaluate.py` (native CoRA
subprocess evaluation, no target imports). Added a scope-only topic repair contract,
disabled private-configuration examples, frozen case registries, ordinary review
feedback iteration, protected-input and exact-source checks, regression/deferral
blocking, cumulative limits, stale-candidate invalidation, observed model/provider binding and terminal deduplication.
No CoRA implementation, original data or active review pool was modified.

Actual captured evaluation intake: 30 sources, 17 sources with grounded-text-related
errors, preserved in ignored private analysis. `root_cause_proven=false` and
`semantic_quality_accepted=false` remain explicit. No live model worker, independent
agent review, real before/after quality acceptance, installed listener, publication
of a worker candidate or automatic merge was executed. Templates are not renewed
execution authorization. Stronger semantic labels, source context and local model
capabilities must be supplied through protected configuration. The protocol cannot
prove an agent's causal reasoning merely from JSON and does not replace human retest.

The implementation was source-reviewed for input ownership, source/version binding,
expected-label/coverage preservation, process-group deadlines, repeat-run limits and
read-only stages. Independent live review remains pending; this is an experimental
branch delivery. Final deterministic validation is recorded below. See
`quality-improvement-protocol.md` for full state transitions and operating limits.

### Protocol delivery validation

Initial protocol controller suite: **181 tests passed in 143.007 seconds**. Focused new
protocol/adapter suite: **16 tests passed in 13.915 seconds**. The focused cases
include a complete synthetic repair-to-retest run, automatic review-feedback retry,
coverage/expectation tampering, semantic decisions, out-of-scope writes, reviewer
writes, regressions, failure-to-deferral hiding, timeout/cycle accounting, no budget
renewal, interrupted-step refusal, stale candidate invalidation, observed model change,
case/source binding and agent sandbox role construction. Earlier full suites of
179/180 tests also passed but are historical intermediate versions. No acceptance
labels were changed to obtain these results. JSON schemas/configuration and bilingual
source documentation were inspected; `git diff --check` passed. Push CI is a separate
mechanical gate and does not replace independent live semantic review.


### Evidence-integrity follow-up

Final source adds complete per-stage file manifests and rechecks them before later
phases and human retest. Changed inputs, logs, raw evaluator/agent outputs, missing
files, added files or symlinks invalidate the candidate. This closes a source-review
finding: recorded result hashes alone were not previously rechecked. Focused suite
**17 passed in 16.596 seconds**; final full suite **182 passed in 144.462 seconds**.
The added regression changes a prior baseline log after readiness and verifies that
the same episode becomes decision_required, with no budget renewal. Initial pushed
revision e699734 passed remote CI; the follow-up has its own exact-head push CI.
Independent live semantic review and actual model repair remain unverified.


### Live experiment timeout configuration — 2026-11-26

Per-step limits may be configured up to 3600 seconds. Each command is still capped by the remaining cumulative episode deadline; this does not renew time or repair cycles. This permits pinned 30-source evaluations to complete within the owner-approved 60-minute experiment.


### Unattended topic experiment — 2026-11-26

A live owner-authorized experiment ran on an isolated CoRA worktree at `fc832b79a15c3149e23ae2bae7cd1280079848aa`, with a cumulative 60-minute / 5-cycle limit. The frozen 8 gold cases and 30 real sources produced 20 passes and 18 failures. Real-source errors were 8 activity-name citation failures, 7 source-grounding failures and 2 identity citation failures. Real-source runtime passes do not establish semantic accuracy.

The installed agent completed a separate read-only diagnosis and requested an owner decision about customer-work canonical names: both the longer source expression and the protected shorter expected name are source-backed, while the design lacks a shared-core naming rule. The episode stopped at `decision_required` before repair, candidate reevaluation or independent candidate review. One diagnostic cycle was consumed; no repair was applied. The original deadline and complete private evidence remain preserved. No target commit, merge, active-pool replacement or original graph modification occurred. An answer to the policy question is not itself a budget renewal.

Validation: controller focused suite 18 passed (16.366s), full suite 183 passed (162.208s); unchanged CoRA baseline 587 passed (20.35s). Timeout-support revision `4d02081ae892a7cd1df8e670c6bb6fdca7c844ba` passed push CI. Private run evidence is stored under ignored `.local/quality-improvement/topic-unattended-20261126/`. This is a reproduced-failure/decision result, not a completed repair or quality acceptance.


### Owner-approved semantic topic evaluation — 2026-11-27

The native CoRA evaluator now reports `semanticVersion: 1` and source-grounded `semanticStatus` (`pass`, `fail`, `needs_review`). The controller uses this verdict rather than diagnostic `exactMatch`; ambiguity maps to `deferred` and cannot satisfy complete acceptance. Semantic fixtures refuse fallback to the old exact-match grade. Evaluation-model completion identities are included in the observed model binding, and the example policy protects the new native semantic evaluator alongside the fixtures and evaluation command.

This is an explicitly owner-approved evaluation-policy revision, not a worker changing labels to pass. The original failed episode, source text and diagnostic expected names remain unchanged. New semantic target descriptors define referent/activity/scope and protected explicit identifiers. A new episode requires fresh frozen expectations; the old terminal state and consumed budget are not reset. The same local model in a separate call is not independent human semantic proof. No automatic merging, graph approval or correction of the previous 17 real-source failures is claimed.


Validation: controller full suite **184 tests passed**; focused quality/adapter suite **19 passed in 17.307s** after the final model-identity binding update. Native CoRA `5540e8f` passed 596 regression tests and all 8 live synthetic semantic cases; the exact-name customer-work diagnostic remained false while the semantic verdict passed. No new unattended 30-source repair episode was run.


### Real-source repair retry outcome — 2026-11-27

A new owner-authorized 60-minute/5-cycle episode froze the semantic fixtures and the same 30 original sources; baseline was 21 pass/17 fail with all 8 synthetic cases passing. The read-only agent stopped with decision requests, treating missing real semantic gold as a blocker to even source-format repair; its pytest attempt also failed because its read-only environment could not create temporary files. Parent supervision selected the already-authorized bounded prompt-format class without changing protected expectations/validators. This intervention does not count as successful unattended operation. Original episode and authority were retained.

Two supervised candidate cycles used the original deadline (three cycles including diagnosis). The first introduced a hobby regression from missing identity `reason`; its evaluation was stopped. The next explicitly specified mandatory fields and passed 602 CoRA regression tests, but its live evaluation completed only four synthetic cases before the cumulative deadline: project failed on an empty identity response, the other three passed. The supervised continuation is `budget_exhausted`. No final same-source candidate comparison, independent candidate review, semantic acceptance or merge occurred; the 17 source failures are not verified fixed. Partial/failed evidence remains under ignored `.local/quality-improvement/topic-runtime-retrial-20261127/`. CoRA experimental candidate `171ab3a` is unaccepted. An additional 30 minutes was requested, not granted at stop; neither deadline nor cycles were reset.

<!-- document-language: ko -->
# 한국어 번역

# 컨트롤러 분리 구현 기록

> 현재 W1 상태: 제한된 복구 파일럿은 CoRA `81b1e21`에서 `ready_for_merge_approval`에 도달했다.
> 실제 작업자·검사·Chrome·독립 검토·자동 commit/push·정확한 HEAD의 push CI·보고서가 모두 통과했다.
> 원래 3600초/5회 한도에서 누적 2회를 사용했다. 고정 W1 평가 18/18과 독립 마일스톤 검토 기준
> 12개를 모두 통과했으며 PR이나 병합은 없다.

> 60분 시험 전의 과거 상태: 구현 후보였다. 사용자 승인 30분/3회 추가 시험도 미완료로 끝났다.
> 후보 3개 모두 집중 31개·품질 21개·전체 484개 검사와 실제 Chrome/고정 F1 검증은 통과했지만
> 독립 검토가 문서 출처를 거부했다. 실제 누적 6회를 보존했다. 당시 W01/W17은 미완료였고
> PR/대상 병합은 없었다. 아래의 이전 기록은 역사 기록이다.

## 2026-11-05 — 독립 저장소

원래의 로컬 실행기·스키마·자동화 검사·CoRA 마일스톤 계약을 CoRA 작업 트리에서 이전했다.
CoRA 인지 소스나 런타임 패키지는 복사하거나 가져오지 않는다.
도메인 결정 원장은 CoRA의 `docs/implementation/decisions.json`에 남기고 프로젝트 설정이
이를 참조한다.

컨트롤러는 명시적 `--project`를 받아 설정으로 대상 위치를 찾고, 대상에서 작업자/검사/검토
프로세스를 실행하며 자체 스키마/계약/상태는 대상 밖에서 사용한다. 설정은 프로젝트의 문서/
결정 경로를 작업 맥락에 제공한다. 문서 검토는 필수이며 계약으로 덮어쓸 수 없다.

컨트롤러/대상 트리 중첩과 대상 아래 상태를 거부하는 기능, 재개 시 컨트롤러 버전/대상 식별
확인, 마일스톤 디렉터리 사이의 대상 잠금을 추가했다. 지문에는 컨트롤러 코드·프로젝트/계약
설정·스키마·운영 지침을 포함한다. 과거 로그는 Git 제외 경로
`.local/archive/cora/development-loop`로 옮기고 migration.json에 SHA-256을 기록했다.
옛 상태의 절대 경로는 실행 재개 지시가 아닌 역사 데이터로 유지한다.

## 검증

- 컨트롤러: `python3 -m unittest discover -s tests -q` — **15개 통과**.
- 검사는 외부 스키마·프로세스 대상 루트·외부 실행 상태·대상/컨트롤러 중첩 거부·문서/완료 게이트·결정 대기·잠금·계약 변경·소스 버전 무효화를 확인한다.
- CoRA 별도 검사: **453개, 31.40초에 통과**. 과거 465개에는 컨트롤러 검사 12개가 포함됐으며 여기로 옮기고 분리 사례 3개를 추가했다.
- `status --project projects/cora.json`: 현재 F1 목표는 시작 전이다.
- 아카이브 내용과 이전 SHA-256을 확인했다. `.local/`은 Git에서 제외하며 새 실제 Codex 개발 실행은 시작하지 않았다.
- 문서 갱신 후 링크/형식과 Git 공백 검사를 마쳤다.

## 남은 한계

경로 분리와 workspace-write/read-only CLI 모드는 적대적 프로세스 격리를 입증하지 않는다.
신뢰된 검사 명령은 여전히 사용자 권한으로 실행한다. 외부 스케줄러·알림 루프·금액 예산·
보호 검사 서비스·OS 보안 경계를 추가하지 않았다. 독립 저장소는 처음에는 로컬 전용이었지만
이후 GitHub에 연결됐다. 후속 사용자 지시는 부모가 결과마다 commit/push하도록 요구하며
자동 병합/배포는 허용하지 않는다. 과거 기록은 docs/original-runner-notes.md에 보존하고
현재 운영은 README를 따른다.

## F1 계약 준비 — 2026-11-05

contracts/cora/F1-distance-decay.json을 revision 2로 확장했다. 기준 버전·허용/금지 범위·
hop 거리/최대곱 감쇠 후보·질의 관련성 요건·수치/종료 의미·경로 일치·공개 합성 커널/통합
사례·결정 경계·대상 문서 의무를 넣었다. 한국어 작업 요약과 외부 평가 fixture를 추가했으며
평가 내용을 실행 계약에 포함하고 파일 해시로 정합성을 확인한다. 라벨은 에이전트 제안이며
사용자가 확정한 실증 정답이 아니다. 필수 문서 기준은 컨트롤러가 주입한다.
컨트롤러나 CoRA 런타임은 변경하지 않았다. 분리 체크아웃/실제 실행을 준비하지 않았으며
현재 원래 대상을 사전 점검 없이 이 파일럿으로 직접 실행하면 안 된다.

검증: JSON/fixture 해시·기준 ID·참조를 확인하고 컨트롤러 단위 검사를 다시 실행해 아래에
기록했다. 외부 계약과 문서만 준비하는 결과이므로 CoRA 기능 검사는 실행하지 않았다.

계약 준비 검증 결과: **컨트롤러 검사 15개 통과**. 계약/평가 JSON·포함 fixture 내용과 해시·
고유 ID·링크·공백 검사를 통과했다.

## F1 파일럿 시작

사용자가 F1 개발을 승인했다. 원래 CoRA의 추적/무시되지 않은 작업 파일을 모두 보존해
분리된 형제 디렉터리 cora-f1을 준비했고 실행 전 소스 내용/모드 digest가 일치했다.
스냅샷 기준과 원래 소스 digest/상태는 Git 제외 사전 점검 증거에 유지했다.
원본 비공개 DB는 복사하지 않았다. 검사 Python과 Node가 있으며 projects/cora-f1.json으로
명시적 3회/1800초 파일럿을 실행한다. 수용 기준/평가 라벨은 유지한다.

## 첫 F1 파일럿 결과 — 2026-11-05

분리 작업자가 실험 구현을 만들었지만 접근할 수 없는 브라우저 환경 때문에 멈췄다.
부모가 실제 앱 내부 브라우저 커널 실행과 제한 없는 루프백 검사를 제공하고, 발견된 경계 결함
2개를 회귀 검사와 함께 수정한 뒤 독립 읽기 전용 검토를 받았다.
실제 최종 전체 검사는 470개, 브라우저/Python 커널 비교는 7개 사례가 통과했다.
독립 검토는 모든 경로의 공통 fixture, API/브라우저 잘못된 입력 검사, 명시적 보호 평가 실행,
일관된 현재 문서를 요청했다. 부모가 상태/이력 표현을 맞췄으나 그 최종 문서 갱신은 아직
독립 재검토하지 않았다.

당시 F1은 완료·병합되지 않았다. 원래 CoRA는 유지했다. 증거/구조화 결과는 Git에서 제외한
`.local/preflight/F1/final-status.json`에 있다. 최초 컨트롤러 상태와 실패는 통과로 다시 쓰지
않고 과거 기록으로 남긴다. 다음 반복은 새 제한 실행에서 검토 지적을 해결해야 한다.
미해결 사용자 개념 정책 결정은 없으며 남은 일은 구현·검증이다.
이 파일럿은 더 많은 무인 작업 전에 외부 브라우저/HTTP 증거 공급과 단계별 검토 시간 배분이
필요함을 드러냈다.

## 결과별 commit/push 정책

사용자가 매 결과 전달 후 commit/push를 명시적으로 요청했다. 컨트롤러/대상 AGENTS.md와
F1 계약의 부모 마무리 정책에 적용했다. 전용 대상 브랜치에 미완료 검토 상태를 보존하고
병합·강제 push·Git 제외 비공개 증거 포함은 하지 않는다. 자동 작업자는 기준을 재정의하거나
직접 게시할 수 없다. 이는 유지보수 부모의 운영 지시이며 실행 루프 안의 새 무인 Git 실행기를
추가한 것은 아니다.

## F1 두 번째 검증 — 2026-11-05

`tools/evaluate_f1.py`는 보호 정의 해시와 사례 ID 13개, 실제 브라우저 DOM 결과, 기록된 두
경로 seed 경계에서의 공통 그래프 질의 2개, 잘못된/누락 활성화, 대상 소스 지문을 검사한다.
CoRA 패키지는 가져오지 않는다. 대상 소유 `tests/f1_evaluation.py`가 합성 도메인 관측을
내보내면 컨트롤러가 자료를 검사한다. 증거는 Git 제외 `.local/preflight/F1-round2/`에 둔다.
이는 실행 가능한 합성 사례 검증이며 독립 의미 정답 판정기는 아니다. 읽기 전용 검토 게이트는
별개다. 대상 내보내기를 실행하고 결과를 로컬로 제공한 뒤 실제 브라우저에서 열어
`#results`를 `browser-result.json`으로 저장하고
`python3 tools/evaluate_f1.py EVIDENCE --target TARGET`을 실행한다.
보호 사례 정의나 수용 임계값은 바꾸지 않았다.

2차 결과: CoRA 검사 484개, 컨트롤러 검사 15개, 보호 합성 사례 13개, 실제 브라우저 커널
비교 4개, 잘못된 브라우저 입력 10개가 통과했다. CoRA는 검사한 잘못된 API 입력 13개도
거부한다. 독립 읽기 전용 검토는 처음 기록 수정 3개를 요구했고, 수정 재확인과 검토한 대상
소스 digest 재계산 후 수용/문서 기준 12개를 모두 통과시켰다. CoRA 결과는
`codex/f1-distance-decay`의 `6888c55`다. 최종 상태 기록은 검토 결과만 추가했으며 소스/검사
지문은 평가한 버전 그대로다. 이 수정은 부모가 별도 CLI 검토로 지휘했다. 옛 실행기 상태를
다시 쓰거나 브라우저까지 완전 자율 실행했다고 표현하지 않았다.

## F1 통합과 W1 계약 — 2026-11-05

F1은 이후 통합 검토를 통과해 CoRA PR #1으로 `codex/workflow-foundation`의 `fe4aac5`에
병합됐다. 통합 후보 전체 검사 484개, 새 브라우저 비교 4개, 잘못된 브라우저 입력 10개가
통과했다. pytest 누락이라는 CI 사전 요건을 품질 게이트를 약화하지 않고 고쳤으며 서버의
품질 21개/전체 484개 검사가 통과했다. 위 첫 파일럿 미완료 표현은 과거 상태이며 최신 F1
상태가 아니다. 이 단계에는 부모의 수동 연결이 포함됐다.

`contracts/dev-workflow/W1-reviewable-delivery.{md,json}`과
`docs/01-reviewable-delivery-design.md`에 W1을 정의했다. 고정 합성 수용 시나리오 18개,
정확한 버전 증거, 실제 브라우저 어댑터, 제한 수정/검토, 누적 재개 한도, 게시기/CI 복구,
사용자 인계를 포함한다. 실제 파일럿은 CoRA의 실제 state_type 불변성 회귀와 관련 문서로
제한하며 런타임/의미/평가를 바꾸지 않는다. 컨트롤러 자기 대상 보호를 유지하고, 사전 구축에는
분리 구현 체크아웃과 외부 소유 보호 입력이 필요하다. 당시 W1은 활성 프로젝트 설정이 없고
아직 구현·실행하지 않았다. 권장 3회/60분은 명세이며 새로 강제된 CLI 동작이 아니다.

이 결과는 계약/설계/현재 상태 문서만 바꾼다. 컨트롤러/CoRA 소스·F1 라벨·실행 상태·실제
서비스는 바꾸지 않았다. 계약 JSON/해시/기준/시나리오 대응·참조 파일·문서 링크를 확인하고
기존 컨트롤러 검사로 호환성을 확인한다. W1 완료 주장 전에 구현과 W1 실제/실패 사례 실행이
여전히 필요하다.

W1 계약 준비 검증: **기존 컨트롤러 검사 15개 통과**. 고유 작업 기준 11개와 예약 주입 문서
게이트, 기준 대응을 가진 고유 시나리오 ID 18개, 포함 평가/해시 일치, 모든 참조 파일/Markdown
링크/공백 검사를 통과했다. W1 사례나 실제 파일럿은 실행하지 않았으며 구현 수용 요건으로 남는다.

## W1 revision 2: PR 선택, 브랜치/보고서 기본 — 2026-11-05

사용자가 1인 개발에서 PR 의무 제거를 승인했다. W1 revision 2 계약·평가 v2·설계·README·
프로젝트 지침을 갱신했다. 최종 결과는 검증된 push 브랜치와 버전 연결 병합 결정 보고서다.
필수 push CI·독립 검토·문서 게이트·명시적 사용자 대상 병합 승인은 유지한다.
보고서는 저장소·정확한 소스/대상 ref/SHA·차이·모든 검증 증거/한계·제안 병합을 식별한다.
대상 이동은 영향받는 통합 증거/승인을 여전히 무효화한다. 기본값에서는 PR API 기능/URL/
pull_request 이벤트가 필요하지 않다. PR 모드는 명시적 선택이며 PR 전용 필수 게이트는
우회나 요청하지 않은 PR 생성 대신 결정 요청을 만든다. 실제 파일럿은 PR 생성/갱신 호출
0회를 입증해야 한다.

사용자 승인 계약 변경은 시나리오 ID 18개와 다른 검사를 모두 유지하면서
W01/W11/W13/W17/W18의 전달/복구 기대와 관련 기준을 바꾼다. 포함 평가와 외부 파일 해시를
맞췄으며 v1은 Git 이력에, 이전 해시/결정은 revision 2에 남긴다. 위 준비 기록은 revision 1이다.
당시에는 계획 단계였으며 컨트롤러/런타임 동작·활성 프로젝트·W1 실제 실행은 바꾸지 않았다.

revision-2 검증: **기존 컨트롤러 검사 15개 통과**. 작업 기준 11개와 유지된 주입 문서 게이트,
고정 시나리오 ID 18개, 승인된 시나리오 5개만 변경한 점, 포함 평가/파일 SHA-256 일치,
이전 버전/해시 이력, 기본 branch_report 설정, 참조 링크/공백을 확인했다.
런타임·프로젝트 설정·스키마·기존 검사·과거 CoRA 평가 정의는 유지했다.
W1 시나리오 18개와 실제 파일럿은 당시 실행 결과가 아닌 명세였다.

## W1 구현 후보 — 2026-11-05

사용자가 revision 2 구현을 요청했다. 개발은 `codex/w1-reviewable-delivery`에 분리하고
구현 전에 소유 계약/평가/기존 검사 해시를 외부 스냅샷으로 남겼다. 기존 실행기/검사와 W1/F1
수용 정의는 보존한다. 새 모듈과 선택적 파일럿 설정은 docs/01-reviewable-delivery-design.md에
대응시켰다. 대상 병합이나 PR은 승인되지 않았다.

실제 headless Chrome 하네스 실행, 불변 소스/환경 기록, 독립 검토 기반 수정, 누적 재개 한도,
정확한 경로의 컨트롤러 게시, push-CI 실패 전달, 버전별 병합 보고서를 구현했다.
미완료 의미 작업은 별도의 게시 안전 검토를 요구하며 push됐다는 이유로 수용되지 않는다.
기능 누락·미해결 결정·예산 소진은 해결 가능한 상태를 보존한다. 새 상태 버전 2는 선택적으로
사용하며 기존 complete 상태를 소급 인증하거나 이전하지 않는다.

당시 검증 진행 중: 합성 실패 재현은 모의 모델/GitHub 응답임을 명시하고 실제 임시 bare 원격과
실제 Chrome을 사용한다. 실제 CoRA 파일럿은 실제 모델 작업자/검토자·프로젝트 검사·Chrome·
GitHub push CI·보고서 수집을 부모 단계 연결 없이 수행할 예정이다. 코드의 존재나 합성 fixture만으로
W1 마일스톤 완료가 성립하지 않는다. 실제 실행 후 결과와 최종 독립 검토를 아래에 기록해야 한다.

사전 구축 실패/복구 검증에서 기존/새 검사는 처음 41개 통과에 도달했다.
첫 실제 CoRA 시험은 집중 31개/품질 21개/전체 484개와 실제 Chrome 비교 4개/잘못된 입력
10개/보호 사례 13개를 통과했다. 이후 통과 판정과 비어 있지 않은 결정 목록이 모순되어
멈췄고 게시 안전 검토는 시간 초과됐다. 수용으로 다시 표시하거나 강제 게시하지 않았다.
별도의 독립 확인은 사용자 선택이 필요 없음을 확인했다. 제한된 형식 확인·생성 하네스 전후
연결·읽기 전용 점검 재시도·누적 예산 연결 재검증을 검사했다.
개정 실제 시험은 같은 고정 작업으로 새 분리 CoRA 체크아웃/브랜치를 사용하고 원래 마감/횟수를
모두 이어받는다. 원래 실패는 외부 w1-live-pilot 증거에 남는다. 아래 결과는 두 시험을 구분해야 한다.

## 당시 W1 전달 상태: 구현 후보, 실제 수용 미완료

실제 시험들이 고정된 누적 3회를 소진했다. 시험 1은 검사/브라우저를 통과했지만 통과 판정/
결정 없음 표현이 모순된 검토를 받았다. 원래 중단을 보존하고 독립 형식 확인을 별도로 기록했다.
연결 시험 2는 같은 원래 마감/횟수로 새 CoRA 기준에서 시작했다. 작업자가 K01의
이름을 바꿔 보호 내보내기의 공개 함수 조회를 깨뜨렸다. 일반 검사 31/21/484개는 통과했지만
보호 검증은 실패했다. 다음 작업자는 일반적인 브라우저 실패 메시지만 받아 호환성 오류를
고치지 못했다. 컨트롤러는 3회에서 중단했으며 실패를 버리거나 라벨을 완화하거나 PR/병합/
예산 재시작을 하지 않았다. 게시 안전 검토가 시간 초과되어 자동 브랜치 push는 주장하지 않았다.
원래 CoRA 체크아웃/대상 브랜치는 유지했다.

컨트롤러 진단 누락을 수정했다. 브라우저 실패 피드백은 정확한 로그/기록/프로젝트 관측을
제공하고 공개 검사/도우미 이름을 바꾸기 전에 이를 확인하도록 명시한다.
독립 소스 검토 지적도 해결했다. 유효 환경/실행 파일/의존성 식별값, 현재 연결 검사,
매 확인 시 CI 상태 저장, 결정적 고아 보고서 복구, 보고서 후 준비 상태 저장을 추가했다.
부정 검토 시 수용 무효화와 부모 한도의 단일 할당 기록도 추가했다.
고정 W1/F1 수용 정의·기존 실행기·원래 검사 15개는 유지했다.
코드/설계는 docs/01-reviewable-delivery-design.md와 맞췄다.

당시 최종 로컬 검증: **54개, 51.348초에 통과**.
명령은 `python3 tools/evaluate_delivery.py --pilot-state .../w1-live-pilot-v2/state.json
--output .../w1-bootstrap/evaluation-reviewed.json`이다.
모델/GitHub 실패 fixture는 합성임을 명시하고 임시 Git/bare 원격과 설치 Chrome은 실제다.
평가는 **INCOMPLETE**로, 대응 시나리오 16개는 통과했으나 실제 전 과정 게시/CI 성공 부재로
W01/W17이 실패했다. 소스/입력/환경 증거는 대상 밖에 보존한다.
결과 전달 전에 소스 수정의 독립 후속 검토가 필요하다.

남은 사용자 결정은 컨트롤러 수정 후 추가 제한 실제 시험의 승인이다.
이는 W1 계약의 예산 확대이며 검사 완화나 병합 승인이 아니다. 당시 추가 실제 파일럿은 없었다.
계약 작성 메타데이터는 과거 기록으로 유지하고 위 구현/설계가 진행 상태를 설명한다.
당시 W1 마일스톤은 완료되지 않았다.

### 최종 소스 검토 수정과 전달 경계

후속 검토자는 연결 할당의 추가 충돌 구간을 발견했다. 최초 상태·입력 연결·실행 ID·상속
예산을 담은 원자적 할당 저널로 수정했다. 상태 저장을 활성화보다 먼저 수행하여 충돌 시 같은
자식을 복구하고 한도를 잃거나 보충하지 않는다. 외부 보호 입력 변경은 복구를 막는다.
새 실패 사례 2개는 충돌 복구와 바뀐 외부 정책을 채택하지 않는 동작을 확인한다.

당시 정확한 소스의 로컬 평가는 **56개, 54.131초에 통과**했으며
`evaluation-final-source.json`은 대응 사례 16개 통과와 W01/W17 미완료를 기록했다.
추가 실제 시험은 없었다. 최종 소스 재검토는 이 수정을 확인하며 전 과정 수용에는 다른 상태
디렉터리나 바꾼 검사 이름이 아니라 명시적인 새 시험 예산이 필요하다.

결과별 보존: 부모가 중단된 CoRA 후보의 네 파일 범위를 확인하고
`codex/w1-state-type-pilot-v2`에 명시적인 미완료 WIP `efb5740`으로 저장/push했다.
실패한 시험 뒤에는 중단 상태 문서만 추가했고 src/tests 해시는 실제 실패 관측과 같다.
이는 수동 부모 마무리이며 자동 게시·CI 수용·W1 성공이 아니다. PR/대상 병합은 없다.
모든 원래 실패 상태/원본 기록은 유지하고 `manual-incomplete-publication.json`으로 별도
기록을 구분한다. 일반 CI의 녹색 상태는 실패한 보호 게이트를 대신하지 못한다.

최종 저널 구간 검증: 상태 저장 전과 저장 후/활성화 전 복구 모두 같은 원래 연결을 비교한다.
제어 값을 활성화 전에 저장/검증하고 직전에도 연결을 재확인한다. 주입한 충돌 검사는 같은
입력 복구 시 제어 값/예산이 유지되고 외부 정책이 바뀌면 저널 활성화 없이 거부됨을 보인다.

당시 최신 정확한 코드 평가는 58개, 58.669초에 통과했다.
외부 evaluation-durable-final.json은 W01/W17 false, 대응 시나리오 16개 true인 INCOMPLETE다.
추가 실제 CoRA 시험은 없었다. 검사 뒤에는 문서만 갱신했고 구현/검사/계약 입력은 같다.
최종 좁은 소스 재검토가 수정을 확인하며 새 시험 예산은 사용자 결정이다.

최종 독립 제한 재검토는 소스의 할당/정책 충돌 결함이 해결됐고 문서도 정확함을 확인했다.
그러나 수정 후 실제 W01/W17 성공과 추가 예산 승인이 없어 전체 판정은 changes_requested다.
이를 W1 전체 수용이나 병합 준비 완료로 설명하지 않는다. 다음 요청은 기준 변경/병합이 아닌
명시적인 제한 시험 한도다.

### 사용자 승인 추가 시험과 문서 출처 수정

사용자는 동일한 완료 기준과 과거 실패 보존을 조건으로 최대 1800초/수정 3회를 추가 승인했다.
`projects/cora-w1-approved-trial.json`은 새 한도·이전 실행 경로·정확한 K01 호출 실패를 기록한다.
자동 예산 갱신이 아니며 과거 설정의 소진 한도도 유지한다.

`.local/w1-approved-trial/state.json`의 실제 실행은 3회를 사용하고 `budget_exhausted`로 끝났다.
모든 후보가 집중 31개·품질 21개·전체 484개·차이 검사·실제 Chrome·고정 F1 평가
(보호 13개·브라우저 경계 비교 4개·잘못된 입력 10개)를 통과했다.
작업자는 state_type/경로 검사를 약화하지 않고 원래 공개 K01 이름을 복원했다.
독립 검토자는 처음에는 대기 결과 표현, 이후에는 이전 시도의 digest 참조 때문에 문서를 거부했다.
수용 후보·자동 게시·정확한 HEAD의 push CI·성공한 W01/W17 보고서는 없었다.
게시 안전 검토는 시간 초과됐고 최종 미완료 보고서와 원본 실패를 보존했다.
이전 3회와 새 3회는 초기화하지 않고 모두 확인할 수 있다.

자기 문서에 후보 digest/현재 결과를 넣으면 후보가 바뀌고 다시 문서를 갱신하라는 검토가
나오는 순환이 드러났다. 컨트롤러는 안정적인 실행/시도/보고서 위치를 제공하고 대상 문서의
과거 관측과 외부 증거/보고서의 최종 정확한 후보 결과를 명시적으로 구분한다.
작업자는 이전 digest가 현재 소스를 인증한다고 주장하면 안 된다. 검토자는 현재 manifest/
검사/브라우저 증거를 독립 검증하고 오해 유발 주장·문서 누락·의미 차단 문제를 거부해야 한다.
명확한 과거 인용만을 이유로 자기 참조 갱신을 요구하지 않는다. 예약 문서 기준·보호 계약/평가·
수용 라벨·기존 실행기는 유지했다. 이는 지침/출처 수정이며 AI가 항상 올바르게 이해한다는
증명은 아니다. 네 번째 실제 사이클은 승인·실행하지 않았다.

회귀 평가와 독립 수정 검토는 외부에 기록한다. 별도 승인 실제 실행이 통과할 때까지
당시 W1은 미완료다.

수정 후 회귀: **58개, 60.262초에 통과**. 고정 W1 평가는 대응 시나리오 16개 통과와
W01/W17 false인 INCOMPLETE다. `evaluation-approved-trial.json`은 검사 소스를 고정하고,
이후에는 보고 문서만 마무리했다. 부모는 CoRA 네 파일 후보를 별도 확인해 명시적 미완료 WIP
**0d28c04**로 보존했다. 이 수동 보존은 자동 게시나 현재 후보의 수용을 충족하지 않는다.
외부 `manual-approved-trial-preservation.json`이 이를 구분한다.

독립 제한 수정 검토 `provenance-review.json`은 수정 정합성·과거 사실·명시적 예산 승인·
문서 동기화의 4개 기준을 차단/결정 없이 통과했다. 범위는 소스/출처 수정이며 W1 수용은 아니다.
실제 W01/W17은 당시 미완료였다.

### 승인된 60분/5회 시험: 검토 단계 시간 초과 복구

사용자가 새 최대 3600초/5회 한도를 승인했다. 새 `cora-w1-approved-trial-60m` 설정은 이전
6회를 별도로 보존한다. 첫 후보의 실제 검사와 Chrome은 통과했지만 독립 검토가 옛 명령별
240초 한도에 걸려 최종 결과가 없었다. 시간/횟수가 남았는데도 전체 소진으로 잘못 분류했다.
게시 안전 검토도 시간 초과됐으며 소스는 그대로 미완료 WIP a037b1b로 수동 보존했다.
의미 수용이나 대상 병합은 없었다.

검토는 이제 원래 누적 마감 안에서 600초 단계 한도를 사용한다. 단계 시간 초과는 검토 부재
피드백으로 다음 제한 수정 사이클에 전달하며 실제 전체 만료는 여전히 중단한다.
과거 시간 초과의 좁은 연결 복구에는 최종 검토/사용자 결정 부재, 보호된 시간 초과/입력 기록,
동일한 소스, 남은 원래 시간/횟수가 필요하다. 기존 배타 영속 할당 저널이 분기 확장과 한도
갱신을 막는다. 복구 설정은 원래 마감과 사용 횟수를 복사하며 새 한 시간이나 추가 5회를
부여하지 않는다. 실제 부정 결정이나 완료된 검토에는 이 검토 부재 복구를 쓸 수 없다.
회귀 사례 4개가 경계·누적 연결·분기 거부·전체 만료를 확인한다.

수정 중 상태: 첫 사이클은 미완료이며 원래 사용자 승인 3600초/5회 안에서 재개하기 전에
복구 소스를 독립 검토한다.

시간 초과 복구 회귀: **62개, 62.248초에 통과**. 고정 W1 평가는 대응 사례 16개 통과와
W01/W17 미완료다. 검토 부재는 실제 파일럿 성공이 아니다.

첫 제한 복구 검토는 과거 증거를 경로만 확인하는 방식을 거부했다. 이제 할당 전에 독립 검토한
복구 설정에 정확한 부모 상태와 원본 시간 초과/입력 SHA-256을 고정한다.
해시 변경·누락은 복구를 거부한다. 과거 부모는 시간 초과 시 해시를 기록하지 않았으므로,
이는 유지보수 컨트롤러가 확인한 원본을 증언하는 복구 기록이지 소급 부모 서명은 아니다.
영속 저널이 설정과 원래 부모 바이트를 연결해 이후 변경을 거부한다.
다섯 번째 회귀 사례는 수정됐거나 고정되지 않은 원본 증거를 확인한다.

해시 고정 증거 복구 재검토가 차단/결정 없이 5개 기준을 통과했고 회귀 검사 63개도 통과했다.
새 한도 승인이나 실제 수용 주장은 아니다. 원래 고정 마감 아래서만 복구를 재개한다.

### 실제 제한 복구 파일럿의 인계 게이트 도달

복구는 첫 시간 초과 검토를 포함한 원래 시작/마감(3600초/최대 5회)을 재사용했고 누적 **2회**로
끝났다. 자식 실행의 기준은 수동 보존한 미완료 WIP a037b1b다. 사전 컨트롤러 수정/WIP 보존은
최종 자식 전에 이뤄졌으며 무인 작업으로 주장하지 않는다. 자식 내부에서는 부모의 수동 단계
연결이나 결과 복사 없이 컨트롤러가 실제 작업자 → 집중 31개/품질 21개/전체 484개/차이 검사 →
실제 Chrome/고정 F1(보호 13개·경계 비교 4개·잘못된 입력 10개) → 독립 5개 기준 통과 →
commit/push **81b1e217606ea78252b93d132660c1ca0102f4f0** → 정확한 HEAD의 push `Test/test`
CI **42126115535** → 불변 보고서 → `ready_for_merge_approval`을 수행했다.
현재 전체 기준 대비 HEAD 범위는 허용 검사와 관련 문서이며, 최종 자식은 이미 보존된 K01
구현의 문서를 다듬었다.

보고서: `.local/w1-approved-trial-60m-recovery/reports/d52f50ed2f008ea47546c325de4dba9472e8831708191a548309f67d2e10559c.json`.
대상은 변하지 않은 foundation **fe4aac5**, 소스는 **81b1e21**이며 제안 병합은 사용자 결정이다.
모든 과거 실패는 유지했다. PR은 없고 CoRA 대상과 dev-workflow main 모두 병합하지 않았다.
W1 최종 시나리오 평가/독립 마일스톤 감사는 CoRA 작업 검토자와 별도이며 아래에 결과를 기록한다.

최종 고정 W1 평가: **PASS, 시나리오 18/18, 검사 63개를 57.855초에 통과**
(`evaluation-60m-final.json`). W01/W17은 합성 모델/GitHub fixture가 아닌 실제 최종 자식
실행을 사용한다. 독립 최종 마일스톤 검토는 별개이며 최종 응답을 기록하기 전까지 대기다.
평가 후에는 보고 문서만 바꿨고 컨트롤러/검사/계약은 유지했다.

최종 독립 W1 마일스톤 감사 `60m-milestone-review.json`은 차단/결정 0개로 **12개 기준을
모두 통과**했다. 고정 계약·실제 소스/차이·이전 실패/수정 기록·최종 소스/환경 연결·브라우저·
정확한 HEAD CI·불변 보고서·누적 예산·명시적인 사전/수동 경계를 확인했다.
W1 revision 2는 이 제한된 파일럿 범위에서 구현·검증됐다. 일반적 의미 신뢰성·전체 UI·OS
격리·금액 계측까지 입증하지는 않는다. CoRA **81b1e21**과 컨트롤러 구현은 사용자 병합 승인을
기다리는 전용 브랜치에 남아 있고 main/CoRA foundation은 이동하지 않았다.
2회 완료 후 추가 실제 사이클이나 한도 갱신은 없었다.

## W2 승인된 순차 대기열

현재 W2 상태: 구현과 최종 94개 회귀 검사가 통과했다. 독립 검토 결과는 아래에 시간순으로
기록한다. 브랜치는 `codex/w2-approved-queue`이며 어느 소스/대상 브랜치도 병합하지 않은
검증 W1을 기반으로 한다. 사용자는 W2 구현을 승인했으며 그 지시에서 실제 CoRA 목표 선택·
새 승인·스케줄링·병합을 추정하지 않는다.

새 `tools/approved_queue.py`는 정확한 대기열/권한 해시에 대한 운영자 제공 승인을 기록하고,
DAG/작업 트리/HEAD 경계를 검사하며 영속 대기열/저장소/작업 시간·횟수를 예약하고 기존 W1
엔진을 실행한다. W1 게시·검사·브라우저·의미/문서 검토·원격 게이트는 유지한다.
전달 완료 상태 전에 현재 소스·보고서 식별값·검사/브라우저/검토/CI·원격 HEAD/기준을 확인한다.
의존성은 검증된 결과 전달 순서를 정할 뿐 코드 병합/통합을 의미하지 않는다.

엔진 실행 전에 dispatch를 영속 저장한다. 부모가 중단되면 완전한 증거로 복구하고 불명확하거나
자식 증거가 없으면 재실행 없이 멈춘다. 대상 잠금과 대기열 식별값 할당 잠금으로 중복/분기
실행을 막으며 할당 상태를 삭제해도 한도는 갱신되지 않는다. 미사용 예약 환급이나 자동 새
실행 창은 없다. 시계 역행/만료된 창은 새 dispatch를 막는다.

예제는 의도적으로 미설정이며 실제 사용자 승인 기록이 없다. 실제 W2 Codex/GitHub/CoRA
시험은 시작하지 않았다. 새 실패 검사는 실제 임시 Git/bare 원격과 W1 엔진에 명백한 합성
모델/CI/브라우저 응답을 사용하며 기존 W1 실제 Chrome 검사는 별도로 유지한다.
운영자 승인 기록은 로컬 신뢰 관례이며 신원 인증이나 OS 격리가 아니다.
포그라운드 대기열 처리를 구현했고 스케줄러 설치·알림·자동 목표/계약 생성·통합·금액 계측은
후속 범위다.

당시 W2 최종 회귀: **대기열 24개, 전체 컨트롤러 87개가 68.607초에 통과**했다.
원래 W1/기존 범위와 실제 Chrome 검사를 포함한다. 추가 대기열 검사는 CLI 할당/상태 삭제·
동시 대기열 잠금·재승인 입력과 오래된 작업 목록·손상된 연결·원격 점검 실패/이동을 다룬다.
증거는 외부 `w2-verification.json`, `w2-regression-final.log`에 있으며 독립 소스 검토는 별개다.
fixture 성공은 실제 AI/GitHub 대기열 운영이 아니다.

### W2 독립 감사 수정

첫 독립 검토는 수정을 요청했고 원래 판정은 외부 `w2-review.json`에 보존했다.
잘못된 상태 위치를 디렉터리 생성 전에 거부하고, 비거나 일부만 남은 시작 상태를 초기화하지
않으며, 배타적 CLI 할당에 최초 실행/입력 연결/마감을 고정하고, 그 할당 없는 기존 상태를
거부하도록 수정했다. 승인 전 확인 자료는 별도이며 예산을 부여하지 않는다.
승인은 깨끗한 HEAD/내용/브랜치/원격 기준 SHA도 고정한다. 대기 작업은 잠금 아래 시작 전에
이를 다시 확인한다.

대기열은 dispatch·의존성 검증·증거 확인/저장을 정렬된 대상 잠금 안에서 수행하고 최종 전달 전
모든 완료 작업을 재검증한다. 원격 ref는 원자적으로 잠글 수 없으므로 시각과 명시적 최신성
한계를 두고 사용자 승인 실제 병합 시 재검증한다. 잠금을 따르지 않는 외부 Git/파일 작성자나
향후 원격 변경은 보장하지 않는다. 브라우저 수용은 엔진/버전·생성 하네스 해시·원본 DOM 결과·
결과 해시·준비/버전/DOM/검증기 실행 기록·보고서 검증 관측을 확인한다.
신뢰된 로컬 기록의 일관성이 서명된 실행 증명이나 파일시스템 적대자에 대한 증거는 아니다.

과거 중간 검증: 수정 대기열 검사 30개가 18.753초에 통과했다. 그 시점에는 할당 기록 삭제 사례
하나를 추가한 전체 재실행을 진행 중이었으며 최종 결과와 독립 재검토는 아래에 이어진다.
위의 21/24개와 84/87개 검사 결과는 과거 기록이다.

### W2 최종 관측 회귀와 소스 검토 경계

최종 소스 회귀는 **94개를 91.071초에 통과**했다. **W2 31개**, 기존 63개와 원래의 기존 검사
15개를 포함한다. `w2-release-tests.log`의 실제 종료 줄(Ran 94 / OK)이며 일부 진행 출력에서
추정한 결과가 아니다. 앞선 `w2-final-regression.log`도 94개, 77.037초 통과로 끝났다.
이는 앞선 단계별 수치/대기 기록보다 최신이다. 최종 소스는 잘못된 상태의 객체/버전을
엄격히 거부하며 기존 손상 상태 검사가 이를 포함한다.

독립 재검토는 6개 수정 후 소스/동작 기준 7개를 통과시켰지만, 미완료 회귀 스냅샷을 읽었고
설계 헤더가 여전히 87개여서 documentation_sync/전체 승인을 보류했다.
`w2-rereview.json`에 그 판정을 보존한다. 현재 설계/헤더는 관측한 최종 94개 결과로 바꿨으며
최종 증거/문서 수정을 다음에 독립 확인한다. 최종 94개 실행 뒤에는 소스/검사를 바꾸지 않았다.
실제 W2 모델/GitHub/CoRA 운영·스케줄러 설치·병합은 주장하지 않는다.

최종 독립 W2 검토 `w2-final-review.json`은 차단 지적과 사용자 결정 없이 **8개 기준을
모두 통과**했다. 수정한 소스/동작 7개 기준과 새 94개 검사 종료 결과/문서 갱신을 수용했다.
이전 부정 검토는 보존한다. 최종 검증은 **W2 31개 + 기존 63개 = 94개, 91.071초 통과**다.
이 실행 후 보고 문서만 마무리했고 소스/검사는 `w2-final-observations.json` 해시와 같다.
W2 구현은 전용 브랜치에서 완료됐다. 실제 승인된 운영 대기열과 스케줄러/병합은 별도의
미수행 작업으로 남긴다.


## 영어 우선·한국어 번역 문서

사용자가 모든 문서를 영어 위·한국어 번역 아래로 요청했다.
추적 중인 Markdown 8개를 계약·운영 규칙·전체 과거 이력까지 변환했다.
기존 영어 원문과 한국어 계약 원문은 각 언어 영역에 그대로 유지했다.
명령·경로·식별자·해시·기준·과거 결과를 보존했다. JSON 계약·스키마·고정 평가·
변경 불가인 외부 실행 자료는 유지했다. AGENTS/README는 이후 문서도 완전한 번역을
동시에 갱신하도록 요구한다.

앞으로 생성하는 병합 결정 Markdown 보고서는 고정 설명을 두 언어로 쓰고 작업/진단/정책의
기계 필드를 양쪽에 원문 인용한다. 모델 번역이나 새 실행 비용 없이 원본 증거를 유지한다.
기준 JSON 보고서 식별값·게시/검토 게이트·기존 보고서 파일·실행 동작은 유지한다.
렌더러 회귀 검사는 언어 순서·정확한 버전/증거 필드·원본 payload 보존을 확인한다.
문서 구조·원문 보존·링크·컨트롤러 회귀를 확인하고 최종 관측 검증은 아래에 기록한다.
새 대상 실행이나 병합은 없다.

W1 단계 맥락도 사용자가 승인한 언어 정책을 이후 작업자와 독립 검토자에게 전달한다.
적용 범위는 해당 작업에서 허용된 문서 경로로 제한한다.

두 언어 문서 검증: 8개 모두 원래 언어의 본문을 보존했고 제목 구조·명령 블록·링크·숫자
대조를 통과했다. 새 보고서 렌더러 사례를 포함한 최종 컨트롤러 회귀는 **95개, 117.796초에
통과**했다. 기계 판독 JSON 파일은 유지했다. 번역/표현의 독립 검토는 최종 응답 후 별도로
기록한다.

독립 두 언어 검토는 번역 충실성·전체 범위·렌더러 정합성·후속 정책·문서 동기화의 5개
기준을 차단 지적/사용자 결정 없이 통과했다(`bilingual-review.json`). 검토/검사 후에는
이 두 언어 결과 기록만 추가했으며 런타임 코드는 유지했다.

## 검토 JSON 접수 — 2026-11-06

`tools/review_intake.py`·비활성 정책/프로젝트 예제·신뢰할 수정 템플릿을 구현했다.
원본/선택 증거를 고정하고 정확한 검토 소스/승인 설정을 연결하며 기존 W1 게이트와
신뢰할 재실행 검사를 유지한 단일 W2 작업을 생성한다. 중복/실행 이력을 보존하며
`awaiting_human_retest`로 반환한다. 정책/모델 모호성과 오래되거나 누락된 입력은
중단한다. 기존 W1은 미완료 브랜치 WIP를 보존할 수 있지만 수용은 아니다.
일정·CoRA 의존성·활성 정책·새 실제 CoRA 수정은 시작하지 않았다. 실제 제공 검토의
읽기 전용 사전 검사는 `911127c`와 `cc820de`의 차이를 감지해 실행을 거부했다.
실제 Git/W2/W1과 합성 AI/브라우저/CI/재실행을 사용해 검사한다. 최종 전체 회귀 **123개가 91.014초**, 새 접수/재실행 집중 **28개가 12.673초**에
통과했다. 실제 W2/W1/Git 인계와 합성 AI/브라우저/CI/재실행 관찰을 사용했다.
첫 독립 소스 검토가 승인 설정 캡처 경쟁과 재실행 증거 연결 부족을 발견했다.
준비 입력과 원래 승인의 일치 검사·실행 시 원래 승인 재검사·실제 질문/설정·소스·
검토·스냅샷·그래프 버전에 연결된 새로운 관찰 파일 검사를 추가해 모두 수정했다.
두 발견의 회귀를 추가했고 기존 게이트를 약화하지 않았다. 초기 모의 컨트롤러가
새 게이트를 불러올 때 실제 환경의 __pycache__ 무시 규칙을 빠뜨린 문제도 수정해
최종 전체 검사를 통과했다. 과거 로그는 무시된 .local/에 비공개로 보존한다.
최종 독립 읽기 전용 검토(review-intake-final-review.json)는 차단/소유자 결정 요청
없이 5개 기준을 통과했다. 실제 소스/검사/문서와 실행 기록을 확인했으며 실제
CoRA 수정이나 일반 의미 정확성 증명은 아니다. 검토 후에는 이 최종 관찰 기록만
추가했고 구현/검사는 변경하지 않았다. commit/push는 브랜치 후보 게시이며 정책
활성화·소유자 재검토·병합은 별도다. 범위와 한계는 [설계/운영](03-review-json-intake.md)을
참조한다.

## 데이터 품질 시험 — 2026-11-12

tools/quality_workflow.py와 [데이터 품질 워크플로](data-quality-workflow.md)를 구현했다. W1 미승인 안전 게시·push CI를 의미 검토 전에 수행한다. 전송 환경 변경은 실행 증거를 무효화하지 않고 실제 실행 환경 변경은 한도 내 재검증을 수행한다. 현재 테스트와 한계는 가이드에 기록하며 새로운 실제 중첩 에이전트 성공을 주장하지 않는다.

## 검토 요청 접수 — 2026-11-15

tools/quality_intake.py에 선택적으로 활성화하는 동일 출처 검토 메모 접수를 구현했다.
기존 검토 화면을 `--policy projects/.local/quality-intake.json`과 함께 제공한다.
정책은 intake를 활성화하고 contracts/cora/data-quality-removal.json을 참조하며
trial 명령에 정확한 repair_mode를 지정하고 repair_project가 없어야 한다.
이번 접수는 고정 도메인 복구를 실행하며 브라우저 메모로 임의 코드 편집을 시키는
것은 지원하지 않는다. 기존 선택적 W1 CLI 수정은 유지한다. 기본 비활성인
projects/cora-quality-intake.example.json을 참고한다.

GET /api/session은 일시적인 토큰을 제공한다. POST /api/requests에는 토큰,
정확한 loopback Host·Origin, JSON 형식과 크기가 제한된 본문이 필요하다.
schemaVersion=1 / changes_requested / 일치하는 planDigest / 비어 있지 않은
이유만 받는다. 추가 명령·경로·예산 필드는 권한이 되지 않는다. 다른 사이트의
요청을 거부하고 허용적인 CORS는 켜지 않는다. 서버는 127.0.0.1에 연결한다.
토큰은 OS 사용자 인증이 아니며 로컬 프로세스 간 격리는 제공하지 않는다.

할당 전에 저장된 계획 digest·선택 노드·그래프 감사 바인딩·스냅샷 해시·대상
manifest·정책·계약을 검사한다. 실행 시에도 시험 전에 그래프를 다시 확인한다.
계획·정책·계약별 지속 기록 키로 재전송이나 메모 수정에 따른 재실행을 방지한다.
단일 큐 작업자는 queued/running/최종 상태와 원래 누적 마감(최대 3600초)을
기록한다. 서비스 재시작 시 실행 중이던 요청은 decision_required로 바꾸고 만료된
대기 작업에는 새 한도를 주지 않는다. 대기 작업은 보존한 마감 안에서만 이어 간다.
서비스 잠금으로 여러 인스턴스가 동시에 실행되는 것을 거부한다.

GET /api/requests/ID는 토큰을 요구하며 진행과 결과 링크를 제공한다. 화면은
이를 조회하고 sessionStorage의 요청 ID로 새로고침 후에도 이어서 표시한다.
결과 경로에는 HTML·계획·검사·비교만 제공하고 원본 DB·격리 보관 파일·로그는
공개하지 않는다. 과거 검토 파일을 덮어쓰지 않고 응답 시 HTML에 제어를 추가한다.
Export notes는 로컬 파일 저장으로 유지한다. approve_proposal로 실행·반영을
시작할 수 없다. 비교 실패는 승인이 아닌 실패로 표시한다. 메모와 요청 이력은
.local/에 비공개로 보존한다.

소유자가 선택한 제거 계약은 모든 근거 참조를 보존하고 확인된 스레드를 나누며
조회 불가 원본 근거를 숨겨 보관하고 복사본에서 되돌리기를 검증한다. 도메인
strict 모드는 원본 누락을 계속 차단한다. 원본 그래프 반영·병합·예약 모니터링·
일반적/로컬 LLM 의미 승인·범용 브라우저 코드 수정 접수는 후속 작업이다.
실제 HTTP로 CSRF·Host 재바인딩·토큰·본문 검사, 오래된 그래프·스냅샷·계획 거부,
지속 중복 방지, 고정 정책 실행, 한도 초기화 방지, 재시작 처리와 파일 허용 목록을
검사한다. 도메인 테스트는 삭제·격리 보존·근거·되돌리기·소유자 충돌을 다룬다.

## Recall 중심 수정 검토 — 2026-11-15

요청 기능을 데이터 품질 진단 화면에서 기존 CoRA 실데이터 Recall 검토로 옮겼다.
선택적인 CoRA loopback JSON 전달은 컨트롤러를 import하지 않고 요청을 보낸다.
컨트롤러의 토큰·Host/Origin·고정 정책·마감·중복 규칙은 유지한다. 일치하는 스냅샷·
그래프 순서를 가진 크기 제한 reviewRecord를 받아 실제 질문·답변·옵션·문제 분류·
이유를 비공개로 저장한다. 명시적인 mixed_node만 제거 계약으로 실행하고
recall_answer는 작업자 실행 없이 범위 검토로 지속 기록한다. 중복 혼합 노드 요청은
새 검토 문맥을 첨부하되 과거 복구를 재시작하거나 마감을 초기화하지 않는다.

세션·상태 응답은 계획 digest와 최근 요청 ID를 제공한다. 범위 검토 대기 의견은
읽기 쉬운 접수 내역을, 실제 시험은 별도 결과 링크를 제공한다. 오프라인 내보내기는
유지한다. 이전 형식 메모는 API에서 지원하지만 진단 화면에 전송 기능을 주입하지
않는다. 본문 한도는 256 KiB이며 큰 기록은 조용히 줄이지 않고 비공개 내보내기를
사용해야 한다. `--review-url http://127.0.0.1:8773/`로 돌아가기 링크를 설정한다.
선택적인 `.local/quality-views/HASH` 표현 캐시는 절대 trial 경로를 JSON 문자열로
인코딩한 SHA-256을 사용하며 view-binding.json의 계획 digest가 일치해야 한다.
변경 불가인 과거 HTML/JSON을 대체하지 않고 CoRA의 새 읽기 전용 설명을 표시한다.

새 도메인 비교 설정에는 신뢰하는 compare argv에
`--review-request {run}/repair-request.json`을 추가한다. 제출한 질문은 승인 정답이
아닌 사람 검토 자료로 추가되며 고정 검사를 바꾸거나 LLM 생성을 요구할 수 없다.
질문 캡처 이전의 과거 요청에는 원래 질문 재실행이 없음을 명시한다. 범용 코드 편집,
식별자 충돌 해결, 원본 반영이나 병합을 허용하지 않는다. 실제 사용자 판단은 여전히 필요하다.

## 검토 전송 수정 — 2026-11-15

실제 Recall 추적은 기존 256 KiB 접수 한도를 초과할 수 있다. 선택적 중계와 외부 접수기는 전체 검토 기록을 보존하며 최대 8 MiB의 제한된 JSON 요청을 받는다. 중계 오류는 JSON으로 반환하며, 화면은 현재 판단을 버리지 않고 JSON이 아닌 서버 응답을 설명한다. 작업 범위·권한·원본 그래프 제한은 유지한다. 회귀 검사는 300 KB 합성 검토와 JSON 중계 거절을 확인하며 모델 답변의 정확성을 입증하지 않는다.

## 답변·검색 개발 계약 — 2026-11-15

`contracts/cora/recall-answer-repair.json`과 영문/한글 지침, 비활성 `projects/cora-recall-answer-{repair,intake}.example.json` 설정 템플릿을 추가했다. 고정 그래프 제거와 구분하여 기존 비공개 검토 접수 및 W2/W1 코드 개발 흐름을 사용한다. 기준 버전 재현·타당한 기대 동작·합성 사례의 기준 실패/후보 통과·부정 인접 사례·원래 질문 전후 재실행·별도 검토·문서·휴먼 재검토·정확한 커밋의 CI를 요구한다. Me 누락 보고만으로 Me가 답변에 포함되어야 한다고 정하지 않는다.

`execution_limits`는 3600초/5회를 고정하며 검토 정책 로딩과 직접 W1 초기화 모두 새 상태 생성 전에 초과를 거절한다. 이 필드가 없는 과거 계약은 기존 동작을 유지한다. 재실행 연결 검사는 이제 대화 메타데이터도 포함한다. 이번 전달은 계약과 실행 가능한 제한 검사 추가이며 실제 CoRA 수정 실행은 아니다. 웹의 답변 보고는 계속 범위 검토로 접수되고 비활성 예제는 실행하지 않으며, 구체적으로 고정된 실제 데이터 재실행 어댑터가 필요하다. 기존 요청·혼합 노드 정책·이전 예산·원본 그래프는 유지한다. `contracts/cora/recall-answer-repair.md`를 참고한다.

이번 전달 검증: 컨트롤러 검사 146개가 117.236초에 통과했다. 집중 검사는 접수 한도·상태 생성 전 직접 W1 거절·잘못된 한도·대화 문맥 누락 거절을 확인한다. 계약 경로/기준과 영문/한글 절을 검토했으며 공백 검사를 통과했다. 이번 계약 전달에서는 실제 코드 작업자·로컬 LLM·브라우저·원격 CoRA CI를 실행하지 않았다.

## 웹 답변 개발 실행 연결 — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json`은 기존 고정 혼합 노드 정책과 함께 답변·검색 실행을 선택적으로 활성화한다. 추가 정책은 `review_intake.policy_inputs`를 통과하고 `cora-recall-answer-repair-v1`을 지정해야 한다. 별도 고정하므로 경로를 활성화해도 과거 제거 정책 해시를 바꾸거나 기존 접수 기록을 승인하거나 예산을 갱신하지 않는다. 완료된 깨끗한 버전 연결의 새 보고는 `answer_dispatch.py`를 통해 운영자가 준비한 격리 체크아웃의 기존 W2/W1 실행기로 전달된다. 웹 호출자는 명령·경로·예산을 선택하지 못한다. 중복 사례 신원은 내보내기/전송/응답 ID를 제외하며 다시 내보내도 원래 기한을 유지한다. 권한 입력이 바뀌면 결정을 요구한다.

실행 연결기는 먼저 `review_replay_gate.py`로 신뢰된 재실행을 수행하고 비공개 기준 관찰을 작업 입력으로 고정한 뒤 고정 개발 계약을 준비·실행한다. `cora_review_replay.py`는 대상 체크아웃의 CoRA 네이티브 복사본 재실행 명령을 시작해 소스/검토 연결을 추가하며 대상 패키지를 가져오지 않는다. 바깥 실행 기한은 사전 확인/재실행을 포함하고 시간 초과 시 프로세스 그룹을 종료하며 내부 W1 수정 횟수는 최대 5회다. 중단된 작업을 자동 재시작하지 않는다. 내보내기에 안정된 그래프 내용 신원이 있으면 검사한다. 대화 기록이나 검증된 로컬 모델 신원이 없으면 설정을 바꾸거나 수정 완료를 주장하지 않고 차단한다.

상태 조회와 비공개 접수 화면에 개발 상태를 표시한다. 검토를 통과한 W1 후보에 승인된 내용 지문과 연결된 재실행 결과가 있을 때만 수정 후 답변을 표시하며 검토 당시 답변과 이유를 유지한다. 휴먼 재검토·의미 모호성·병합·운영 반영은 별도 결정이다. 브라우저는 검토 상태를 보존하며 새로고침이 과거 기록을 현재 승인으로 바꾸지 않는다. 재실행 관찰만으로 의미 정확성을 승인하지 않는다. 현재 통합 시험의 작업자/브라우저/CI는 합성 대체이며 실제 데이터 네이티브 재실행 시험은 실제 자율 수정과 구분한다. 이번 통합 전달에서는 실제 코드 작업자를 시작하거나 원본 그래프를 수정하지 않았다.

최종 통합 검증(2026-11-18): 컨트롤러 검사 149개가 124.938초에 통과했으며 이전 실행(136.511초)도 보존했다. CoRA 검사 533개와 1dd7608의 정확한 커밋 CI를 통과했다. HTTP 실행/W2/W1/후보 답변 시험의 작업자와 CI는 합성이며 네이티브 복사본 재실행은 실제 데이터를 사용했다. 실제 코드 작업자 실행이나 답변 오류 수정을 주장하지 않는다. 그래프 버전이 바뀌면 공유 접수기의 검토 연결을 갱신해야 한다.

## 오래된 답변 재확인과 한도 내 연결 실행 — 2026-11-19

답변 정책은 무시되는 `.local/` 아래에 고정한 계획 `revalidation_binding`과 함께 `allow_stale_revalidation`을 명시적으로 켤 수 있다. 계획 지문도 정책 권한 검증에 포함된다. 원래 검토를 보존하고 신뢰된 네이티브 재실행에서 원래 스냅샷·순번 및 계획의 의미 그래프 지문을 확인한다. 별도 현재 문맥·응답은 기존 오류 보고를 계승하며 새 사람 판단이 아니다. W1 준비 전에 현재 소스를 검증한다. LLM 요청은 명시적 제공자·모델 설정으로 LLM을 유지한다. 과거 신원이 없으면 만들어내지 않고 알 수 없다고 밝힌다. 모델 신원은 설정·파일 메타데이터이며 전체 가중치 증명이 아니다. 작업자는 코드를 바꾸기 전에 문제가 여전히 재현되는지 확인해야 한다.

`tools/continue_answer_request.py --review REVIEW_FOLDER --policy QUALITY_POLICY --answer-policy ANSWER_POLICY --request REQUEST_ID --authorization OWNER_REFERENCE`는 W1 준비·실행이 시작되지 않은 중단 사전 검사만 명시적으로 이어간다. 이전 실패를 보존하고 하위 요청을 연결하며 원래 3600초 한도에서 앞선 실행 시간을 차감한다. 반복 호출은 같은 하위 요청을 사용한다. 이미 실행된 작업은 기존 누적 상태가 필요하며 이 명령으로 초기화할 수 없다. 별도 5회 한도도 유지한다. 자동 한도 갱신이나 운영 병합은 허가하지 않는다. 웹 상태와 접수 화면은 연결 실행을 따라가며 현재 재실행과 실제 작업 단계를 표시한다.

검증은 합성 W2/W1을 통한 오래된 소스 갱신, 원래 검토 보존, 신뢰된 연결, 연결 실행의 한도·중복 방지·실행 후 거절을 다룬다. 최종 컨트롤러 전체 검사 151개가 139.071초에 통과했다. 실제 작업자 결과는 별도로 보고한다. 합성 작업자 시험은 실제 답변 수정을 입증하지 않는다.

## 게시 검토 순서 명확화 — 2026-11-19

실제 답변 수정 시험은 원래 누락을 재현하고, 실데이터 답변에 근거 있는 소유자가 포함되는 후보를 만들었다. 후보는 컨트롤러가 실행한 검사 537개·복사본 재실행·브라우저 검사를 통과했지만 의미 승인을 받거나 게시되지는 않았다. 첫 게시 검토에서 새로 추가한 비공개 절대 증거 경로를 발견해 원래 증거를 바꾸지 않고 문서에서 제거했다. 두 번째 검토는 커밋 전 작업 후보의 게시와 의미 승인·병합 권한을 혼동했다. 후보와 두 거절 기록은 비공개로 보존했고 한도를 갱신하지 않았다. 운영자의 문서 수정 1회는 같은 W1 상태에서 두 번째 회차로 계산했다. 이 시험을 완전 자동 수정 성공으로 보지 않는다.

게시 검토 프롬프트는 커밋·CI보다 앞선 단계라는 점과 미승인 전용 브랜치를 게시할 기존의 신뢰된 권한을 명시한다. CI·독립 의미 검토·사람 재시험 대기와 병합 미승인 자체는 안전하지 않은 게시를 뜻하지 않는다. 실제 개인정보·범위 문제는 계속 차단하며 안전 검토 통과도 의미 승인을 부여하지 않는다. 이 명확화는 다른 실제 검토자로 아직 검증하지 않았다. 전달 집중 검사 48개가 68.517초에 통과했다. 이 기계적 검사는 모델의 지침 준수를 입증하지 않는다.

## 개발 검토 인계 — 2026-11-26

외부 컨트롤러의 `tools/handoff_server.py`는 대기 요청 진행 상태와 버전에 묶인
수정 전후 비교를 제공하는 로컬 화면이다. 저장된 질문·수정 이유·원래 답변·후보 답변,
반환 그래프 일부·답변 항목·경로·근거를 보여준다. 그래프 배치는 표시용이다.
후보 근거가 없으면 없다고 표시한다. 기존 큐·실행기 상태를 3초마다 읽으며
작업을 새로 시작하거나 한도를 보충하지 않는다.

답변 수정 실행이 성공하면 검증된 게시 보고서와 대응 재현 결과로 비공개 불변
인계 기록을 자동 생성한다. 독립 검토와 정확한 후보·기준 버전의 CI가 통과해야 하며,
재현 요청·소스 다이제스트·스냅샷·존재하는 그래프 내용 식별자가 일치해야 한다.
연결된 자료가 바뀌면 인계를 무효화한다. 브라우저 테스트 기록은 버전에 묶이며
이력을 추가로 보존하고 최신 기록을 별도로 표시한다. 로컬 비인증 메모이므로
병합 권한을 부여하지 않는다.

`tools/delivery_handoff.py merge`는 작업자의 명시적 실행으로, 통과 테스트 기록,
사용자 승인 참조와 신뢰하는 검사 명령 인자 배열이 필요하다. 대상 체크아웃이
깨끗해야 하고 저장소, 로컬·원격 기준 버전, 원격 후보 버전이 정확히 일치해야 한다.
기록된 커밋을 병합하고 트리 일치를 확인한 뒤 병합 후 검사를 실행한다.
각 검사는 600초, 전체는 3600초 한도다. 미커밋 변경이나 버전 이동을 확인한 뒤
강제 옵션 없는 일반 푸시를 수행한다. 실패·중단된 병합은 기록되고 조용히
재시작하지 않는다. 검사 실패 시 로컬 병합을 보존하고 푸시하지 않으며,
복구는 작업자가 판단한다. 웹 서버에는 병합·명령 실행·작업 재시작 API가 없다.

사용자는 통과 테스트 후 필수·금지 답변 항목 ID를 명시해 회귀 사례로 보존할 수 있다.
사례와 데이터 연결은 비공개다. 이후 같은 입력의 후보 재현 결과는 인계 전에 이 조건을
검사하며, 다른 질문·스냅샷은 적용 대상이 아니라고 표시한다. 독립 회귀 실행 명령은
새 외부 폴더에서 신뢰하는 재현을 실행하고 소스·요청·데이터 식별자와 조건을 검사한다.
사례는 자동으로 생성한 정답이나 일반 정확도 증명이 아니다. 읽기 전용 `inspect`는
다른 방식으로 이미 병합한 작업의 Git 조상 관계를 기록한다. 새로운 승인을
만들거나 과거 전달 보고서를 다시 쓰지 않는다.

```sh
python3 tools/handoff_server.py --port 8780
python3 tools/delivery_handoff.py register --report REPORT.json --review REVIEW.json --observation REPLAY.json
python3 tools/delivery_handoff.py inspect --packet PACKET.json --target TARGET_CHECKOUT
python3 tools/delivery_handoff.py retest --packet PACKET.json --decision pass --reason 'What was tested'
python3 tools/delivery_handoff.py preserve --packet PACKET.json --required claim:STATE_ID
python3 tools/delivery_handoff.py merge --packet PACKET.json --target TARGET_CHECKOUT --approval projects/.local/merge-approvals/PACKET_ID.json
python3 tools/delivery_handoff.py regression --case CASE.json --target TARGET_CHECKOUT --command TRUSTED_REPLAY_ARGV.json --expected-head CURRENT_FULL_SHA --output .local/NEW_REGRESSION
```

인계·보고서·검토·재현 파일은 모두 컨트롤러 `.local/` 아래에 있어야 한다.
검사 파일은 명령 인자 배열들의 JSON 배열이다. 재현 파일은 새 증거 폴더를 나타내는
`{output}`이 들어간 명령 인자 배열이며 `review-replay.json`을 생성해야 한다.
브라우저 메모에서 셸 명령을 받지 않는다. 소스·검토·CI 검사는 기존의 한도 있는
실행기가 담당한다. 백그라운드 스케줄러·금액 계측·임의의 다음 목표 선택은 추가하지
않았다. 이번 전달은 CoRA 코드와 원본 데이터를 바꾸지 않는다. 로컬 사용자는
비공개 증거에 접근할 수 있으며, 루프백·세션 보호는 다중 사용자 인증이나 운영체제
격리가 아니다. 화면의 승인 인계 범위는 답변 수정이다. 도메인 그래프 수정은
기존 복사본 결과와 별도 적용 정책을 유지한다.

### 신뢰 경계와 검증 세부 사항

인계 등록은 기존 재현 게이트의 전체 검증기를 재사용한다. 정확한 선택 레코드의
바이트, 응답의 질문·설정, 추적과 그래프 버전을 확인한다. 불변 보고서 식별자를
컨트롤러 상태, 소스에 묶인 실제 검사·검토 기록, 고정된 프로젝트·계약의 기준과
CI 게이트에 대조하며 설정된 브라우저 증거도 확인한다. 같은 증거 파일을 인계에
고정한다. 성공처럼 보이는 JSON을 임의로 만드는 것만으로는 충분하지 않다.

작업자는 실제 사용자 결정을 먼저 `authorize`로 기록한다. 이 명령은 신뢰하는
`projects/.local/` 아래에 버전·대상·검사에 묶인 불변 승인 파일을 만든다.
`merge`는 자유 형식 승인 문구 대신 그 파일을 사용하며, 대상 변경 전에 컨트롤러와
보호된 작업 입력도 재확인한다. 이는 작업자의 확인 기록이며 인간의 신원을
인증하지는 않는다. 검토 문구와 웹 메모로는 이 기록을 만들 수 없으며 작업자가
사용자 승인을 만들어내서는 안 된다. Git 호출은 60초 한도이며 병합 후 검사는
개별·누적 시간 한도를 유지한다.

```sh
python3 tools/delivery_handoff.py authorize --packet PACKET.json --target TARGET_CHECKOUT --reference 'Actual owner decision reference' --checks TRUSTED_CHECKS.json
python3 tools/delivery_handoff.py merge --packet PACKET.json --target TARGET_CHECKOUT --approval projects/.local/merge-approvals/PACKET_ID.json
```

회귀 사례는 과거 커밋에 영구 고정하지 않고 이후 버전에서도 실행하는 것이 목적이다.
기원 SHA·다이제스트를 보존하고, 매 실행은 `--expected-head CURRENT_FULL_SHA`,
깨끗한 체크아웃, 변경되지 않은 소스, 정확한 검토 바이트와 추적을 포함한 재현을
요구한다. 신뢰하는 재현 인자에는 `{review}`와 `{output}`이 모두 있어야 한다.
이번 소스 식별자는 새 관찰 결과에 대조하며 과거 사례의 소스 식별자로 대체하지 않는다.

신뢰하는 품질 접수 정책의 선택 항목 `handoff_console_url`로 루프백 화면 주소를
설정한다. 기존 접수 내역 화면이 이 주소로 연결하며, 상대 경로인 결과 URL은
CoRA 중계와 계속 호환된다. 비활성 예제에 이 항목을 포함했다. 이번 전달은
과거 실행 권한을 갱신하거나 정책을 대체하지 않는다. 새로운 승인 범위에는
명시적으로 설정한 접수 실행기를 사용한다.

`register --historical-only`는 과거 비교를 가져오되 테스트 통과·회귀 사례 채택·병합
권한을 부여하지 않는다. 실제 증거 재확인 실패를 기록하며 Git에서 병합을 확인해도
읽기 전용이다. 현재 EMNLP 비교는 이 모드다. 과거 브라우저 검사 폴더의 현재
파일 목록이 기록된 목록과 일치하지 않기 때문이다. 과거 보고서·증거·승인을
다시 쓰지 않았다.

### 전달 검증 — 2026-11-26

구현된 후보 상태다. 최종 로컬 전체 검사 **165개가 129.383초에 통과**했다.
인계 집중 검사 13개는 실제 임시 Git 병합·푸시, 검사 실패 시 푸시 차단,
버전·승인 변경, 재현 자료 오류와 HTTP 경계를 다룬다. 실제 CUA에서 저장된
EMNLP 전후 비교를 확인했고, 별도로 합성 사례라고 표시한 화면에서 테스트 기록,
회귀 조건 선택·보존, 새로고침 후 복원을 확인했다. 새로운 실데이터 수정 실행은 아니다.
독립 재검토는 최초의 연결·권한 지적이 수정됐음을 확인했으며, 심볼릭 링크 재현
증거를 거부한 뒤 마지막 집중 검토도 통과했다. 추가한 푸시 CI는 게시 버전에서
전체 검사를 다시 실행한다. CoRA 구현·원본 그래프·과거 실행 권한은 변경하지 않았다.

원격 CI는 Python 3.9를 위해 Ubuntu 22.04를 사용한다. 최초 Ubuntu 26.04
환경은 Python 3.9 설치 단계에서 실패해 검사를 실행하지 못했고 실패 기록을 보존했다.
실행 환경만 고정했으며 전체 검사 명령은 바꾸지 않았다.

## 자동 품질 개선 구현 — 2026-11-26

실험적 컨트롤러 구성 요소를 구현했다. `quality_improvement.py`는 지속되는 단계·회차·마감·
검증 조건을, `quality_agent_stage.py`는 컨트롤러 소유 스키마를 사용하는 설치된 에이전트의
역할을, `quality_topic_evaluate.py`는 대상 패키지를 가져오지 않는 CoRA 하위 프로세스 평가를
담당한다. 토픽 수정 범위 계약·비활성 비공개 설정 예제·고정 사례 목록·일반 검토 지적의 반복
전달·보호 입력과 정확한 소스 검사·회귀/보류 차단·누적 한도·오래된 후보 무효화·관찰된 모델/제공자 연결·종료 상태 중복
방지를 추가했다. CoRA 구현·원본 데이터·실제 검토 pool은 변경하지 않았다.

실제 평가 기록 접수는 원문 30개·원문 근거 관련 오류가 있는 원문 17개이며 비공개 분석으로
보존했다. `root_cause_proven=false`, `semantic_quality_accepted=false`를 유지한다. 실제
모델 작업자·독립 에이전트 검토·실제 수정 전후 품질 승인·설치된 수신기·작업자 후보 게시·자동
병합은 실행하지 않았다. 템플릿은 실행 권한 갱신이 아니다. 더 강한 의미 정답·원문 맥락·로컬
모델 기능을 보호된 설정으로 공급해야 한다. JSON만으로 에이전트의 인과 추론이 옳다고 증명할
수 없으며 사람 재시험을 대체하지 않는다.

구현 소스에서 입력 소유권·소스/버전 연결·정답/사례 보존·프로세스 그룹 마감·재호출 한도·
읽기 전용 단계를 검토했다. 독립 실제 검토는 대기 상태이며 실험 브랜치 전달이다. 최종 결정적
검증은 아래에 기록한다. 전체 상태 전이와 운영 한계는 `quality-improvement-protocol.md`를
참고한다.

### 프로토콜 전달 검증

최초 프로토콜 컨트롤러 전체 검사 **181개가 143.007초에 통과**했다. 새 프로토콜/연결기 집중 검사
**16개가 13.915초에 통과**했다. 집중 검사는 합성 수정→재시험 전체 흐름, 검토 지적의 자동
재시도, 사례/정답 변조, 의미 결정, 범위 밖 변경, 검토자의 변경, 회귀, 실패를 보류로 숨김,
시간/회차 집계, 예산 갱신 금지, 중단 단계 재실행 거절, 오래된 후보 무효화, 관찰한 모델 변경,
사례/소스 연결과 에이전트 실행 모드 구성을 다룬다. 앞선 전체 검사 179/180개도 통과했으나
중간 버전의 과거 결과다. 통과를 위해 승인 기준이나 정답을 바꾸지 않았다. JSON 스키마/설정과
영문·한국어 소스 문서를 검토했고 `git diff --check`가 통과했다. Push CI는 별도 기계적 검사이며
실제 독립 의미 검토를 대체하지 않는다.

### 증거 무결성 후속 보완

최종 소스는 단계별 전체 파일 목록·해시를 기록하고 이후 단계와 사람 재시험 전에 다시 대조한다.
입력·로그·원본 평가/에이전트 출력의 수정, 파일 누락·추가·심볼릭 링크는 후보를 무효화한다.
결과 해시를 저장만 하고 다시 대조하지 않던 소스 검토 지적을 보완했다. 집중 검사 **17개가
16.596초**, 최종 전체 검사 **182개가 144.462초에 통과**했다. 추가 회귀 검사는 준비 완료 뒤
과거 기준 버전 로그를 바꾸면 동일 작업이 예산 갱신 없이 decision_required로 바뀌는지 확인한다.
최초 게시 버전 e699734는 원격 CI를 통과했다. 후속 보완에는 별도의 정확한 게시 버전 CI가
적용된다. 독립적인 실제 의미 검토와 실제 모델 수정은 여전히 미검증이다.

### 실제 실험 시간 제한 설정 — 2026-11-26

단계별 제한은 최대 3600초까지 설정할 수 있다. 각 명령은 계속 누적 실험의 남은 시간으로 제한되며, 시간이나 수정 횟수를 갱신하지 않는다. 사용자 승인 60분 실험 안에서 고정 원문 30개 평가를 완료할 수 있도록 한다.

### 무인 토픽 실험 — 2026-11-26

사용자가 승인한 실제 실험을 CoRA `fc832b79a15c3149e23ae2bae7cd1280079848aa`의 별도 작업 공간에서 누적 60분·5회 한도로 실행했다. 고정 합성 사례 8개와 실제 원문 30개의 결과는 통과 20개, 실패 18개였다. 실제 원문의 오류는 활동 이름 인용 실패 8건, 원문 근거 검증 실패 7건, 식별 이름 인용 실패 2건이었다. 실제 원문의 처리 성공은 의미 정확성의 입증이 아니다.

설치된 에이전트가 별도의 읽기 전용 진단을 완료하고 고객 업무의 대표 이름 정책에 대한 사용자 결정을 요청했다. 원문의 긴 표현과 보호된 짧은 예상 이름 모두 원문 근거가 있지만 설계에 공통 핵심 이름 규칙이 없기 때문이다. 실험은 수정·후보 재평가·별도 후보 검토 전에 `decision_required`로 중단됐다. 진단 주기 1회를 사용했으며 실제 수정은 적용하지 않았다. 원래 마감 시각과 비공개 증거 전체는 보존된다. 대상 commit·병합·활성 pool 교체·원본 그래프 변경은 없었다. 정책 질문의 답변 자체가 실행 예산 갱신을 뜻하지는 않는다.

검증: 실행기 집중 검사 18개 통과(16.366초), 전체 검사 183개 통과(162.208초), 변경 없는 CoRA 기준 검사 587개 통과(20.35초). 시간 제한 지원 버전 `4d02081ae892a7cd1df8e670c6bb6fdca7c844ba`의 push CI가 통과했다. 비공개 실행 증거는 무시된 `.local/quality-improvement/topic-unattended-20261126/`에 보관한다. 이 결과는 실패 재현과 결정 요청이며, 수정 완료나 품질 승인이 아니다.

### 사용자 승인 토픽 의미 평가 — 2026-11-27

CoRA 자체 평가기는 이제 `semanticVersion: 1`과 원문 기반 `semanticStatus`(`pass`, `fail`, `needs_review`)를 보고한다. 실행기는 진단용 `exactMatch` 대신 이 판정을 사용한다. 모호함은 `deferred`로 전달하며 전체 승인 조건을 충족하지 못한다. 의미 평가 사례를 기존 정확 일치 판정으로 대체하지 않는다. 평가 모델 응답의 식별 정보도 관측 모델 고정 검사에 포함하며 예제 정책은 기존 사례·평가 명령과 함께 새 의미 평가기를 보호한다.

이는 사용자가 명시적으로 승인한 평가 정책 변경이며 작업자가 통과하려고 정답을 바꾼 것이 아니다. 과거 실패 실험·원문·진단용 예상 이름은 유지한다. 새 의미 대상 설명은 대상·활동·범위와 보호된 명시적 식별 정보를 정의한다. 새 실험에는 새 고정 예상 기준이 필요하며 과거 종료 상태와 사용 예산은 초기화하지 않는다. 같은 로컬 모델의 별도 호출은 독립적인 사람의 의미 검증이 아니다. 자동 병합·그래프 승인·과거 실제 원문 오류 17건의 수정을 주장하지 않는다.

검증: 실행기 전체 검사 **184개 통과**, 최종 모델 식별 고정 변경 후 품질·연결 집중 검사 **19개 통과(17.307초)**. CoRA `5540e8f`는 회귀 검사 596개와 실제 합성 의미 평가 8개를 통과했다. 고객 업무의 이름 정확 일치 진단은 false를 유지하고 의미 판정은 통과했다. 새로운 원문 30개 무인 수정 실험은 실행하지 않았다.

### 실제 원문 수정 재실험 결과 — 2026-11-27

사용자가 승인한 새 60분·5회 실험에서 의미 사례와 동일 원문 30개를 고정했다. 기준 결과는 통과 21개·실패 17개이며 합성 사례 8개는 모두 통과했다. 읽기 전용 작업자는 실제 의미 정답 부재를 원문 형식 수정까지 막는 사유로 보아 결정 요청으로 중단했고, 임시 파일을 만들 수 없어 pytest 시도도 실패했다. 상위 감독은 보호된 예상 기준·검증기를 바꾸지 않고 기존 허용 범위인 제한적 prompt-format 수정을 선택했다. 이 개입은 무인 운영의 성공으로 계산하지 않는다. 최초 실험과 권한 기록은 유지했다.

감독 후보 주기 2회는 최초 마감 시각을 사용했으며 진단 포함 총 3회였다. 첫 후보는 식별 `reason` 누락으로 취미 회귀가 발생해 평가를 중단했다. 다음 후보는 필수 필드를 명시하고 CoRA 회귀 검사 602개를 통과했지만 실제 평가는 누적 마감 전에 합성 사례 4개만 완료했다. 프로젝트는 빈 식별 응답으로 실패하고 나머지 3개는 통과했다. 감독 후속 실행은 `budget_exhausted`다. 최종 동일 원문 후보 비교·독립 후보 검토·의미 승인·병합은 없었으며 원문 오류 17건은 수정 검증되지 않았다. 부분·실패 증거는 무시된 `.local/quality-improvement/topic-runtime-retrial-20261127/`에 보존한다. CoRA 실험 후보 `171ab3a`는 수락되지 않았다. 추가 30분은 요청했지만 중단 시점에 승인되지 않았으며 마감이나 횟수를 초기화하지 않았다.
