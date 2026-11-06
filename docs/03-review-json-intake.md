<!-- document-language: en -->
# Review JSON intake

## Status and boundary

Implemented explicit one-file/one-record repair dispatch over the existing W2 queue
and W1 engine. It does not watch folders, install schedules, add a CoRA dependency,
create worktrees or merge branches. The example policy is disabled and grants no
live repair authority. No new CoRA repair was dispatched in this delivery.

The review is issue evidence, never a command, scope definition or authorization.
Only an operator-selected, enabled policy under `projects/` supplies a trusted W1
project, a dedicated repair template, ordered source-fingerprint patterns, a fixed
real-data replay check, limits and a reference to an actual owner authorization.
Those inputs are pinned. No review text can supply paths, commands or allowance.
This records existing authority; it does not authenticate a human or prove that a
free-text authorization reference is real. Treat controller policy files as trusted
operator configuration. Path separation is not OS isolation or a prompt-injection
proof; workers and independent reviewers must inspect the actual correction.

## Setup once for an authorized scope

1. Copy `projects/cora-review-intake.example.json` and
   `projects/cora-review-repair.example.json` to operator-owned project settings.
   Keep the example disabled. Choose a clean, separate target checkout, already on
   its dedicated repair branch at the exact reviewed commit. Use a suitable Python
   environment, real Chrome and remote CI settings. Preserve original data.
2. Inspect `contracts/cora/review-repair-template.json`; freeze the narrowly allowed
   files, checks and criteria for the intended class of repairs. The template must
   declare `review_repair_template: true`; an unrelated W1 task cannot be reused.
3. Supply a real owner-approved `replay_check` argv referencing `{review}`. The
   placeholder in the disabled example is intentionally not executable. This
   project-specific check must replay the original case against the candidate,
   establish source/data/provider identity, preserve private before/after evidence
   under `{evidence}`, and fail when prerequisites or reproduction are unavailable.
   A running old API or a successful HTTP response is insufficient. Independent
   review must assess semantic correction; the intake does not invent a gold answer.
4. Select ordered source patterns that reproduce the exporter's source digest.
   CoRA's current recipe is all `src/**/*.py` in sorted order, followed by
   `src/cora/visualization/real_recall_review.html`; each contributes its relative
   path, a NUL byte and file bytes. Hashes of graph/snapshot and retrieval versions
   are required/preserved; domain data freshness is enforced by the trusted replay,
   not inferred from the frontend commit. Backend identity in the current export
   is not attested by the Recall API.
5. Record an actual authorization reference and explicit positive time/cycle limits;
   enable only the operator copy when that scope is authorized. Example 1200
   seconds/two cycles is illustrative, not an active owner grant. Required W1
   browser, independent review, documentation, publication and exact-head remote
   CI gates remain intact. PRs are optional; merging is separate owner action.

## Commands

From the controller checkout (Python 3.9+):

```sh
python3 tools/review_intake.py prepare --review /PRIVATE/review.json \
  --policy projects/approved-review-policy.json
python3 tools/review_intake.py start --review /PRIVATE/review.json \
  --policy projects/approved-review-policy.json
python3 tools/review_intake.py run --intake INTAKE_SHA256
python3 tools/review_intake.py status --intake INTAKE_SHA256
```

`prepare` preserves evidence and creates the immutable task/project/queue/approval
packet without executing a worker. `start` prepares and dispatches a newly prepared
packet immediately. `run` dispatches/resumes the recorded intake without allocating
another task. `status` reads the journal. For a multi-record export supply
`--record-id RECORD_ID`; never silently choose the first report. Exit 0 means
prepared or awaiting human retest, not accepted/merged; other states exit 2.

Only `changes_requested`, a nonempty reason and supported issue categories are
accepted. Pass/Hold, malformed or dirty-version records are rejected. Commit and
source digest must match the clean target both before preparation approval and
before dispatch. A stale report is preserved for a decision, without starting a
repair. Policy/concept/acceptance changes, ambiguous requirements, already-fixed
or unreproducible reports must stop for owner decision through the task criteria.
This semantic boundary is review-enforced, not automatic language understanding.

### Replay observation protocol

