<!-- document-language: en -->
# CoRA answer and retrieval repair contract

## Current delivery

`recall-answer-repair.json` is a dedicated executable W1 repair template for human-reported Recall answer/retrieval errors. It uses existing `review_intake.py` → W2 → W1 execution, not the mixed-node-removal runner. Controller and contracts remain outside CoRA. The associated example intake policy is disabled: adding this contract does not start a worker, change the live web routing, revive a historical request or modify a graph. A private enabled operator configuration must pin a clean reviewed checkout and an actual replay command before dispatch.

## Input and authority

One exported `changes_requested` review record must include the actual question, options, scope, conversation context, answer, retrieval version, source/snapshot/graph fingerprints, issue category and reason. A review reports a possible error; it cannot define commands, an expected answer, file scope, a budget or approval. The trusted policy, project and contract are immutable inputs. Existing stale/dirty-version rejection, duplicate detection, evidence archives and cumulative execution state remain in force. An old report can inform diagnosis but cannot silently become a new clean baseline.

## Execution and completion

1. Reproduce the reported problem on the exact baseline before editing; retain both the submitted response and reproduction. Verify data/backend/provider identity. Missing prerequisites or an already-fixed report require a decision.
2. Establish expected behavior using accepted design and source evidence. Identify whether the problem is interpretation, traversal/retrieval, selection, answer construction, local-model verification or presentation.
3. Modify only the enumerated Recall implementation/presentation files and one synthetic regression test file, plus affected implementation/design/master documentation. Foundations, source data, graph schema and frozen evaluators are outside scope. No query/name-specific patches or weaker grounding checks.
4. Demonstrate a justified regression failing on baseline and passing on candidate; preserve relevant negative and neighboring cases. Run the frozen Recall quality suite, full suite, whitespace checks, required browser checks, independent semantic/documentation review and exact-head remote CI.
5. Replay the original case on the candidate with the same question, options, working-memory scope, required conversation and data. Keep complete private before/after answers, traces, source references and runtime identities. The replay gate checks bindings and now also rejects dropped conversation metadata; it does not certify semantic correctness or backend honesty. Missing context must block, not silently start a new topic.
6. Deliver a dedicated branch and revision-bound report with diagnosis, answer/evidence changes, remaining limits and human retest instructions. Final human review and merge/production installation remain owner decisions. Never publish private queries or source excerpts in commits/reports intended for a public repository.

The worker and separate read-only reviewer must assess the actual correction. Ordinary path separation and passing tests are not proof of isolation, model quality or semantic correctness. The example F1 browser harness only checks that existing browser boundary; it does not certify the complete Recall review UI. The real-data replay command must be supplied and verified for the local environment, rather than pointing at an unverified old API.

## Limits and decisions

Maximum **3600 seconds and five implementation cycles** per authorized execution, cumulative across its repair loop/resume. Intake and direct W1 reject a larger grant before creating execution state. Retries, duplicate submissions and changed notes cannot automatically renew allowance. Historical contracts without `execution_limits` retain their prior rules. This contract does not install a scheduler or allocate an endless sequence of new cases.

Stop for owner decision on an ambiguous expected answer, a new conceptual/participant-role rule, modifications outside the allowed files, changes to source/graph/schema/evaluators, unavailable replay prerequisites, budget exhaustion or merge/production installation. Preserve failures and partial results.

## Initial case: missing Me

Use the reported EMNLP question and “Missing Me” reason as evidence, not a gold label. Determine whether Me is a source-evidenced participant or only an owner/scope anchor. The contract requires neighboring synthetic cases for both roles and an unrelated active entity. If accepted semantics do not decide inclusion, report the alternatives and impact before changing code. No correction or new real-data comparison has been performed merely by adding this contract.

## Configuration and dispatch

Use `projects/cora-recall-answer-repair.example.json` and `projects/cora-recall-answer-intake.example.json` as templates for private operator settings under `projects/.local/`. Keep the tracked examples disabled. Supply an isolated clean target on its dedicated branch, exact reviewed baseline, available Python/Chrome environments, protected evaluator paths, fixed real-data replay argv using `{review}` and `{evidence}`, and actual authorization reference. Configure delivery repository/base/head and exact-head CI gates. The generic replay script placeholder is intentionally not a working adapter.

