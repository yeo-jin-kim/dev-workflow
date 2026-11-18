<!-- document-language: en -->
# Data quality workflow

`tools/quality_workflow.py` is an experimental explicit-invocation pipeline, not
an active scheduler. CoRA supplies domain audit/trial/compare commands; this repo
imports no CoRA code. Copy `projects/cora-quality.example.json` to an ignored
`projects/.local/` policy, supply exact paths and trusted Recall cases, then enable
it only for owner-approved scope. Run:

```sh
python3 tools/quality_workflow.py run --policy projects/.local/quality.json --output .local/quality-run
python3 tools/quality_workflow.py serve --output .local/quality-run --port 8775
```

The fixed argv commands are trusted configuration, never generated from finding
text or executed through a shell. All findings are untrusted evidence. A cumulative
deadline of at most 3600 seconds covers audit, optional code repair, trial and
comparison; process groups are terminated on timeout. Per-binding journal/lock
suppresses duplicate dispatch without resetting consumed allowance. Changed policy,
project or contract stops the run. This is cooperative process control, not OS
isolation or semantic proof. Target and controller paths must be disjoint.

Optional repair_project references a trusted projects/ W1 project with a contract
under contracts/ for the same target. A private copy retains fixed scope/checks
and attaches finding data explicitly as untrusted context. Existing W1 check,
browser, publication-safety, push-CI and independent review gates remain. A code
repair is not required for a source-only blocker; default example does not enable
it. No general-purpose autonomous scope or budget expansion is granted.

After code gates, a blocked domain trial stops before Recall comparison. Successful
copy trials execute trusted deterministic before/after Recall invariants and end
awaiting_owner_review. Empty cases fail and LLM generation is not evaluated.
No production graph apply or automatic merge exists. Owner notes are unauthenticated
plan-bound records. Serving binds localhost and exposes only review HTML, plan,
result, comparison and receipt; graph databases/source files are not served.
Private output contains source-derived text and stays under ignored .local/.

W1 now performs an independent publication-safety audit and publishes an explicitly
unaccepted WIP revision before exact-head push CI, then performs semantic review.
Final acceptance still requires all gates. Transport-only environment variables
are excluded from runtime identity; changed runtime settings invalidate acceptance
and rerun probes/checks/browser/CI/review within the original deadline/cycle budget.
Stopped runs still require an explicit linked authorization, never silent restart.
The worker is told existing authorized verification does not require a new owner
question; genuine scope/model/criteria decisions still do.

Tests include temporary Git/remote W1 CI ordering and environment invalidation,
blocked source trials, duplicate suppression and disabled policy rejection. Synthetic
workers/CI are not a new live nested-agent acceptance trial. The actual private
Nan run blocked because 13 of 187 authoritative source rows are unavailable;
no candidate or after-Recall result was produced. Scheduled monitoring, authenticated
original application and general semantic acceptance remain deferred.

---

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


## Web answer-development dispatch — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json` optionally enables answer/retrieval dispatch alongside the unchanged fixed mixed-node policy. The additional policy must pass `review_intake.policy_inputs` and name `cora-recall-answer-repair-v1`. It is pinned separately, so enabling the route does not alter the old removal policy hash, authorize old staged reports or renew their budgets. New completed, clean/version-bound reports are dispatched through `answer_dispatch.py` to the existing W2/W1 engine in an operator-provisioned isolated checkout. The web caller cannot choose commands, paths or budget. Duplicate case identity ignores export/transport/response IDs and preserves the original deadline even after another export; changed authority requires a decision.

The dispatcher first invokes a trusted replay through `review_replay_gate.py`, pins that private baseline observation into the task, then prepares/runs the frozen development contract. `cora_review_replay.py` launches CoRA's native copy-only replay command from the target checkout, wraps source/review bindings and imports no target package. The outer execution deadline includes preflight/replay and terminates the process group on timeout; internal W1 cycles remain capped at five. Interrupted jobs are not automatically restarted. Stable graph content is checked when exported. Missing history or verified local-model identity blocks rather than changing settings or claiming correction.

Status and the private feedback page show development state. Only a successfully reviewed W1 candidate with a bound replay for its accepted digest exposes an after-answer; the original reviewed answer and reason remain visible. Human retest, semantic ambiguity, merge and production installation remain separate decisions. The browser retains review state; refreshing does not turn an old record into current authorization. A replay observation alone is not semantic acceptance. Current integration tests use synthetic worker/browser/CI fixtures; a real-data native replay probe is separate from an actual autonomous repair. No actual coding worker or original graph modification was started in this integration delivery.

<!-- document-language: ko -->
# 한국어 번역

# 데이터 품질 워크플로

`tools/quality_workflow.py`는 명시적으로 실행하는 실험적 파이프라인이며 작동 중인
예약 실행기가 아니다. CoRA는 도메인 audit/trial/compare 명령을 제공하며 이 저장소는
CoRA 코드를 가져오지 않는다. `projects/cora-quality.example.json`을 무시되는
`projects/.local/` 정책으로 복사하고 정확한 경로·신뢰하는 Recall 사례를 설정한 뒤
소유자가 승인한 범위에만 활성화한다. 실행 방법:

```sh
python3 tools/quality_workflow.py run --policy projects/.local/quality.json --output .local/quality-run
python3 tools/quality_workflow.py serve --output .local/quality-run --port 8775
```

