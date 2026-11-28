<!-- document-language: en -->
# Automatic quality improvement protocol

## Status and boundary

Implemented as an experimental controller feature, separate from CoRA. It is not
an installed scheduler and no live model repair has been started by this delivery.
The disabled example is configuration, not execution authorization. Existing W1/W2
contracts, budgets and historical runs are unchanged. Independent candidate review,
human retest, publication and merge remain distinct gates.

`tools/quality_improvement.py` executes: reproduce/evaluate → diagnose → repair →
evaluate the same cases → separate review → revise or await human retest. It runs
only trusted argv arrays from a controller-owned policy. Captured notes and model
traces cannot supply commands, grant approval, change labels or renew budgets.

Each episode has a stable ID under `.local/quality-improvement/`. It records an
absolute deadline (at most 3600 seconds), cumulative repair count (at most 5),
phase inputs, command logs, raw step results, source digests and reviewer feedback.
The target lock is shared with W1/W2. Repeating the episode returns its terminal
state; changing policy cannot replenish its limits. In-flight crashes become
`interrupted`; they do not silently replay a possibly mutating step. Recovery and
new authorization must preserve prior evidence and consumed budgets; there is no
automatic recovery/extension command in this version. Process termination has the
existing runner's up-to-five-second termination grace.

## Evidence and quality gates

The evaluator must return every frozen case ID and expectation digest, the exact
current source digest and dataset digest. Missing cases, changed expectations or
stale results stop the run. A candidate must improve an actual reproduced failure,
preserve every previously passing case, and not disguise failure as deferral.
Review blockers, regressions and non-improvement are fed into the next diagnosis.
Two consecutive non-accepted attempts require a strategy decision. All attempts,
including failed ones, consume the same cumulative limits. No repair is fabricated
when the baseline does not reproduce a failure.

Diagnosis must include reproduction, root cause and evidence; automatic classes
are implementation and prompt-format corrections within existing meaning. A change
to meaning, role policy, expected behavior, provider/model, graph/source data,
approval rules or scope requires an owner decision. The separate review must inspect
root cause, grounding, regressions, scope and implementation/design documentation.
Every review criterion must be boolean true with evidence, no blockers and no
pending decisions. Only then may a fully corrected candidate reach
`awaiting_human_retest`. This protocol does not commit, push, merge or deploy its
worker's candidate. Existing verified delivery/publication gates must be used later.

Controller code, stage schemas, policy, case registry, configured command files and
listed evaluator/data inputs are fingerprinted. Literal allowed target paths, HEAD,
branch and inter-stage content digests are checked. Observed provider/model identities can be required and must remain equal to the
baseline; the CoRA example requires this. Missing/changed identity requires a decision.
This does not attest model-weight bytes or all runtime dependencies. Read-only stages are checked for
changes; the agent adapter also uses read-only CLI mode for diagnosis/review and
workspace-write for repair, in separate invocations with default model settings.
No worker or reviewer subagents are launched by the adapter. These controls are
not OS isolation, authenticated human approval or proof of independent semantic
correctness. Unlisted ignored target files are not covered by the content digest;
original data/evaluators must be explicitly protected and stronger execution isolation
is required for hostile workloads. Partial candidate changes are preserved on failure.

## CoRA adapters and operating instructions

`tools/quality_agent_stage.py` connects installed agent execution for the three
agent stages using controller-owned JSON schemas. `tools/quality_topic_evaluate.py`
invokes CoRA's native evaluator in subprocesses; the controller never imports CoRA.
It combines frozen synthetic expectations with pinned real-source runtime checks.
A real-source pass means no recorded schema/model/resolver/grounding error. It does
**not** establish meaningful topic selection: empty output or deferral on an unlabelled
real source is not a semantic gold answer. Positive frozen gold cases stop universal
empty output from passing the entire suite. Human-labelled real expectations are
still required for stronger semantic coverage. Source segmentation changes can
invalidate the native segment-based source hash and require a deliberate new freeze.

1. Copy `projects/quality-improvement.example.json` and
   `projects/topic-quality-evaluation.example.json` to private controller configuration.
   Select a clean dedicated worktree and literal allowed files from the topic contract.
2. Pin full source manifests and original data; preserve the existing gold labels.
   Replace all absolute-path placeholders, including evaluator/schema/contract paths.
3. Generate the case-digest registry and inspect expectations. This command hashes
   existing expectations; it does not derive correct answers from model output.
4. Record an actual owner scope/budget reference and enable only the trusted policy.
   This does not authorize changing the meaning of topics or extending a prior trial.
5. Run, inspect private evidence, and use the candidate's exact version for human
   retest and existing verified delivery. No background listener or web button was added.