```sh
python3 tools/review_intake.py prepare --review /PRIVATE/review.json \
  --policy projects/.local/cora-recall-answer-intake.json
python3 tools/review_intake.py start --review /PRIVATE/review.json \
  --policy projects/.local/cora-recall-answer-intake.json
```

`prepare` creates a pinned packet; `start` prepares and starts only an eligible record. See `docs/03-review-json-intake.md` for status/resume and the replay artifact protocol. The current web `recall_answer` route still stores a scope-review request; this contract alone does not make that route execute code repairs. Automatic web dispatch and concrete replay provisioning are subsequent integration work, not a completed repair claim.


Validation for this delivery: 146 controller tests passed in 117.236 seconds. Focused tests cover capped intake, direct W1 rejection before state creation, malformed limits and conversation-loss rejection. Contract paths/criteria and English/Korean sections were inspected; whitespace checks passed. No actual coding worker, local LLM, browser or remote CoRA CI run was started for this contract delivery.


## Web answer-development dispatch — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json` optionally enables answer/retrieval dispatch alongside the unchanged fixed mixed-node policy. The additional policy must pass `review_intake.policy_inputs` and name `cora-recall-answer-repair-v1`. It is pinned separately, so enabling the route does not alter the old removal policy hash, authorize old staged reports or renew their budgets. New completed, clean/version-bound reports are dispatched through `answer_dispatch.py` to the existing W2/W1 engine in an operator-provisioned isolated checkout. The web caller cannot choose commands, paths or budget. Duplicate case identity ignores export/transport/response IDs and preserves the original deadline even after another export; changed authority requires a decision.

The dispatcher first invokes a trusted replay through `review_replay_gate.py`, pins that private baseline observation into the task, then prepares/runs the frozen development contract. `cora_review_replay.py` launches CoRA's native copy-only replay command from the target checkout, wraps source/review bindings and imports no target package. The outer execution deadline includes preflight/replay and terminates the process group on timeout; internal W1 cycles remain capped at five. Interrupted jobs are not automatically restarted. Stable graph content is checked when exported. Missing history or verified local-model identity blocks rather than changing settings or claiming correction.

Status and the private feedback page show development state. Only a successfully reviewed W1 candidate with a bound replay for its accepted digest exposes an after-answer; the original reviewed answer and reason remain visible. Human retest, semantic ambiguity, merge and production installation remain separate decisions. The browser retains review state; refreshing does not turn an old record into current authorization. A replay observation alone is not semantic acceptance. Current integration tests use synthetic worker/browser/CI fixtures; a real-data native replay probe is separate from an actual autonomous repair. No actual coding worker or original graph modification was started in this integration delivery.

<!-- document-language: ko -->
# 한국어 번역

# CoRA 답변·검색 수정 계약

## 현재 전달 범위

`recall-answer-repair.json`은 사람이 보고한 Recall 답변·검색 오류를 위한 전용 W1 실행 계약 템플릿이다. 혼합 노드 제거 실행기가 아닌 기존 `review_intake.py` → W2 → W1 실행을 사용한다. 컨트롤러와 계약은 CoRA 밖에 유지한다. 연결된 예제 접수 정책은 비활성 상태다. 계약 추가만으로 작업자를 실행하거나 실제 웹 경로를 바꾸거나 과거 요청을 재시작하거나 그래프를 수정하지 않는다. 실행하려면 비공개 활성 운영 설정에서 깨끗한 검토 체크아웃과 실제 재실행 명령을 고정해야 한다.

## 입력과 권한

내보낸 `changes_requested` 검토 기록 하나에 실제 질문·옵션·범위·대화 문맥·답변·검색 버전·소스/스냅샷/그래프 지문·문제 유형·이유가 있어야 한다. 검토는 오류 가능성을 보고하며 명령·정답·수정 파일·예산·승인을 정의하지 못한다. 신뢰된 정책·프로젝트·계약은 변경 불가 입력이다. 기존의 오래되거나 수정 중인 버전 거절·중복 감지·근거 보관·누적 실행 상태는 유지한다. 과거 보고는 진단 근거가 될 수 있지만 조용히 새 검토 기준 버전으로 바뀌지 않는다.

## 실행과 완료