The controller wraps the trusted argv with `tools/review_replay_gate.py`; both
`{review}` and `{evidence}` must occur in its argv. Exit 0 alone is insufficient.
The replay must create a fresh `{evidence}/review-replay.json` (no preexisting file
or symlink) with `schema_version: 1`, `selected_review_sha256` (selected file bytes),
`target_digest` (the existing `delivery_evidence.manifest(target)` digest),
`snapshot_sha256`, `replayed_request` and the complete observed API `response`.
The wrapper rejects source/review changes, wrong bindings, a different question,
options or working-memory scope, missing activation trace and a changed/missing
integer retrieval `graphSequence`. The response must contain `request.query`,
`answer.summary`, and trace dictionaries `activationScores`/`activationPaths`.
A valid artifact is `observed_not_semantically_accepted`; semantic correction is
still the independent reviewer's task. The wrapper validates bindings, not the
truthfulness of a trusted project's replay implementation or backend provenance.

## Durable records and gates

- Original export bytes and SHA-256, normalized export and selected record live
  privately under `.local/review-intake/INTAKE_SHA256/`. Generated contracts are in
  ignored `contracts/.local/review-intake/`. Generated folders must be Git-ignored;
  packet files are created exclusively with private permissions.
- `.local/review-journal/` stores durable intake reservation/state outside queue
  state. The identity excludes export/review timestamps and record UUIDs; reexporting
  the same execution does not grant more time. Editing its reason/issues requires a
  decision rather than allocating another budget. Changed actual execution contents
  can be a new intake and require another explicit invocation. There is no global
  monetary/project quota beyond the one-task queue's approved limits.
- All packet files, policy, project/template authority and approval are fingerprint
  bound. Missing/changed evidence or authority refuses dispatch. Lost state after
  dispatch, unowned existing state or interrupted preparation never regenerates
  allowance. The original journal/inputs must be preserved; deleting all controller
  evidence defeats local bookkeeping and is outside this filesystem trust model.
- One cooperative local intake lock serializes import/dispatch. Existing W2 target
  locks, reservation accounting, W1 evidence verification and exact-head gates
  remain unchanged. Inputs from review JSON are never used as shell commands.
- Success is `awaiting_human_retest` with the candidate/report receipt and an explicit
  no-merge handoff. The W2 raw status may say `delivered_awaiting_merge`; the intake
  adds the owner real-data retest requirement. Automated pass is not owner acceptance.
- Failure preserves W1 history and may safely commit/push an explicitly incomplete
  dedicated-branch candidate under existing publication-safety review. Such a WIP
  is not accepted and does not trigger another automatic repair allowance.

The operator must export CoRA review records before reload. This first version
accepts a file explicitly; it has no CoRA submission button, filesystem watcher,
automatic policy generation, persistent human-approval service or scheduler.
Private review data must never be committed. Generated JSON remains machine-readable;
existing W1 Markdown reports already use English followed by Korean.

## Verification

Tests use real temporary Git repositories, local bare remotes and the actual
W2→W1 gate chain with explicitly synthetic AI/browser/CI and replay responses.
They do not establish unattended real CoRA repair or semantic reliability.
The supplied actual CoRA review was checked read-only: reviewed commit `911127c`
differs from current `cc820de`; preflight correctly requested a decision and
performed no dispatch. Final counts and independent review are recorded in
`docs/implementation.md`.

---

<!-- document-language: ko -->
# 한국어 번역

# 검토 JSON 접수

## 상태와 경계

기존 W2 대기열과 W1 실행기에 파일 하나/기록 하나를 명시적으로 접수해 수정 작업을
실행하는 연결을 구현했다. 폴더 감시·일정 설치·CoRA 의존성 추가·작업 트리 생성·
병합은 하지 않는다. 예제 정책은 비활성이며 실제 수정 권한을 부여하지 않는다.
이번 전달에서 새 CoRA 수정 작업은 실행하지 않았다.

검토는 오류 증거이며 명령·범위 정의·승인이 아니다. 운영자가 선택한 `projects/`의
활성 정책만 신뢰할 W1 프로젝트·전용 수정 템플릿·순서가 정해진 소스 지문 패턴·
고정 실데이터 재실행 검사·한도·실제 소유자 승인 참조를 제공한다. 이 입력을 고정하며
검토 문구로 경로·명령·예산을 정할 수 없다. 기존 승인을 기록하는 것이며 사람 인증이나
자유 문구 승인 참조의 진위를 증명하지 않는다. 컨트롤러 정책 파일은 신뢰할 운영자
설정으로 다룬다. 경로 분리는 OS 격리나 프롬프트 주입 방지 증명이 아니며 작업자와
독립 검토자는 실제 수정 내용을 검토해야 한다.