```sh
python3 tools/quality_topic_evaluate.py freeze --config projects/.local/topic-evaluation.json --output projects/.local/topic-cases.json
python3 tools/quality_improvement.py run --policy projects/.local/topic-quality.json
python3 tools/quality_improvement.py analyze-topics --report PRIVATE_CAPTURED_RESULTS.json --output .local/NEW_ANALYSIS.json
```

The agent adapter and evaluator use inherited process groups so the controller's
command deadline covers their child commands. Required model/server/environment
capabilities must already exist; missing capabilities remain explicit failures.
The supplied contract is a scope template, not a fresh live execution approval.

## Verification and limits

Synthetic tests exercise actual temporary Git targets and subprocess stage adapters,
review feedback, regression/deferral/coverage/label guards, cumulative limits and
terminal deduplication. Mocked agent calls check sandbox roles and preservation of
default model settings; they are not real agent quality trials. Actual captured CoRA
results were ingested: 30 sources, 17 with recorded source-grounding-related failures.
The analysis explicitly sets `root_cause_proven=false` and
`semantic_quality_accepted=false`. Classification localizes symptoms; reproduction
and a justified diagnosis must still establish their cause. No original graph,
source data, active topic pool or CoRA code was changed by this controller delivery.
See `docs/implementation.md` for final test and delivery-review evidence.


Prior phase directories are content-hashed after commands exit. Every later check and retest validates the complete recorded file set, including inputs, process logs, native results and agent outputs. Modified, missing, added or symlink evidence invalidates the candidate; a stored hash without rechecking is insufficient.


### Live experiment timeout configuration — 2026-11-26

Per-step limits may be configured up to 3600 seconds. Each command is still capped by the remaining cumulative episode deadline; this does not renew time or repair cycles. This permits pinned 30-source evaluations to complete within the owner-approved 60-minute experiment.


### Owner-approved semantic topic evaluation — 2026-11-27

The native CoRA evaluator now reports `semanticVersion: 1` and source-grounded `semanticStatus` (`pass`, `fail`, `needs_review`). The controller uses this verdict rather than diagnostic `exactMatch`; ambiguity maps to `deferred` and cannot satisfy complete acceptance. Semantic fixtures refuse fallback to the old exact-match grade. Evaluation-model completion identities are included in the observed model binding, and the example policy protects the new native semantic evaluator alongside the fixtures and evaluation command.

This is an explicitly owner-approved evaluation-policy revision, not a worker changing labels to pass. The original failed episode, source text and diagnostic expected names remain unchanged. New semantic target descriptors define referent/activity/scope and protected explicit identifiers. A new episode requires fresh frozen expectations; the old terminal state and consumed budget are not reset. The same local model in a separate call is not independent human semantic proof. No automatic merging, graph approval or correction of the previous 17 real-source failures is claimed.


Validation: controller full suite **184 tests passed**; focused quality/adapter suite **19 passed in 17.307s** after the final model-identity binding update. Native CoRA `5540e8f` passed 596 regression tests and all 8 live synthetic semantic cases; the exact-name customer-work diagnostic remained false while the semantic verdict passed. No new unattended 30-source repair episode was run.


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

# 자동 품질 개선 프로토콜

## 상태와 경계

CoRA와 분리된 실험적 컨트롤러 기능으로 구현했다. 설치된 스케줄러는 아니며 이번 작업에서
실제 모델 수정 작업을 시작하지 않았다. 비활성 예제는 설정이며 실행 승인이 아니다. 기존
W1/W2 계약·예산·과거 실행은 유지한다. 별도 후보 검토·사람 재시험·게시·병합은 서로 다른
게이트로 남긴다.

`tools/quality_improvement.py`는 재현/평가 → 원인 검토 → 수정 → 동일 사례 재평가 → 별도
검토 → 재수정 또는 사람 재시험 대기를 실행한다. 컨트롤러 소유 정책의 신뢰하는 명령 인자
배열만 실행한다. 접수 메모나 모델 기록은 명령·승인·정답 변경·예산 갱신의 근거가 될 수 없다.

각 작업은 `.local/quality-improvement/` 아래 고정 ID를 사용한다. 최대 3600초의 절대
마감, 최대 5회의 누적 수정, 단계 입력·명령 기록·원본 단계 결과·소스 다이제스트·검토 지적을
보존한다. W1/W2와 대상 잠금을 공유한다. 같은 작업을 재호출하면 종료 상태를 반환하며 정책을
바꿔 한도를 보충할 수 없다. 실행 중 중단은 `interrupted`로 남겨 변경 가능성이 있는 단계를
조용히 재실행하지 않는다. 복구·추가 승인은 과거 증거와 사용 예산을 보존해야 한다. 이번 버전에는
자동 복구·한도 확대 명령이 없다. 프로세스 종료에는 기존 실행기의 최대 5초 종료 유예가 적용된다.

