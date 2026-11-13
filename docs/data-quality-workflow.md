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