## 승인된 범위를 위한 최초 설정

1. `projects/cora-review-intake.example.json`과
   `projects/cora-review-repair.example.json`을 운영자용 프로젝트 설정으로 복사한다.
   예제는 비활성으로 둔다. 정확한 검토 커밋에서 전용 수정 브랜치를 사용하는 깨끗한
   별도 체크아웃을 선택하고 적절한 Python·실제 Chrome·원격 CI를 설정한다. 원본
   데이터는 보존한다.
2. `contracts/cora/review-repair-template.json`의 허용 파일·검사·기준을 검토하고
   해당 수정 유형에 맞게 좁혀 고정한다. `review_repair_template: true`가 필요하며
   관련 없는 W1 작업 계약을 재사용할 수 없다.
3. `{review}`를 참조하는 실제 소유자 승인 `replay_check` 명령 인자 목록을 제공한다.
   비활성 예제의 자리표시자는 의도적으로 실행 가능하지 않다. 프로젝트별 검사는
   원래 사례를 후보 버전에서 재실행하고 소스/데이터/provider 버전을 확인하며 비공개
   전후 증거를 `{evidence}`에 보존하고, 전제 조건이나 재현이 없으면 실패해야 한다.
   예전 API가 실행 중이거나 HTTP 요청이 성공한 것만으로는 부족하다. 독립 검토에서
   의미적 수정을 판단해야 하며 접수기가 정답을 만들어내지 않는다.
4. 내보내기 소스 지문을 재현하는 순서의 패턴을 지정한다. 현재 CoRA는 정렬한
   `src/**/*.py` 전체 뒤에 `src/cora/visualization/real_recall_review.html`을 처리하며
   각 상대 경로·NUL 바이트·파일 바이트를 해시에 넣는다. 그래프/스냅샷 해시와 검색
   버전은 요구/보존하며 실제 데이터 최신성은 프런트엔드 커밋에서 추론하지 않고
   신뢰할 재실행 검사에서 확인한다. 현재 Recall API는 내보내기의 백엔드 버전을
   증명하지 않는다.
5. 실제 승인 참조와 양의 시간/횟수 한도를 기록하고 해당 범위가 승인됐을 때만
   운영자용 복사본을 활성화한다. 예제의 1200초/2회는 설명용이며 활성 승인 한도가
   아니다. W1의 브라우저·독립 검토·문서·게시·정확한 HEAD의 원격 CI 게이트는 유지한다.
   PR은 선택이고 병합은 별도의 소유자 행위다.

## 명령

컨트롤러 체크아웃에서 Python 3.9 이상으로 실행한다.

```sh
python3 tools/review_intake.py prepare --review /PRIVATE/review.json \
  --policy projects/approved-review-policy.json
python3 tools/review_intake.py start --review /PRIVATE/review.json \
  --policy projects/approved-review-policy.json
python3 tools/review_intake.py run --intake INTAKE_SHA256
python3 tools/review_intake.py status --intake INTAKE_SHA256
```

`prepare`는 증거를 보존하고 불변 작업/프로젝트/대기열/승인 패킷을 만들지만 작업자를
실행하지 않는다. `start`는 새로 준비된 패킷을 즉시 실행한다. `run`은 추가 할당 없이
기록된 접수를 실행/재개하며 `status`는 저널을 읽는다. 여러 기록이 있으면
`--record-id RECORD_ID`로 하나를 지정하며 첫 항목을 임의로 선택하지 않는다.
종료 코드 0은 준비 완료 또는 사람 재검토 대기이며 수용/병합을 뜻하지 않는다.
그 밖의 상태는 종료 코드 2다.

`changes_requested`·비어 있지 않은 이유·지원하는 문제 유형만 받는다. 통과/보류·
잘못된 형식·변경 중인 버전은 거부한다. 준비 승인 전과 실행 전 모두 커밋/소스 지문이
깨끗한 대상과 일치해야 한다. 오래된 검토는 결정용으로 보존하고 수정을 시작하지
않는다. 정책/개념/수용 기준 변경·모호한 요구·이미 수정됐거나 재현 불가능한 보고는
작업 기준을 통해 소유자 결정으로 넘긴다. 의미 경계는 자동 언어 이해가 아닌
검토로 집행한다.

### 재실행 관찰 기록 규약