## 증거와 품질 조건

평가기는 고정 사례 ID·기대 결과 다이제스트 전체와 정확한 현재 소스·데이터셋 다이제스트를
반환해야 한다. 사례 누락·정답 변경·오래된 결과는 실행을 중단한다. 후보는 실제로 재현된 실패를
개선하고, 이전 통과 사례를 모두 유지하며, 실패를 보류로 바꿔 숨기지 않아야 한다. 검토 지적·회귀·
개선 없음은 다음 원인 검토로 자동 전달한다. 두 번 연속 수락되지 않은 시도는 전략 결정을 요구한다.
실패를 포함한 모든 시도는 동일한 누적 한도를 사용한다. 기준 버전에서 실패가 재현되지 않으면
수정거리를 만들어내지 않는다.

원인 검토에는 재현·원인·근거가 필요하다. 자동 수정은 기존 의미를 유지하는 구현·프롬프트 형식
교정으로 제한한다. 의미·역할 정책·기대 동작·제공자/모델·그래프/원문·승인 규칙·작업 범위 변경은
사용자가 결정한다. 별도 검토는 원인·근거·회귀·범위와 구현/설계 문서를 확인해야 한다. 모든 검토
기준이 근거와 함께 boolean true이고 지적·결정 대기가 없어야 한다. 이 조건을 통과하고 실패가 모두
해결된 후보만 `awaiting_human_retest`로 이동한다. 이 프로토콜은 작업자의 후보를 commit/push·
병합·배포하지 않는다. 이후 기존의 검증된 전달·게시 게이트를 사용해야 한다.

컨트롤러 코드·단계 스키마·정책·사례 목록·설정된 명령 파일·명시된 평가기/데이터 입력의 지문을
보존한다. 명시적인 대상 파일 경로·HEAD·브랜치·단계 사이 내용 다이제스트를 검사한다. CoRA 예제는 관찰한 제공자·모델 식별자가 기준 버전과 같아야 하며 누락·변경 시 결정을 요구한다.
이것이 모델 가중치 바이트나 모든 실행 의존성을 증명하지는 않는다. 읽기 전용
단계의 변경을 확인하며, 에이전트 연결기는 원인 검토/재검토에 read-only, 수정에 workspace-write
CLI 모드를 별도 호출로 사용하고 기본 모델 설정을 유지한다. 연결기는 작업자나 검토자 하위
에이전트를 시작하지 않는다. 이 통제는 운영체제 격리·인증된 사용자 승인·독립적인 의미 정확성의
증명이 아니다. 목록에 없는 무시된 대상 파일은 내용 다이제스트에 포함하지 않으므로 원문·평가기
파일을 보호 대상으로 명시해야 하며, 적대적 작업에는 더 강한 실행 격리가 필요하다. 실패 시 부분
수정 후보를 보존한다.

## CoRA 연결과 사용 순서

`tools/quality_agent_stage.py`는 컨트롤러 소유 JSON 스키마로 설치된 에이전트의 세 단계를
연결한다. `tools/quality_topic_evaluate.py`는 하위 프로세스로 CoRA 고유 평가기를 실행하며
컨트롤러는 CoRA 패키지를 가져오지 않는다. 고정 합성 정답과 고정 실원문의 실행 검사를 결합한다.
실원문 통과는 기록된 형식·모델·조회·근거 오류가 없다는 뜻이며 의미 있는 토픽 선정의 증거는
**아니다**. 정답이 없는 실원문의 빈 출력·보류는 의미 정답이 아니다. 고정 양성 정답 사례가 전체
출력을 비워 모든 검사를 통과하는 것을 막는다. 더 강한 의미 검증에는 사람이 정답을 정한 실원문이
필요하다. 원문 분할을 바꾸면 고유 평가기의 구간 기반 원문 해시가 달라져 의도적인 새 고정이 필요할
수 있다.

1. `projects/quality-improvement.example.json`과 `projects/topic-quality-evaluation.example.json`을
   비공개 컨트롤러 설정으로 복사한다. 깨끗한 전용 작업 폴더와 토픽 계약의 허용 파일을 선택한다.
2. 전체 원문 manifest와 원본 데이터를 고정하고 기존 정답을 보존한다. 평가기·스키마·계약을 포함한
   모든 절대 경로 자리표시자를 바꾼다.
3. 사례 다이제스트 목록을 생성하고 기대 동작을 검토한다. 이 명령은 기존 기대 동작을 해시할 뿐
   모델 출력에서 정답을 만들어내지 않는다.
