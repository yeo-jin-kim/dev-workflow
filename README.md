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
selection and a dedicated approval UI are not implemented. W2 adds bounded
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
금액 예산·설치형 백그라운드 스케줄러·알림·다음 목표 선택·전용 승인 UI는 구현하지 않았다.
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