컨트롤러가 신뢰할 명령을 `tools/review_replay_gate.py`로 감싼다. 명령 인자에
`{review}`와 `{evidence}`가 모두 필요하며 종료 코드 0만으로는 부족하다.
재실행 명령은 기존 파일/심볼릭 링크가 없는 새로운
`{evidence}/review-replay.json`을 생성해야 한다. 필드는 `schema_version: 1`,
선택 파일 바이트의 `selected_review_sha256`, 기존
`delivery_evidence.manifest(target)`의 `target_digest`, `snapshot_sha256`,
`replayed_request`, 전체 관찰 API `response`다. 래퍼는 소스/검토 변경·지문
불일치·다른 질문/설정/작업 기억 범위·활성화 경로 누락·정수 검색 `graphSequence`의
변경/누락을 거부한다. 응답에 `request.query`, `answer.summary`, 경로 딕셔너리
`activationScores`/`activationPaths`가 필요하다. 유효해도
`observed_not_semantically_accepted`이며 의미적 수정은 독립 검토자가 판단한다.
래퍼는 지문 연결을 확인하며 신뢰한 프로젝트 재실행 구현의 진실성이나 백엔드 버전을
증명하지는 않는다.

## 영속 기록과 게이트

- 원본 내보내기 바이트/SHA-256·정규화 내보내기·선택 기록은
  `.local/review-intake/INTAKE_SHA256/`에 비공개로 보존한다. 생성 계약은 무시된
  `contracts/.local/review-intake/`에 둔다. 생성 폴더는 Git 무시 대상이어야 하며
  패킷은 비공개 권한으로 배타 생성한다.
- `.local/review-journal/`에 대기열 상태와 별도로 영속 할당/접수 상태를 둔다.
  식별자는 내보내기/검토 시각·기록 UUID를 제외하므로 같은 실행을 다시 내보내도
  시간을 늘릴 수 없다. 같은 실행의 이유/문제 유형 변경은 추가 할당이 아니라
  결정을 요구한다. 실제 실행 내용이 바뀌면 새 접수가 될 수 있으며 별도 명시적
  호출이 필요하다. 단일 작업 대기열 한도 밖의 전역 금액/프로젝트 할당량은 없다.
- 모든 패킷 파일·정책·프로젝트/템플릿·승인 지문을 고정하며 누락/변경 시 실행을
  거부한다. 실행 후 상태 유실·소유 불명 기존 상태·준비 중단은 한도를 재생성하지
  않는다. 저널/입력을 보존해야 하며 컨트롤러 증거 전체 삭제는 로컬 기록 모델을
  무력화하므로 이 파일시스템 신뢰 모델 밖이다.
- 협조적인 로컬 접수 잠금 하나가 접수/실행을 직렬화한다. 기존 W2 대상 잠금·
  예산 예약·W1 증거 검증·정확한 HEAD 게이트는 유지한다. 검토 JSON의 입력을 셸
  명령으로 사용하지 않는다.
- 성공은 후보/보고서와 병합 불가 인계를 포함한 `awaiting_human_retest`다. 원래
  W2 상태는 `delivered_awaiting_merge`일 수 있지만 접수기가 소유자 실데이터 재검토를
  추가로 요구한다. 자동 통과는 소유자 수용이 아니다.
- 실패하면 W1 이력을 보존하고 기존 게시 안전 검토에 따라 명시적 미완료 후보를
  전용 브랜치에 commit/push할 수 있다. 해당 WIP는 수용이 아니며 추가 자동 수정
  한도를 부여하지 않는다.

새로고침 전에 CoRA 검토 기록을 내보내야 한다. 첫 버전은 파일을 명시적으로 받으며
CoRA 전송 버튼·파일 감시·정책 자동 생성·영속 사람 승인 서비스·스케줄러는 없다.
개인 검토 데이터를 커밋하면 안 된다. 생성 JSON은 기계 판독 구조를 유지하며 기존
W1 Markdown 보고서는 영어 다음 한국어 순서로 작성된다.

## 검증

임시 실제 Git 저장소·로컬 bare 원격·실제 W2→W1 게이트 연결과 명시적으로 합성인
AI/브라우저/CI/재실행 응답을 사용했다. 무인 실제 CoRA 수정이나 의미 신뢰성을
입증하지 않는다. 제공한 실제 CoRA 검토는 읽기 전용으로 확인했다. 검토 커밋
`911127c`가 현재 `cc820de`와 달라 사전 검사에서 결정을 요구하고 실행하지 않았다.
최종 검사 수와 독립 검토는 `docs/implementation.md`에 기록한다.