1. 수정 전에 정확한 기준 버전에서 문제를 재현하고 제출 당시 응답과 재현 결과를 함께 보존한다. 데이터·백엔드·모델 제공자 신원을 확인한다. 필수 조건이 없거나 이미 수정된 보고라면 결정을 요청한다.
2. 승인된 설계와 원문 근거로 기대 동작을 정한다. 해석·전파/검색·선택·답변 구성·로컬 모델 검증·화면 표시 중 원인을 찾는다.
3. 열거된 Recall 구현/표시 파일·합성 회귀 검사 파일 하나·관련 구현/설계/마스터 문서만 수정한다. foundation·원본 데이터·그래프 스키마·고정 평가기는 범위 밖이다. 질문/이름에 맞춘 임시 수정이나 근거 검증 약화는 금지한다.
4. 타당한 회귀 사례가 기준 버전에서 실패하고 후보 버전에서 통과함을 보이며 관련 부정·인접 사례를 보존한다. 고정 Recall 품질 검사·전체 검사·공백 검사·필수 브라우저 검사·별도 의미/문서 검토·정확한 커밋의 원격 CI를 수행한다.
5. 동일 질문·옵션·작업 기억 범위·필요한 대화 문맥·데이터로 후보에서 원래 사례를 다시 실행한다. 전체 비공개 전후 답변·추적·원문 참조·실행 신원을 보존한다. 재실행 게이트는 연결을 검사하고 이제 대화 메타데이터 누락도 거절하지만 의미 정확성이나 백엔드의 정직함을 인증하지는 않는다. 문맥이 없으면 차단하며 조용히 새 주제로 바꾸지 않는다.
6. 진단·답변/근거 변화·남은 한계·휴먼 재검토 지침을 포함한 별도 브랜치와 해당 버전에 연결된 보고서를 전달한다. 최종 휴먼 검토와 병합/운영 반영은 사용자 결정이다. 비공개 질문이나 원문 발췌를 공개 저장소용 커밋/보고서에 게시하지 않는다.

작업자와 별도 읽기 전용 검토자는 실제 수정의 타당성을 판단해야 한다. 일반적인 경로 분리와 검사 통과는 격리·모델 품질·의미 정확성의 증명이 아니다. 예제 F1 브라우저 검사는 기존 브라우저 경계만 확인하며 전체 Recall 검토 화면을 인증하지 않는다. 실제 데이터 재실행 명령은 검증하지 않은 과거 API를 가리키는 대신 로컬 환경에 맞게 제공하고 확인해야 한다.

## 한도와 결정

승인된 실행당 최대 **3600초·구현 5회**이며 수정 루프/재개 전체에 누적 적용한다. 접수기와 직접 W1 실행 모두 실행 상태 생성 전에 더 큰 한도를 거절한다. 재시도·중복 제출·메모 변경으로 예산을 자동 갱신하지 않는다. `execution_limits`가 없는 과거 계약은 기존 규칙을 유지한다. 이 계약은 스케줄러를 설치하거나 무한히 새 사례를 배정하지 않는다.

정답이 모호하거나 새 개념/참여자 역할 규칙이 필요하거나 허용 파일 밖의 수정·원문/그래프/스키마/평가기 변경·재실행 필수 조건 부재·예산 소진·병합/운영 반영이 필요하면 사용자 결정을 요청한다. 실패와 부분 결과를 보존한다.

## 첫 사례: Me 누락

보고된 EMNLP 질문과 “Me 누락” 이유를 정답 표지가 아닌 근거로 사용한다. Me가 원문으로 확인된 참여자인지 단순 소유자/범위 기준인지 판단한다. 계약은 두 역할과 무관하게 활성화된 개체를 다루는 인접 합성 사례를 요구한다. 기존 의미 규칙으로 포함 여부를 결정할 수 없다면 코드 수정 전에 대안과 영향을 보고한다. 계약 추가만으로 오류 수정이나 새 실제 데이터 비교가 수행된 것은 아니다.

## 설정과 실행

`projects/cora-recall-answer-repair.example.json`과 `projects/cora-recall-answer-intake.example.json`을 `projects/.local/`의 비공개 운영 설정 템플릿으로 사용한다. 추적된 예제는 비활성 상태로 유지한다. 별도 브랜치의 격리된 깨끗한 대상·정확한 검토 기준 버전·사용 가능한 Python/Chrome 환경·보호된 평가기 경로·`{review}`와 `{evidence}`를 사용하는 고정 실제 데이터 재실행 명령·실제 승인 참조를 제공한다. 전달 저장소/base/head와 정확한 커밋의 CI 게이트를 설정한다. 일반 재실행 스크립트 자리표시자는 의도적으로 동작하는 어댑터가 아니다.