고정 argv 명령은 신뢰하는 설정이며 탐지 문구로 생성하거나 셸로 실행하지 않는다.
모든 탐지 결과는 신뢰하지 않는 근거다. 최대 3600초의 누적 한도에 탐지, 선택적 코드
수정, 시험과 비교가 포함되며 시간 초과 시 프로세스 그룹을 종료한다. 바인딩별 기록·잠금은
사용한 한도를 초기화하지 않고 중복 실행을 억제한다. 정책·프로젝트·계약 변경 시 중단한다.
이는 협력적 프로세스 제어이며 OS 격리나 의미 정확성 증명이 아니다. 대상과 컨트롤러
경로는 겹치면 안 된다.

선택적 repair_project는 같은 대상을 가진 신뢰하는 projects/ W1 프로젝트와 contracts/
아래 계약을 참조한다. 비공개 복사본은 고정 범위·검사를 유지하고 탐지 데이터를 명시적으로
신뢰하지 않는 문맥으로 첨부한다. 기존 W1 검사·브라우저·게시 안전 검토·push CI·독립
검토 게이트를 유지한다. 원본 누락만으로 코드 수정을 요구하지 않으며 기본 예제에서는
이를 활성화하지 않는다. 범용 자율 범위 확장이나 예산 확대 권한은 부여하지 않는다.

코드 게이트 이후 도메인 시험이 차단되면 Recall 비교 전에 중단한다. 복사본 시험에
성공하면 신뢰하는 결정적 변경 전후 Recall 조건을 실행하고 awaiting_owner_review로
끝난다. 빈 사례는 실패하고 LLM 생성은 평가하지 않는다. 운영 그래프 적용이나 자동
병합은 없다. 소유자 메모는 계획에 연결된 인증되지 않은 기록이다. 서버는 localhost에
연결하고 검토 HTML·계획·결과·비교·실행 기록만 제공하며 그래프 DB·원본 파일은 제공하지
않는다. 비공개 결과에는 원문 파생 텍스트가 포함되며 무시되는 .local/에 둔다.

W1은 이제 독립적인 게시 안전 검토 후 명시적으로 미승인인 WIP 버전을 게시하고,
정확한 버전의 push CI 이후 의미 검토를 수행한다. 최종 승인은 모든 게이트를 요구한다.
전송에만 쓰이는 환경 변수는 실행 환경 식별에서 제외한다. 실행 설정 변경은 승인을
무효화하고 기존 마감·반복 예산 안에서 탐색·검사·브라우저·CI·검토를 다시 실행한다.
중단된 실행은 명시적인 연결 승인이 필요하며 조용히 재시작하지 않는다. 이미 승인된
검증은 새 소유자 질문이 필요 없다고 작업자에게 지시하지만 실제 범위·모델·기준 결정은
여전히 소유자에게 남는다.

테스트에는 임시 Git·원격 저장소 기반 W1 CI 순서·환경 무효화, 원본 누락 시험,
중복 억제와 비활성 정책 거부가 포함된다. 모의 작업자·CI는 새로운 실제 중첩 에이전트
승인 시험이 아니다. 실제 비공개 Nan 실행은 권위 있는 원본 187개 중 13개가 없어
차단됐으며 후보나 변경 후 Recall 결과를 만들지 않았다. 예약 모니터링, 인증된 원본
반영과 일반적 의미 승인은 후속 작업이다.


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

## 웹 답변 개발 실행 연결 — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json`은 기존 고정 혼합 노드 정책과 함께 답변·검색 실행을 선택적으로 활성화한다. 추가 정책은 `review_intake.policy_inputs`를 통과하고 `cora-recall-answer-repair-v1`을 지정해야 한다. 별도 고정하므로 경로를 활성화해도 과거 제거 정책 해시를 바꾸거나 기존 접수 기록을 승인하거나 예산을 갱신하지 않는다. 완료된 깨끗한 버전 연결의 새 보고는 `answer_dispatch.py`를 통해 운영자가 준비한 격리 체크아웃의 기존 W2/W1 실행기로 전달된다. 웹 호출자는 명령·경로·예산을 선택하지 못한다. 중복 사례 신원은 내보내기/전송/응답 ID를 제외하며 다시 내보내도 원래 기한을 유지한다. 권한 입력이 바뀌면 결정을 요구한다.

실행 연결기는 먼저 `review_replay_gate.py`로 신뢰된 재실행을 수행하고 비공개 기준 관찰을 작업 입력으로 고정한 뒤 고정 개발 계약을 준비·실행한다. `cora_review_replay.py`는 대상 체크아웃의 CoRA 네이티브 복사본 재실행 명령을 시작해 소스/검토 연결을 추가하며 대상 패키지를 가져오지 않는다. 바깥 실행 기한은 사전 확인/재실행을 포함하고 시간 초과 시 프로세스 그룹을 종료하며 내부 W1 수정 횟수는 최대 5회다. 중단된 작업을 자동 재시작하지 않는다. 내보내기에 안정된 그래프 내용 신원이 있으면 검사한다. 대화 기록이나 검증된 로컬 모델 신원이 없으면 설정을 바꾸거나 수정 완료를 주장하지 않고 차단한다.

상태 조회와 비공개 접수 화면에 개발 상태를 표시한다. 검토를 통과한 W1 후보에 승인된 내용 지문과 연결된 재실행 결과가 있을 때만 수정 후 답변을 표시하며 검토 당시 답변과 이유를 유지한다. 휴먼 재검토·의미 모호성·병합·운영 반영은 별도 결정이다. 브라우저는 검토 상태를 보존하며 새로고침이 과거 기록을 현재 승인으로 바꾸지 않는다. 재실행 관찰만으로 의미 정확성을 승인하지 않는다. 현재 통합 시험의 작업자/브라우저/CI는 합성 대체이며 실제 데이터 네이티브 재실행 시험은 실제 자율 수정과 구분한다. 이번 통합 전달에서는 실제 코드 작업자를 시작하거나 원본 그래프를 수정하지 않았다.
