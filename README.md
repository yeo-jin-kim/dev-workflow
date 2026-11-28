<!-- document-language: en -->
# dev-workflow

Independent local development orchestration. Target repositories do not import
or depend on this repository. Python 3.9+ on macOS/Linux; standard library only.

## Usage

Run from this repository (the script resolves defaults from its own location):

```sh
python3 tools/development_loop.py status --project projects/cora.json
python3 tools/development_loop.py run --project projects/cora.json --max-cycles 3 --total-seconds 1800
python3 -m unittest discover -s tests -q
```

`run` invokes the installed/authenticated Codex CLI and executes trusted contract
checks in the target checkout. Default model settings are preserved. The project files still point to historical F1; F1 has since completed and merged.
Select an explicit new authorized contract/isolated target before a new run; the
example command is not a newly selected goal. `pilot.json` is historical.

## Layout

- `tools/`: project-independent runner.
- `schemas/`: worker/reviewer output contracts.
- `projects/`: target root and project-specific policy/decision references.
- `contracts/<project>/`: approved goal, scope, checks, acceptance criteria.
- `.local/runs/`: durable state, subprocess logs, check and review results (ignored).
- `.local/archive/`: original historical run artifacts and migration checksums (ignored).
- `docs/implementation.md`: behavior, verification and remaining limitations.

Project root paths are relative to this repository unless absolute. Check command
arguments run relative to the target root. The project policy and decision paths
are target-relative. Add another project configuration/contract without importing
its source code into the controller. A contract cannot redefine the mandatory
`documentation_sync` review criterion. Missing/failed evidence blocks completion.

The worker uses the target as its workspace-write root; the separate reviewer
uses read-only mode. Schemas, contracts and output files are controller-owned.
Locks cover target identity across milestone runs. Target/controller trees must
be disjoint, and state must remain external. Reusing state after target or
controller changes is rejected; start a new state directory. Human decisions
remain pending until explicitly resolved in a new contract/state directory.

## Boundaries and limitations

This is path/ownership separation plus CLI workspace sandboxing, not a proof of
OS-level isolation. Local checks execute with the controller user's permissions;
use trusted checks. Protect the controller from target scripts, symlink attacks,
and arbitrary external commands with stronger OS/CI isolation before unattended
operation. Target code cannot legitimately edit contracts, controller or logs.
The legacy runner has per-invocation limits; the opt-in W1 runner persists
cumulative deadlines/cycles. Monetary budgets, installed background scheduling, notifications, next-goal
selection are not implemented. A local human-retest console is implemented below; merge authorization remains an explicit operator action. W2 adds bounded
owner-approved queue dispatch; its workflow and limits are described below.
No target merge/deploy is automatically authorized. W1 publication is limited
to the explicitly configured task repository/branch and reviewed task files.

The preserved archive is historical: original state files contain old absolute
paths. Do not resume them or rewrite their evidence. See migration.json.

## CoRA F1 history and current next milestone