```sh
python3 tools/review_intake.py prepare --review /PRIVATE/review.json \
  --policy projects/.local/cora-recall-answer-intake.json
python3 tools/review_intake.py start --review /PRIVATE/review.json \
  --policy projects/.local/cora-recall-answer-intake.json
```

`prepare`는 고정 입력 묶음을 생성하고 `start`는 조건을 충족한 기록만 준비·실행한다. 상태 조회/재개와 재실행 산출물 규약은 `docs/03-review-json-intake.md`를 따른다. 현재 웹의 `recall_answer` 경로는 여전히 범위 검토 요청을 저장한다. 이 계약만으로 그 경로가 코드 수정을 실행하지는 않는다. 자동 웹 실행 연결과 구체적인 재실행 환경 구성은 후속 통합 작업이며 수정 완료로 주장하지 않는다.

이번 전달 검증: 컨트롤러 검사 146개가 117.236초에 통과했다. 집중 검사는 접수 한도·상태 생성 전 직접 W1 거절·잘못된 한도·대화 문맥 누락 거절을 확인한다. 계약 경로/기준과 영문/한글 절을 검토했으며 공백 검사를 통과했다. 이번 계약 전달에서는 실제 코드 작업자·로컬 LLM·브라우저·원격 CoRA CI를 실행하지 않았다.

## 웹 답변 개발 실행 연결 — 2026-11-18

`quality_workflow.py serve --answer-policy projects/.local/answer-policy.json`은 기존 고정 혼합 노드 정책과 함께 답변·검색 실행을 선택적으로 활성화한다. 추가 정책은 `review_intake.policy_inputs`를 통과하고 `cora-recall-answer-repair-v1`을 지정해야 한다. 별도 고정하므로 경로를 활성화해도 과거 제거 정책 해시를 바꾸거나 기존 접수 기록을 승인하거나 예산을 갱신하지 않는다. 완료된 깨끗한 버전 연결의 새 보고는 `answer_dispatch.py`를 통해 운영자가 준비한 격리 체크아웃의 기존 W2/W1 실행기로 전달된다. 웹 호출자는 명령·경로·예산을 선택하지 못한다. 중복 사례 신원은 내보내기/전송/응답 ID를 제외하며 다시 내보내도 원래 기한을 유지한다. 권한 입력이 바뀌면 결정을 요구한다.

실행 연결기는 먼저 `review_replay_gate.py`로 신뢰된 재실행을 수행하고 비공개 기준 관찰을 작업 입력으로 고정한 뒤 고정 개발 계약을 준비·실행한다. `cora_review_replay.py`는 대상 체크아웃의 CoRA 네이티브 복사본 재실행 명령을 시작해 소스/검토 연결을 추가하며 대상 패키지를 가져오지 않는다. 바깥 실행 기한은 사전 확인/재실행을 포함하고 시간 초과 시 프로세스 그룹을 종료하며 내부 W1 수정 횟수는 최대 5회다. 중단된 작업을 자동 재시작하지 않는다. 내보내기에 안정된 그래프 내용 신원이 있으면 검사한다. 대화 기록이나 검증된 로컬 모델 신원이 없으면 설정을 바꾸거나 수정 완료를 주장하지 않고 차단한다.

상태 조회와 비공개 접수 화면에 개발 상태를 표시한다. 검토를 통과한 W1 후보에 승인된 내용 지문과 연결된 재실행 결과가 있을 때만 수정 후 답변을 표시하며 검토 당시 답변과 이유를 유지한다. 휴먼 재검토·의미 모호성·병합·운영 반영은 별도 결정이다. 브라우저는 검토 상태를 보존하며 새로고침이 과거 기록을 현재 승인으로 바꾸지 않는다. 재실행 관찰만으로 의미 정확성을 승인하지 않는다. 현재 통합 시험의 작업자/브라우저/CI는 합성 대체이며 실제 데이터 네이티브 재실행 시험은 실제 자율 수정과 구분한다. 이번 통합 전달에서는 실제 코드 작업자를 시작하거나 원본 그래프를 수정하지 않았다.
