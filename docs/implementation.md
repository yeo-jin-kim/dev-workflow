# Controller separation implementation record

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
