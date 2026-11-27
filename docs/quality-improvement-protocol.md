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