4. 실제 사용자 범위·예산 승인 참조를 기록하고 신뢰하는 정책만 활성화한다. 이는 토픽 의미 변경이나
   과거 시험의 한도 확대를 허용하지 않는다.
5. 실행하고 비공개 증거를 검토한 뒤 정확한 후보 버전으로 사람 재시험과 기존 검증된 전달을 수행한다.
   백그라운드 수신기나 웹 버튼은 추가하지 않았다.

```sh
python3 tools/quality_topic_evaluate.py freeze --config projects/.local/topic-evaluation.json --output projects/.local/topic-cases.json
python3 tools/quality_improvement.py run --policy projects/.local/topic-quality.json
python3 tools/quality_improvement.py analyze-topics --report PRIVATE_CAPTURED_RESULTS.json --output .local/NEW_ANALYSIS.json
```

연결기와 평가기는 상속된 프로세스 그룹을 사용해 컨트롤러 명령 마감이 하위 명령에도 적용되도록 한다.
필요한 모델·서버·환경은 이미 존재해야 하며 기능이 없으면 실패로 남긴다. 제공한 계약은 범위 템플릿이며
새로운 실제 실행 승인이 아니다.

## 검증과 한계

합성 검사는 실제 임시 Git 대상과 하위 프로세스 단계 연결기, 검토 지적 전달, 회귀·보류·사례 누락·
정답 변경 방지, 누적 한도·종료 상태 중복 방지를 다룬다. 모의 에이전트 호출은 실행 모드와 기본 모델
설정 유지를 검사하며 실제 에이전트 품질 시험은 아니다. 실제 CoRA 결과도 접수했다. 원문 30개 중
17개에 원문 근거와 관련된 실패가 기록돼 있었다. 분석은 `root_cause_proven=false`,
`semantic_quality_accepted=false`를 명시한다. 분류는 증상의 위치를 좁힐 뿐 원인을 확정하려면
재현과 근거 있는 원인 검토가 필요하다. 이번 컨트롤러 작업에서 원본 그래프·원문·실제 토픽 pool·
CoRA 코드는 변경하지 않았다. 최종 검사와 전달 검토 증거는 `docs/implementation.md`를 참고한다.

명령이 끝난 뒤 이전 단계 폴더의 내용 해시를 기록한다. 이후 검사와 재시험에서는 입력·프로세스 로그·고유 평가 결과·에이전트 출력을 포함한 전체 파일 목록을 다시 대조한다. 수정·누락·추가·심볼릭 링크 증거는 후보를 무효화한다. 해시를 저장만 하고 대조하지 않는 것은 충분하지 않다.

### 실제 실험 시간 제한 설정 — 2026-11-26

단계별 제한은 최대 3600초까지 설정할 수 있다. 각 명령은 계속 누적 실험의 남은 시간으로 제한되며, 시간이나 수정 횟수를 갱신하지 않는다. 사용자 승인 60분 실험 안에서 고정 원문 30개 평가를 완료할 수 있도록 한다.

### 사용자 승인 토픽 의미 평가 — 2026-11-27

CoRA 자체 평가기는 이제 `semanticVersion: 1`과 원문 기반 `semanticStatus`(`pass`, `fail`, `needs_review`)를 보고한다. 실행기는 진단용 `exactMatch` 대신 이 판정을 사용한다. 모호함은 `deferred`로 전달하며 전체 승인 조건을 충족하지 못한다. 의미 평가 사례를 기존 정확 일치 판정으로 대체하지 않는다. 평가 모델 응답의 식별 정보도 관측 모델 고정 검사에 포함하며 예제 정책은 기존 사례·평가 명령과 함께 새 의미 평가기를 보호한다.

이는 사용자가 명시적으로 승인한 평가 정책 변경이며 작업자가 통과하려고 정답을 바꾼 것이 아니다. 과거 실패 실험·원문·진단용 예상 이름은 유지한다. 새 의미 대상 설명은 대상·활동·범위와 보호된 명시적 식별 정보를 정의한다. 새 실험에는 새 고정 예상 기준이 필요하며 과거 종료 상태와 사용 예산은 초기화하지 않는다. 같은 로컬 모델의 별도 호출은 독립적인 사람의 의미 검증이 아니다. 자동 병합·그래프 승인·과거 실제 원문 오류 17건의 수정을 주장하지 않는다.

검증: 실행기 전체 검사 **184개 통과**, 최종 모델 식별 고정 변경 후 품질·연결 집중 검사 **19개 통과(17.307초)**. CoRA `5540e8f`는 회귀 검사 596개와 실제 합성 의미 평가 8개를 통과했다. 고객 업무의 이름 정확 일치 진단은 false를 유지하고 의미 판정은 통과했다. 새로운 원문 30개 무인 수정 실험은 실행하지 않았다.

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