F1 completed synthetic verification and merged in
[CoRA PR #1](https://github.com/yeo-jin-kim/cora/pull/1) to
`codex/workflow-foundation` (`fe4aac5`). Parent intervention supplied browser,
review/publication handoffs and a CI prerequisite fix; this was not a fully
unattended run. Its contracts and run histories remain preserved.

W1 revision 2 has an **opt-in verified implementation: 18/18 scenarios, 63 tests and all 12 final independent-review criteria passed**:
[task contract](contracts/dev-workflow/W1-reviewable-delivery.md),
[design and status](docs/01-reviewable-delivery-design.md).
`tools/delivery_loop.py` adds actual Chrome execution, version-bound evidence,
durable repair/review, dedicated-branch commit/push, exact-head push CI and a
versioned merge-decision report. No PR is created and target merge remains an
explicit owner action. The legacy runner and its historical states are unchanged.

```sh
python3 tools/delivery_loop.py run --project projects/cora-w1-pilot-v2.json --state-dir /ABSOLUTE/EXTERNAL/RUN --max-cycles 3 --total-seconds 3600
python3 tools/delivery_loop.py status --project projects/cora-w1-pilot-v2.json --state-dir /ABSOLUTE/EXTERNAL/RUN
```

The shown invocation is historical: its three-cycle allowance is exhausted.
Do not use another state directory to replenish it. The owner subsequently authorized one additional 30-minute/three-cycle trial;
that allowance is also exhausted without live acceptance. A further real pilot
needs explicit owner budget authorization. The linked v2 pilot config preserves the
original failed trial and its cumulative budget (see the implementation record). It is opt-in and host-specific (existing Chrome and CoRA Python
test environment). Use the implementation checkout described in the design.
Do not run against the original/dirty checkout or the controller itself. `status`
reports a historical snapshot; `run` rechecks current inputs/remote state, honors
persisted cumulative limits and refuses pending decisions. Browser, reviewer or
GitHub capability failures remain incomplete with actionable evidence; no manual
result-copy shortcut qualifies as unattended success. New dependencies are not
installed by the runner. Live-pilot/final-review results are recorded in
`docs/implementation.md`; do not infer completion from code presence.

## Delivery publication policy

The owner requests commit/push after each delivery. The maintaining parent
performs finalization after checking results. Incomplete milestones are pushed
to dedicated branches with their failed/missing gates stated, never merged or
reported accepted merely because they were published. Private .local logs stay
excluded; implementation workers do not push during their runs.

F1 synthetic evidence verification is available through `tools/evaluate_f1.py`.
It checks protected definitions, recorded source fingerprints and actual browser
results; see `docs/implementation.md`. Evidence completion does not bypass the
independent review gate.


The owner approved a further bounded 60-minute/five-cycle actual trial, recorded
in `projects/cora-w1-approved-trial-60m.json`. Its first review hit a phase cap;
the recovery profile preserves the same deadline/consumed cycles and guarded
missing-review evidence. This does not automatically renew either trial's budget.
The recovery reached `ready_for_merge_approval` at CoRA `81b1e21`, using two cumulative cycles with the original deadline. Its actual checks, Chrome, independent review, automatic commit/push, exact-head push CI and report passed; no PR or merge. Bootstrap repairs and prior failures remain recorded in the implementation record.

The bounded recovery milestone passed final W1 evaluation and independent audit.
It remains a constrained browser/kernel pilot, not general semantic or full UI
certification. Dedicated branches are pushed; actual merging is owner-gated.

## W2 approved task queue

`tools/approved_queue.py` drains an explicitly owner-approved W1 task queue in
order, with dependency checks, separate worktrees/heads, durable queue/repository
reservation caps and a fixed execution window. It keeps W1 checks, independent
review, actual browser, exact-head push CI and branch/report delivery. Each merge
still needs owner authorization. See [design and operator workflow](docs/02-approved-queue-design.md)
and the deliberately unconfigured [example](queues/example.json).

Approval receipts bind exact queue/project/contract/authority files and clean
target HEAD/content/branch plus observed remote base. `run` never
automatically approves a proposal. Repeat runs reconcile complete receipts but
stop ambiguous interrupted dispatch instead of replaying it. Reservations are
conservative, never refunded; separately approved queues do not share a monetary
or rolling daily meter. This is a foreground bounded drain, not an installed
background scheduler. No new CoRA work is selected or authorized by the example.

W2 handoff freshness is a timestamped remote observation. Cooperative local locks
cover engine/verification/checkpoints; external writers and future remote changes
are not locked. Revalidate exact refs before any owner-authorized merge.

W2 implementation validation: **94 tests passed**, including 31 queue cases;
independent final source review passed all eight criteria. No live queue approval,
background scheduler or merge was created as part of implementation.


## Documentation languages

All human-readable Markdown documents use a complete English version first,
followed by the complete Korean translation. Update both in the same change.
Commands, identifiers and machine-readable evidence retain their original values.
JSON contracts/schemas and immutable historical run artifacts are not duplicated
or rewritten. Future merge-decision Markdown reports follow the same language
order and quote original machine fields explicitly as evidence.

---


## Review-file repair intake

`tools/review_intake.py` accepts one explicitly selected private review export and
uses a trusted enabled policy to prepare/start one bounded W2→W1 repair. It pins
reviewed commit/source, preserves original bytes, refuses duplicates/drift/state
loss and ends at human retest. Existing independent review/browser/CI gates stay.
Examples are disabled; a project-specific trusted real-data replay check is required.
No watcher, active policy or new CoRA repair was installed. See
[guide](docs/03-review-json-intake.md).

## Data quality trials — 2026-11-12

An explicit copy-only data quality pipeline is available; see [the guide](docs/data-quality-workflow.md). It detects, optionally invokes fixed-scope W1 code repair, tests isolated graph changes and stops for owner review; source ambiguity blocks repair. No scheduler or original graph application is enabled.

## Review request intake — 2026-11-15

Review pages can submit changes_requested directly to an opt-in local intake with session token, Host/Origin checks, durable deduplication, status/result links and fixed copy-only repair contracts. See [the guide](docs/data-quality-workflow.md); generic code editing and production application are not enabled by browser notes.

## Recall-centered repair review — 2026-11-15

Submit review feedback from the existing CoRA Real-data Recall page. The quality page is a readable result/diagnostic view; source-thread IDs are details. Answer issues outside the configured removal contract are saved for scope review, never executed as removals. See docs/data-quality-workflow.md.


## Review transport correction — 2026-11-15

Real Recall traces can exceed the previous 256 KiB intake limit. Both optional relay and external intake now accept bounded JSON requests up to 8 MiB, preserving the complete review record. Relay failures return JSON; the UI reports non-JSON service responses without discarding the current judgment. Scope, authorization and original-graph restrictions are unchanged. Regression checks cover a 300 KB synthetic review and JSON relay rejection; these do not establish model answer accuracy.


## Answer/retrieval development contract — 2026-11-15

Added `contracts/cora/recall-answer-repair.json` with its bilingual guide and disabled `projects/cora-recall-answer-{repair,intake}.example.json` configuration templates. It uses the existing private review intake and W2/W1 code-development pipeline, distinct from fixed graph removal. Criteria require exact-baseline reproduction, justified expected behavior, synthetic baseline failure/candidate pass, negative neighbors, original-case before/after replay, independent review, documentation, human retest and exact-head CI. The Me omission report does not itself establish that Me belongs in the answer.

`execution_limits` freeze 3600 seconds/five cycles; both review-policy loading and direct W1 initialization reject excess before new state. Historical contracts without these fields retain prior behavior. Replay binding now includes conversation metadata. This delivery adds a contract and executable guard behavior, not a live CoRA repair: web answer reports still stage for scope review, disabled examples do not dispatch, and a concrete pinned real-data replay adapter remains required. Existing requests, mixed-node policy, prior budgets and original graphs are untouched. See `contracts/cora/recall-answer-repair.md`.


## Web answer-development dispatch — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json` optionally enables answer/retrieval dispatch alongside the unchanged fixed mixed-node policy. The additional policy must pass `review_intake.policy_inputs` and name `cora-recall-answer-repair-v1`. It is pinned separately, so enabling the route does not alter the old removal policy hash, authorize old staged reports or renew their budgets. New completed, clean/version-bound reports are dispatched through `answer_dispatch.py` to the existing W2/W1 engine in an operator-provisioned isolated checkout. The web caller cannot choose commands, paths or budget. Duplicate case identity ignores export/transport/response IDs and preserves the original deadline even after another export; changed authority requires a decision.

The dispatcher first invokes a trusted replay through `review_replay_gate.py`, pins that private baseline observation into the task, then prepares/runs the frozen development contract. `cora_review_replay.py` launches CoRA's native copy-only replay command from the target checkout, wraps source/review bindings and imports no target package. The outer execution deadline includes preflight/replay and terminates the process group on timeout; internal W1 cycles remain capped at five. Interrupted jobs are not automatically restarted. Stable graph content is checked when exported. Missing history or verified local-model identity blocks rather than changing settings or claiming correction.

Status and the private feedback page show development state. Only a successfully reviewed W1 candidate with a bound replay for its accepted digest exposes an after-answer; the original reviewed answer and reason remain visible. Human retest, semantic ambiguity, merge and production installation remain separate decisions. The browser retains review state; refreshing does not turn an old record into current authorization. A replay observation alone is not semantic acceptance. Current integration tests use synthetic worker/browser/CI fixtures; a real-data native replay probe is separate from an actual autonomous repair. No actual coding worker or original graph modification was started in this integration delivery.


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

## Automatic quality improvement protocol — experimental

`tools/quality_improvement.py` adds bounded reproduction, causal diagnosis, repair,
fixed-case evaluation and separate review. Review feedback is automatically passed
to another attempt; regression, hidden failures, two non-accepted attempts and owner
boundaries are preserved. Successful candidates stop at human retest, without automatic
publication or merge. Stable episode IDs retain cumulative limits and interrupted runs.

The CoRA evaluator adapter combines frozen synthetic labels with real-source runtime
checks; runtime success is not semantic accuracy. The installed agent adapter uses
separate read-only diagnosis/review and bounded writable repair. It preserves default
model settings. The disabled example policy and topic contract need trusted local
paths, protected inputs and an actual scope/budget reference before live execution.
No scheduler or current-model repair was activated. Current captured CoRA results
were ingested: 30 sources, 17 with failures, still not proven causal diagnoses or gold.
See [protocol and operating instructions](docs/quality-improvement-protocol.md).


Prior step inputs, logs and result files are hashed and rechecked before later phases and human retest; changed evidence invalidates the candidate.


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


### Approved extension completed without acceptance — 2026-11-27

Owner approval added 30 minutes while retaining five total cycles; consumed authority is now 90 minutes/five cycles. The original episode and each failed/partial attempt remain immutable. Cycle 4 restored the baseline first-call prompt and passed 602 tests/8 synthetic cases, but partial real-source states showed no improvement and preliminary review found a potential identity switch. Cycle 5 added preservation of already-grounded identity values, a separate same-target check, exact field-specific repair feedback and adversarial regression cases.

Final evidence: CoRA `9485160`, **607 tests passed (21.34s)**; **8/8** synthetic semantic cases passed; **30/30** fixed original sources evaluated. Processing-error sources decreased **17 → 13** (38-case operational pass 21 → 25, fail 17 → 13; no case-level processing regressions). Accepted outcomes increased 14 → 17 and needs_scope 4 → 6. Case-level runtime scoring treats normal deferral as operational completion; private item-level audit records new deferrals separately, which cannot qualify semantic repair.

The candidate is not accepted: parent inspection found a reviewer notification promoted to an authored-submission candidate. Final independent review timed out with no verdict; preliminary review requested changes, and no final pass is implied by addressing its source-guard finding. All five cycles are used. No merge, canonical graph mutation or active-pool replacement occurred. Native evidence, comparison, explicit extension authority and `final-outcome.json` are under ignored `.local/quality-improvement/topic-runtime-retrial-20261127/`. Final status is budget_exhausted with thirteen processing failures and a semantic role blocker. Next priority requires source-backed owner-role/authorship validation and another explicitly approved allowance, not a silent retry/reset. This was supervised recovery after an automatic diagnostic stop, not a successful unattended closed loop.


### Contextual interpretation outcomes — 2026-11-27

CoRA supplies context-generated alternatives/conditions/questions and exact-source assessment records before topic pool insertion (design/16 in the target repository). The controller remains independent and imports no target modules. Runtime grading v2 maps `needs_scope`, `interpretation_deferred` and `interpretation_revision_required` to `deferred`, including mixed accepted/unresolved batches; they are neither verified fixes nor code failures. Invalid contextual review remains a processing failure. A baseline with no failure stops at `needs_context` if unresolved or `no_repair_needed` if fully passing, without invoking a development worker. Both terminal records retain integrity checks; they do not approve merge or Knowledge. Existing fail-to-deferred anti-hiding checks remain in force.

The optional `context_fixtures` profile field adds frozen `context:` cases through the native contextual evaluator; missing or duplicate coverage fails closed, and evaluator/model identities are preserved. The example contract allows contextual implementation/test/design fixes while protecting contextual fixtures and evaluation commands. Runtime v2 changes case expectation digests: create a fresh registry rather than reuse/rewrite historical experiments. No automatic execution, budget renewal, model training, cross-event retrieval or publication is introduced. The previous 90-minute/five-cycle experiment remains exhausted and unaccepted. This is a new owner-requested implementation, not an extension/reset of that experiment.

Validation: controller full suite **188 tests passed**; final focused suite **23 tests passed (23.393s)**. CoRA integration passed **634 tests** and a bounded four-case local-model pilot met unchanged primary-selection expectations. Uncertain original-source roles remained deferred; these results do not certify general semantic accuracy or resolve the prior 13 processing failures. Independent delivery review is pending; no merge or old-episode renewal.

Final provenance-bound repeat: CoRA **634 tests passed (21.26s)**, controller **188 tests passed (148.184s)**, unchanged four-case primary-selection pilot **4/4 passed**. The controller deadline-error attempt remains preserved; a clean full repeat passed without code or test-budget changes. Test logs and model output are bound to file hashes before/after execution. This is prototype delivery evidence, not merge approval or general semantic certification.

Delivery review completed: the separate read-only follow-up passed all five criteria with no blockers or decision requests. Earlier requested changes and failed checks remain preserved. This final status annotation changes documentation only; publication and merge are distinct gates.

### Cross-source context evaluation — 2026-11-28

The target now performs bounded original-source lookup inside its current entity
snapshot before contextual assessment; its native topic evaluator narrows lookup
to its frozen manifest only. This controller imports no target code and changes
no execution budget. Optional `additional_context_fixtures` paths append protected
source-linkage cases to the existing `context_fixtures` set through native
`--additional-fixtures` arguments. All old case digests remain unchanged; duplicate
IDs, omitted cases and extras without a primary fixture are rejected. New case
sets require a new frozen registry, not restarting/regrading old episodes.

Templates enumerate the new retrieval module/test and protect the new synthetic
source-context fixture. Incomplete related-source lookup remains normal context
`deferred`; its sources do not add pool hits. Missing/invalid model or processing
results remain failures under the unchanged anti-hiding protocol. Evaluation cases
can test conservative non-adoption, but neither the controller nor model certifies
semantic truth. Graph traversal, alternative rewriting, original source/graph
mutation and new repair-episode execution remain outside this delivery. The new
read-only review contract is `contracts/quality/contextual-source-retrieval.json`.
Actual extension validation is pending; previous 188-test results are historical.

Extension regression: controller **190 tests passed (139.761s)**, including unchanged old case digests, required coverage for additional cases and rejection of duplicates/missing primary fixtures. The target preserves failed positive-model cases as failures; ordinary context deferral is not credited as a positive semantic fix. No old episode or execution budget was renewed.

Extension validation — 2026-11-28: hash-bound CoRA **663 tests passed (22.47s)**;
controller **190 tests passed (139.761s)**. Final local Gemma pilot **5/5** met the
unchanged primary-selection expectations, including actual participation supported
by a linked original and no authorship promotion from a different submission
edition. The positive case used separate link/hypothesis assessments. Three earlier
pilots (4/5, 3/5, 4/5) remain failures in private evidence, not retroactively passed.
The source-bound real lookup probe retained three complete originals from 242 other
matching cues in a 3,840-event snapshot and recorded 239 unexamined; this is lookup
verification, not semantic accuracy. UI source inspection, JavaScript syntax and
diff formatting passed; browser interaction and active-preview replacement were
not performed. Independent read-only delivery review is pending. Existing 13-source
processing failures were not rerun or claimed fixed. No source/graph write, old
repair budget renewal, automatic rewriting, PR or merge.

Final delivery candidate — 2026-11-28: **664 CoRA tests passed (22.73s)** and
**190 controller tests passed (139.761s)**. After the native gold-isolation fix,
the unchanged five-case model suite again passed **5/5** on the fully bound
candidate. The existing ordinary synthetic gold cases now have no companion
corpus: they are independent worlds even if names coincide. Real evaluation uses
only its manifest; explicit cross-source fixtures supply their own companion set.
The CLI integration test verifies this distinction without claiming model accuracy.
Final real lookup again resolved three originals and reported 239 unexamined.

The first independent review timed out without a verdict; it is not a pass.
A concise read-only follow-up is pending. Earlier test/model failures and review
output are preserved. This extension runs only after existing extraction,
identity and semantic gates; it does not rescue an upstream `no_subject` or
semantic rejection automatically. Active preview, graph data and old repair
limits remain unchanged; graph traversal and alternative rewriting are deferred.

Post-review validation — 2026-11-28: after the primary-time correction, bound CoRA
regression **678 passed (23.44s)** and the unchanged model suite again passed
**5/5**. Controller code still matches its **190-test** bound evidence. Actual
source lookup remains three retained originals/239 unexamined. The fourteen new
invalid-primary-time cases include empty and nonmatching explicit corpora. No
companion records means no cross-source query is requested; ordinary single-source
claims retain their previous behavior without claiming temporal corroboration.
The independent correction request remains preserved; targeted follow-up is
pending. No original data, graph, expected labels, thresholds or old episode limits
changed.

Delivery review completed — 2026-11-28: independent read-only follow-up passed all five criteria with no blockers or owner decisions. Earlier timeouts, requested correction and failed pilots remain preserved. This status annotation changes documentation only; commit/push is branch delivery, not merge or semantic adoption.

<!-- document-language: ko -->
# 한국어 번역

# dev-workflow

독립적인 로컬 개발 실행 제어 저장소다. 대상 프로젝트는 이 저장소를 가져오거나
의존하지 않는다. macOS/Linux의 Python 3.9+와 표준 라이브러리만 사용한다.

## 사용법

이 저장소에서 실행한다. 스크립트는 자신의 위치를 기준으로 기본값을 찾는다.

```sh
python3 tools/development_loop.py status --project projects/cora.json
python3 tools/development_loop.py run --project projects/cora.json --max-cycles 3 --total-seconds 1800
python3 -m unittest discover -s tests -q
```

`run`은 설치·인증된 Codex CLI를 호출하고 대상 체크아웃에서 신뢰된 계약 검사를 실행한다.
기본 모델 설정은 유지한다. 프로젝트 파일은 여전히 과거 F1을 가리키며 F1은 이후 완료·병합됐다.
새 실행 전에는 명시적으로 승인된 새 계약/분리 대상을 선택한다. 예제 명령이 새 목표를
선택하는 것은 아니다. `pilot.json`은 과거 기록이다.

## 구성

- `tools/`: 프로젝트와 독립된 실행기.
- `schemas/`: 작업자/검토자 출력 계약.
- `projects/`: 대상 루트와 프로젝트별 정책/결정 참조.
- `contracts/<project>/`: 승인된 목표·범위·검사·수용 기준.
- `.local/runs/`: 영속 상태·자식 프로세스 로그·검사/검토 결과. Git에서 제외한다.
- `.local/archive/`: 원래 과거 실행 자료와 이전 검증용 체크섬. Git에서 제외한다.
- `docs/implementation.md`: 동작·검증·남은 한계.

프로젝트 루트는 절대 경로가 아니면 이 저장소 기준이다. 검사 명령 인자는 대상 루트에서
실행한다. 프로젝트 정책/결정 경로는 대상 기준이다. 대상 소스를 컨트롤러로 가져오지 않고
프로젝트 설정/계약을 추가할 수 있다. 계약은 필수 `documentation_sync` 검토 기준을
재정의할 수 없다. 증거 누락·실패는 완료를 막는다.

작업자는 대상을 workspace-write 루트로 사용하고 별도 검토자는 read-only 모드를 사용한다.
스키마·계약·출력 파일은 컨트롤러가 소유한다. 잠금은 마일스톤 실행 사이에도 대상 식별값을
보호한다. 대상/컨트롤러 트리는 분리하고 상태는 외부에 둔다. 대상이나 컨트롤러가 바뀐 뒤
기존 상태를 재사용하는 것은 거부하며 새 상태 디렉터리를 사용한다. 사람의 결정은 새 계약/
상태 디렉터리에서 명시적으로 해결할 때까지 대기로 유지한다.

## 경계와 한계

이는 경로/소유권 분리와 CLI 작업 공간 샌드박스이며 운영체제 수준 격리의 증명은 아니다.
로컬 검사는 컨트롤러 사용자 권한으로 실행하므로 신뢰된 검사를 사용한다.
무인 운영 전에는 더 강한 OS/CI 격리로 대상 스크립트·심볼릭 링크 공격·임의 외부 명령에서
컨트롤러를 보호한다. 대상 코드는 정당하게 계약·컨트롤러·로그를 편집할 수 없다.
기존 실행기 한도는 호출별이고 선택적 W1 실행기는 누적 마감/횟수를 유지한다.
금액 예산·설치형 백그라운드 스케줄러·알림·다음 목표 선택은 구현하지 않았다. 로컬 휴먼 테스트 화면은 아래와 같이 구현했으며 병합 승인은 작업자가 명시적으로 처리한다.
W2는 제한된 승인 대기열 처리를 추가하며 아래에 절차와 한계를 설명한다.
대상 병합/배포는 자동 승인되지 않는다. W1 게시 범위는 명시적으로 설정한 작업 저장소/
브랜치와 검토한 작업 파일로 제한한다.

보존한 아카이브는 과거 기록이다. 원래 상태 파일에는 옛 절대 경로가 들어 있으므로 재개하거나
증거를 다시 쓰지 않는다. migration.json을 참조한다.

## CoRA F1 이력과 현재 후속 마일스톤

F1은 합성 검증을 완료하고 [CoRA PR #1](https://github.com/yeo-jin-kim/cora/pull/1)을 통해
`codex/workflow-foundation`의 `fe4aac5`에 병합됐다. 부모가 브라우저·검토/게시 단계 연결·
CI 사전 의존성 수정을 제공했으므로 완전한 무인 실행은 아니었다. 계약과 실행 이력은 보존한다.

W1 revision 2는 **선택적으로 사용하는 검증된 구현이다. 시나리오 18/18, 검사 63개,
최종 독립 검토 기준 12개를 모두 통과했다.**
[작업 계약](contracts/dev-workflow/W1-reviewable-delivery.md),
[설계·상태](docs/01-reviewable-delivery-design.md)를 참조한다.
`tools/delivery_loop.py`는 실제 Chrome 실행·버전에 연결된 증거·영속 수정/검토·전용 브랜치
commit/push·정확한 HEAD의 push CI·버전별 병합 결정 보고서를 제공한다. PR은 만들지 않으며
실제 대상 병합은 사용자의 명시적 행동으로 남긴다. 기존 실행기와 과거 상태는 유지한다.

```sh
python3 tools/delivery_loop.py run --project projects/cora-w1-pilot-v2.json --state-dir /ABSOLUTE/EXTERNAL/RUN --max-cycles 3 --total-seconds 3600
python3 tools/delivery_loop.py status --project projects/cora-w1-pilot-v2.json --state-dir /ABSOLUTE/EXTERNAL/RUN
```

위 호출은 과거 기록이며 3회 한도가 소진됐다. 새 상태 디렉터리로 한도를 보충하지 않는다.
사용자는 이후 30분/3회의 추가 시험을 한 번 승인했지만 그 한도도 실제 완료 없이 소진됐다.
그 이후 추가 실제 시험에는 사용자의 명시적 예산 승인이 필요하다. 연결된 v2 설정은 원래
실패와 누적 한도를 보존한다. 구현 기록을 참조한다. 설정은 선택 사항이며 기존 Chrome과
CoRA Python 검사 환경이 있는 특정 호스트용이다. 설계에 기록한 구현 체크아웃을 사용한다.
원본/변경 중 체크아웃이나 컨트롤러 자신을 대상으로 실행하지 않는다.
`status`는 과거 스냅샷을 보여 주며 `run`은 현재 입력/원격 상태를 재검사하고 영속 누적
한도와 미해결 결정을 존중한다. 브라우저·검토자·GitHub 기능 실패는 해결 가능한 근거를 담아
미완료로 남긴다. 결과를 수동 복사하는 지름길은 무인 성공으로 인정하지 않는다.
실행기는 새 의존성을 설치하지 않는다. 실제 파일럿/최종 검토는 `docs/implementation.md`에
기록하며 코드가 있다는 사실만으로 완료를 추정하지 않는다.

## 결과 게시 정책

사용자는 결과를 전달할 때마다 commit/push하도록 요청했다. 유지보수 부모가 결과 확인 후
게시를 마무리한다. 미완료 마일스톤도 실패/누락 게이트를 명시한 전용 브랜치에 push하되,
게시됐다는 이유만으로 병합하거나 통과로 보고하지 않는다. 비공개 .local 로그는 제외하고
구현 작업자는 실행 중 push하지 않는다.

F1 합성 증거는 `tools/evaluate_f1.py`로 검증할 수 있다. 보호 정의·기록한 소스 지문·
실제 브라우저 결과를 검사한다. `docs/implementation.md`를 참조한다.
증거 완료는 독립 검토 게이트를 우회하지 않는다.

사용자는 `projects/cora-w1-approved-trial-60m.json`에 기록한 60분/5회의 추가 실제 시험을
승인했다. 첫 검토는 단계별 시간 한도에 도달했고, 복구 설정은 같은 마감 시각/사용 횟수와
보호된 미완료 검토 증거를 유지한다. 어느 시험의 예산도 자동 갱신하지 않는다.
복구 실행은 원래 마감 시각 안에서 누적 2회를 사용해 CoRA `81b1e21`의
`ready_for_merge_approval`에 도달했다. 실제 검사·Chrome·독립 검토·자동 commit/push·
정확한 HEAD의 push CI·보고서가 통과했으며 PR이나 병합은 없었다. 사전 복구와 이전 실패는
구현 기록에 보존했다.

제한된 복구 마일스톤은 최종 W1 평가와 독립 감사를 통과했다.
이는 제한된 브라우저/커널 파일럿이며 일반 의미 정확성이나 전체 UI 인증은 아니다.
전용 브랜치는 push됐고 실제 병합은 사용자 승인으로 제한한다.

## W2 승인된 작업 대기열

`tools/approved_queue.py`는 사용자가 명시적으로 승인한 W1 작업 대기열을 순서대로 처리한다.
의존성 검사·분리 작업 트리/게시 브랜치·영속 대기열/저장소 예약 한도·고정 실행 창을 사용한다.
W1의 검사·독립 검토·실제 브라우저·정확한 HEAD의 push CI·브랜치/보고서 전달은 유지한다.
각 병합에는 여전히 사용자 승인이 필요하다.
[설계·운영 절차](docs/02-approved-queue-design.md)와 의도적으로 설정하지 않은
[예제](queues/example.json)를 참조한다.

승인 기록은 정확한 대기열/프로젝트/계약/권한 파일과 깨끗한 대상의 HEAD/내용/브랜치,
관측한 원격 기준을 고정한다. `run`은 제안을 자동 승인하지 않는다.
반복 호출은 완료 증거를 복구하되 불명확한 중단 dispatch를 다시 실행하지 않고 멈춘다.
예약은 보수적으로 유지하고 환급하지 않는다. 별도 승인 대기열끼리 금액 계정이나 이동식
일일 계정을 공유하지 않는다. 이는 포그라운드의 제한 처리이며 설치된 백그라운드 스케줄러는
아니다. 예제는 새로운 CoRA 작업을 선택하거나 승인하지 않는다.

W2 전달의 최신성은 시각이 기록된 원격 관측이다. 협조적인 로컬 잠금은 엔진/검증/
체크포인트를 포함하지만 외부 작성자와 이후 원격 변경을 잠그지 않는다.
사용자가 승인한 실제 병합 전에는 정확한 ref를 다시 검증한다.

W2 구현 검증: **검사 94개 통과**, 그중 대기열 사례 31개를 포함한다.
최종 독립 소스 검토 기준 8개도 모두 통과했다. 구현 과정에서 실제 대기열 승인·
백그라운드 스케줄러·병합을 생성하지 않았다.


## 문서 언어

사람이 읽는 모든 Markdown 문서는 완전한 영어 버전을 먼저 두고 전체 한국어 번역을 아래에 둔다.
두 언어는 같은 변경에서 함께 갱신한다. 명령·식별자·기계 판독 증거의 값은 원문을 유지한다.
JSON 계약/스키마와 변경 불가인 과거 실행 자료는 복제하거나 다시 쓰지 않는다.
앞으로 생성하는 병합 결정 Markdown 보고서도 같은 언어 순서를 따르고 원래 기계 필드는
증거임을 명시해 인용한다.

## 검토 파일 기반 수정 접수

`tools/review_intake.py`는 명시적으로 선택한 비공개 검토 파일 하나를 받아 신뢰할
활성 정책으로 제한된 W2→W1 수정 하나를 준비/실행한다. 검토 커밋/소스를 고정하고
원본 바이트를 보존하며 중복·변경·상태 유실을 거부하고 사람 재검토에서 멈춘다.
기존 독립 검토/브라우저/CI 게이트는 유지한다. 예제는 비활성이며 프로젝트별로
신뢰할 실데이터 재실행 검사가 필요하다. 감시기·활성 정책·새 CoRA 수정은 설치하지
않았다. [가이드](docs/03-review-json-intake.md)를 참조한다.

## 데이터 품질 시험 — 2026-11-12

명시적으로 실행하는 복사본 전용 데이터 품질 파이프라인을 제공한다. [가이드](docs/data-quality-workflow.md)를 참고한다. 탐지, 선택적인 고정 범위 W1 코드 수정, 격리 그래프 시험 후 소유자 검토에서 멈춘다. 원본이 모호하면 복구를 차단하며 예약 실행이나 원본 그래프 적용은 활성화하지 않는다.

## 검토 요청 접수 — 2026-11-15

검토 화면에서 changes_requested를 선택적 로컬 접수로 직접 전송할 수 있다. 세션 토큰·Host/Origin 검사·지속 중복 방지·상태/결과 링크·고정 복사본 복구 계약을 제공한다. [가이드](docs/data-quality-workflow.md)를 참고한다. 브라우저 메모로 범용 코드 편집이나 원본 반영을 허용하지 않는다.

## Recall 중심 수정 검토 — 2026-11-15

기존 CoRA 실데이터 Recall 화면에서 검토 의견을 전송한다. 품질 화면은 읽기 쉬운 결과·진단용이며 원본 스레드 ID는 상세에 둔다. 설정된 제거 계약 밖의 답변 문제는 범위 검토로 저장하고 제거 작업으로 실행하지 않는다. docs/data-quality-workflow.md를 참고한다.

## 검토 전송 수정 — 2026-11-15

실제 Recall 추적은 기존 256 KiB 접수 한도를 초과할 수 있다. 선택적 중계와 외부 접수기는 전체 검토 기록을 보존하며 최대 8 MiB의 제한된 JSON 요청을 받는다. 중계 오류는 JSON으로 반환하며, 화면은 현재 판단을 버리지 않고 JSON이 아닌 서버 응답을 설명한다. 작업 범위·권한·원본 그래프 제한은 유지한다. 회귀 검사는 300 KB 합성 검토와 JSON 중계 거절을 확인하며 모델 답변의 정확성을 입증하지 않는다.

## 답변·검색 개발 계약 — 2026-11-15

`contracts/cora/recall-answer-repair.json`과 영문/한글 지침, 비활성 `projects/cora-recall-answer-{repair,intake}.example.json` 설정 템플릿을 추가했다. 고정 그래프 제거와 구분하여 기존 비공개 검토 접수 및 W2/W1 코드 개발 흐름을 사용한다. 기준 버전 재현·타당한 기대 동작·합성 사례의 기준 실패/후보 통과·부정 인접 사례·원래 질문 전후 재실행·별도 검토·문서·휴먼 재검토·정확한 커밋의 CI를 요구한다. Me 누락 보고만으로 Me가 답변에 포함되어야 한다고 정하지 않는다.

`execution_limits`는 3600초/5회를 고정하며 검토 정책 로딩과 직접 W1 초기화 모두 새 상태 생성 전에 초과를 거절한다. 이 필드가 없는 과거 계약은 기존 동작을 유지한다. 재실행 연결 검사는 이제 대화 메타데이터도 포함한다. 이번 전달은 계약과 실행 가능한 제한 검사 추가이며 실제 CoRA 수정 실행은 아니다. 웹의 답변 보고는 계속 범위 검토로 접수되고 비활성 예제는 실행하지 않으며, 구체적으로 고정된 실제 데이터 재실행 어댑터가 필요하다. 기존 요청·혼합 노드 정책·이전 예산·원본 그래프는 유지한다. `contracts/cora/recall-answer-repair.md`를 참고한다.

## 웹 답변 개발 실행 연결 — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json`은 기존 고정 혼합 노드 정책과 함께 답변·검색 실행을 선택적으로 활성화한다. 추가 정책은 `review_intake.policy_inputs`를 통과하고 `cora-recall-answer-repair-v1`을 지정해야 한다. 별도 고정하므로 경로를 활성화해도 과거 제거 정책 해시를 바꾸거나 기존 접수 기록을 승인하거나 예산을 갱신하지 않는다. 완료된 깨끗한 버전 연결의 새 보고는 `answer_dispatch.py`를 통해 운영자가 준비한 격리 체크아웃의 기존 W2/W1 실행기로 전달된다. 웹 호출자는 명령·경로·예산을 선택하지 못한다. 중복 사례 신원은 내보내기/전송/응답 ID를 제외하며 다시 내보내도 원래 기한을 유지한다. 권한 입력이 바뀌면 결정을 요구한다.

실행 연결기는 먼저 `review_replay_gate.py`로 신뢰된 재실행을 수행하고 비공개 기준 관찰을 작업 입력으로 고정한 뒤 고정 개발 계약을 준비·실행한다. `cora_review_replay.py`는 대상 체크아웃의 CoRA 네이티브 복사본 재실행 명령을 시작해 소스/검토 연결을 추가하며 대상 패키지를 가져오지 않는다. 바깥 실행 기한은 사전 확인/재실행을 포함하고 시간 초과 시 프로세스 그룹을 종료하며 내부 W1 수정 횟수는 최대 5회다. 중단된 작업을 자동 재시작하지 않는다. 내보내기에 안정된 그래프 내용 신원이 있으면 검사한다. 대화 기록이나 검증된 로컬 모델 신원이 없으면 설정을 바꾸거나 수정 완료를 주장하지 않고 차단한다.

상태 조회와 비공개 접수 화면에 개발 상태를 표시한다. 검토를 통과한 W1 후보에 승인된 내용 지문과 연결된 재실행 결과가 있을 때만 수정 후 답변을 표시하며 검토 당시 답변과 이유를 유지한다. 휴먼 재검토·의미 모호성·병합·운영 반영은 별도 결정이다. 브라우저는 검토 상태를 보존하며 새로고침이 과거 기록을 현재 승인으로 바꾸지 않는다. 재실행 관찰만으로 의미 정확성을 승인하지 않는다. 현재 통합 시험의 작업자/브라우저/CI는 합성 대체이며 실제 데이터 네이티브 재실행 시험은 실제 자율 수정과 구분한다. 이번 통합 전달에서는 실제 코드 작업자를 시작하거나 원본 그래프를 수정하지 않았다.

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

## 자동 품질 개선 프로토콜 — 실험 단계

`tools/quality_improvement.py`에 한도 있는 재현·원인 검토·수정·고정 사례 평가·별도 검토를
추가했다. 검토 지적을 다음 시도에 자동 전달하며 회귀·실패 숨김·연속 두 번 미수락·사용자 결정
경계를 유지한다. 성공 후보도 자동 게시·병합 없이 사람 재시험에서 멈춘다. 고정 작업 ID가 누적
한도와 중단 기록을 보존한다.

CoRA 평가 연결기는 고정 합성 정답과 실원문 실행 검사를 결합한다. 실행 성공은 의미 정확도가
아니다. 설치된 에이전트 연결기는 읽기 전용 원인 검토/재검토와 한도 있는 쓰기 수정을 별도로
호출하고 기본 모델 설정을 유지한다. 비활성 예제 정책·토픽 계약은 실제 로컬 경로·보호 입력·
범위/예산 승인 참조를 설정해야 실제 실행할 수 있다. 스케줄러나 현재 모델 수정은 활성화하지
않았다. 실제 CoRA 결과 30개 원문·17개 실패를 접수했으며 아직 확정된 원인이나 정답은 아니다.
[프로토콜과 사용 순서](docs/quality-improvement-protocol.md)를 참고한다.

이전 단계의 입력·로그·결과 파일을 해시하고 이후 단계와 사람 재시험 전에 다시 대조한다. 증거가 바뀌면 후보를 무효화한다.

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

### 승인 연장 완료, 수락 없음 — 2026-11-27

사용자가 총 5회를 유지하며 30분을 추가 승인했다. 사용한 권한은 이제 90분·5회다. 최초 실험과 모든 실패·부분 실행은 변경 없이 보존한다. 4번째 주기는 기준 첫 호출 프롬프트를 복원해 검사 602개·합성 사례 8개를 통과했지만 실제 원문 부분 상태에 개선이 없었고 예비 검토에서 식별 대상 변경 가능성을 지적했다. 5번째 주기는 이미 원문으로 확인된 식별 값 보존, 별도 동일 대상 검사, 정확한 필드별 수정 피드백과 적대적 회귀 사례를 추가했다.

최종 증거: CoRA `9485160`, **검사 607개 통과(21.34초)**, 합성 의미 사례 **8/8 통과**, 고정 실제 원문 **30/30 평가**. 처리 오류 원문은 **17 → 13건**(38개 처리 점수 통과 21 → 25, 실패 17 → 13, 사례 단위 처리 회귀 없음). 수락 항목은 14 → 17개, needs_scope는 4 → 6개로 늘었다. 사례 단위 실행 점수는 정상 보류를 처리 완료로 보므로 비공개 항목 단위 감사에서 새 보류를 별도로 기록하며 의미 수정으로 인정하지 않는다.

후보는 수락하지 않는다. 상위 감독 검토에서 리뷰어 알림을 저자 논문 제출 후보로 승격한 문제가 확인됐다. 최종 독립 검토는 판정 없이 시간 초과됐고 예비 검토는 수정을 요청했으며, 소스 보호 지적을 반영한 것만으로 최종 통과를 뜻하지 않는다. 5회를 모두 사용했다. 병합·정식 그래프 변경·활성 pool 교체는 없었다. 자체 실행 증거·비교·명시적 연장 권한·`final-outcome.json`은 무시된 `.local/quality-improvement/topic-runtime-retrial-20261127/`에 있다. 최종 상태는 처리 실패 13건과 의미 역할 문제를 남긴 budget_exhausted다. 다음 우선순위는 원문 기반 사용자 역할·저자 관계 검증이며 별도로 승인된 추가 한도가 필요하고, 몰래 재시도하거나 초기화하지 않는다. 자동 진단 중단 후 감독 복구였으며 무인 폐쇄 반복의 성공은 아니다.

### 맥락별 해석 결과 처리 — 2026-11-27

CoRA는 토픽 pool 저장 전에 맥락에서 생성한 대안·조건·질문과 원문 그대로의 평가 기록을 제공한다(대상 저장소 설계/16). 실행기는 독립적이며 대상 모듈을 가져오지 않는다. 실행 판정 v2는 `needs_scope`, `interpretation_deferred`, `interpretation_revision_required`를 수락·미해결이 섞인 결과까지 포함하여 `deferred`로 전달한다. 검증된 수정이나 코드 실패가 아니다. 맥락 검토 무효는 처리 실패로 유지한다. 실패가 없는 기준 평가는 미해결이면 `needs_context`, 모두 통과하면 `no_repair_needed`에서 멈추고 개발 작업자를 실행하지 않는다. 두 종료 기록도 무결성 검사를 유지하며 병합·Knowledge를 승인하지 않는다. 기존 실패→보류를 수정 성공으로 숨기지 못하는 검사는 유지한다.

선택적 `context_fixtures` 설정은 자체 맥락 평가기로 고정 `context:` 사례를 추가한다. 누락·중복 항목은 차단하며 평가기·모델 식별 기록을 보존한다. 예제 계약은 맥락 구현·검사·설계 수정을 허용하되 맥락 사례·평가 명령은 보호한다. 실행 v2는 사례 예상 해시를 바꾸므로 새 목록을 만들고 과거 실험을 재사용·덮어쓰지 않는다. 자동 실행·예산 갱신·모델 학습·다른 이벤트 검색·게시는 도입하지 않는다. 이전 90분·5회 실험은 소진·미수락 상태로 보존한다. 사용자가 새로 요청한 구현이며 과거 실험의 연장·초기화가 아니다.

검증: 실행기 전체 **188개 검사 통과**, 최종 집중 **23개 검사 통과(23.393초)**. CoRA 연결은 **634개 검사**와 변경하지 않은 primary 선택 기준의 제한적 로컬 모델 시험 4건을 통과했다. 실제 원문의 불확실한 역할은 보류했으며 일반 의미 정확성이나 기존 처리 실패 13건의 해결을 입증하지 않는다. 독립 전달 검토는 대기 상태이며 병합이나 과거 실험 한도 갱신은 없다.

최종 버전 연결 재검증: CoRA **634개 검사 통과(21.26초)**, 실행기 **188개 검사 통과(148.184초)**, 변경하지 않은 primary 선택 모델 시험 **4/4개 통과**. 실행기의 시간 한도 오류 실행은 보존했고 코드나 검사 예산을 바꾸지 않은 전체 재실행은 통과했다. 검사 로그와 모델 출력은 실행 전후 파일 해시에 연결한다. 이는 프로토타입 전달 증거이며 병합 승인이나 일반 의미 정확성의 입증은 아니다.

전달 검토 완료: 별도 읽기 전용 후속 검토가 다섯 기준을 모두 통과했고 차단 항목이나 결정 요청은 없었다. 앞선 수정 요청과 실패 검사는 보존한다. 이 최종 상태 주석은 문서만 바꾸며 게시와 병합은 별도 단계다.

### 원문 간 맥락 평가 — 2026-11-28

대상은 맥락 평가 전에 현재 개체 snapshot 안의 실제 원문을 제한적으로 검색하고,
자체 토픽 평가기는 고정 manifest만 검색한다. 실행기는 대상 코드를 가져오지 않고
실행 예산도 바꾸지 않는다. 선택적 `additional_context_fixtures` 경로는 자체
`--additional-fixtures` 인자를 통해 기존 `context_fixtures`에 보호된 원문 연결 사례를
추가한다. 기존 사례 해시는 유지하며 중복 ID·평가 누락·기본 사례 없이 추가 사례만
지정한 설정은 거부한다. 사례 집합이 달라지면 새 고정 목록을 만들며 과거 실험을
재시작하거나 다시 채점하지 않는다.

예제는 새 검색 모듈·검사를 허용 경로에 명시하고 새 합성 원문 맥락 사례를 보호한다.
관련 원문 조회가 불완전하면 정상 맥락 `deferred`로 남고 검색 원문은 pool hit를
늘리지 않는다. 모델/처리 결과 누락·무효는 기존 실패 숨김 방지 정책의 실패로 유지한다.
보수적 미채택을 검사할 수 있지만 실행기나 모델은 의미적 진실을 인증하지 않는다.
그래프 탐색·대안 재작성·원본/그래프 변경·새 수정 실험 실행은 이번 전달에 포함하지
않는다. 새 읽기 전용 검토 계약은 `contracts/quality/contextual-source-retrieval.json`이다.
확장 검증 결과는 대기 상태이며 이전 188개 검사 결과는 과거 기록이다.

확장 회귀 검증: 실행기 **190개 검사 통과(139.761초)**. 기존 사례 해시 유지·추가 사례 전체 평가·중복/기본 사례 누락 거부를 포함한다. 대상에서 실패한 긍정 모델 사례는 실패로 유지하며 정상 맥락 보류를 긍정적인 의미 수정으로 계산하지 않는다. 과거 실험이나 실행 예산을 갱신하지 않았다.

확장 검증 — 2026-11-28: 코드에 연결한 CoRA **663개 검사 통과(22.47초)**,
실행기 **190개 검사 통과(139.761초)**. 마지막 로컬 Gemma 시험은 변경하지 않은
primary 선택 기준 **5/5개**를 충족했다. 연결된 실제 원문의 참여 근거로 원래 가설을
선택하고 다른 제출 연도로 저자 참여를 승격하지 않는 경우를 포함한다. 긍정 사례는
연결과 해석을 나눠 평가했다. 앞선 시험 세 번(4/5·3/5·4/5)은 비공개 증거에 실패로
보존하며 소급해서 통과로 바꾸지 않는다. 코드에 연결한 실제 검색 시험은 이벤트
3,840개 중 검토 원문 외 일치 단서 242개에서 전체 원문 3개를 유지하고 239개를
미검토로 기록했다. 이는 검색 동작 검증이며 의미 정확성이 아니다. UI 소스 검토·
JavaScript 문법·diff 형식 검사는 통과했고 브라우저 조작이나 활성 미리보기 교체는
하지 않았다. 독립적인 읽기 전용 전달 검토는 대기 상태다. 기존 원문 처리 실패 13건은
재실험하거나 해결했다고 주장하지 않는다. 원본/그래프 쓰기·과거 수정 예산 갱신·
자동 대안 재작성·PR·병합은 없다.

최종 전달 후보 — 2026-11-28: **CoRA 664개 검사 통과(22.73초)**,
**실행기 190개 검사 통과(139.761초)**. 자체 합성 기준 평가 격리 보완 후 변경하지
않은 모델 시험 다섯 건이 전체 코드에 연결된 후보에서 다시 **5/5개 통과**했다.
일반 합성 기준 사례는 이름이 같아도 서로 독립된 상황이므로 보강 검색 범위를
비워 둔다. 실제 평가는 manifest만 사용하고 명시적인 원문 연결 사례는 자체 관련
원문 집합을 제공한다. CLI 통합 검사는 이 구분을 확인하며 모델 정확성을 주장하지
않는다. 마지막 실제 검색도 원문 3개를 조회하고 미검토 239개를 기록했다.

첫 독립 검토는 판정 없이 시간 초과됐으며 통과로 취급하지 않는다. 간결한 증거를
사용한 읽기 전용 후속 검토는 대기 상태다. 앞선 검사·모델 실패와 검토 출력은
보존한다. 이 확장은 기존 추출·동일성·의미 검증을 통과한 뒤 실행하며 앞 단계의
`no_subject`나 의미 거절을 자동 복구하지 않는다. 활성 미리보기·그래프 데이터·
과거 수정 한도는 그대로이며 그래프 탐색과 대안 재작성은 보류 상태다.

검토 후 검증 — 2026-11-28: 기준 시점 보완 후 코드에 연결한 CoRA 회귀는
**678개 통과(23.44초)**이고 변경하지 않은 모델 시험도 다시 **5/5개 통과**했다.
실행기 코드는 **190개 검사** 증거와 계속 일치한다. 실제 원문 검색도 유지 원문
3개/미검토 239개로 동일하다. 새 무효 기준 시점 사례 14개는 빈 범위와 불일치 범위의
명시적 검색도 포함한다. 관련 기록이 없으면 원문 간 검색을 요청하지 않으며 단일
원문 주장은 시간적 보강 근거를 얻었다고 주장하지 않고 기존 동작을 유지한다.
독립 검토의 수정 요청은 보존하고 해당 부분의 후속 검토를 진행할 예정이다.
원본·그래프·예상 정답·기준 횟수·과거 실험 한도는 바꾸지 않았다.

전달 검토 완료 — 2026-11-28: 독립적인 읽기 전용 후속 검토가 다섯 기준을 모두 통과했고 차단 항목이나 사용자 결정 요청은 없었다. 앞선 시간 초과·수정 요청·실패 시험은 보존한다. 이 상태 주석은 문서만 바꾸며 commit/push는 브랜치 전달이지 병합이나 의미 채택이 아니다.
