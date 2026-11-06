<!-- document-language: en -->
# W2 approved sequential queue

Status: implementation complete; 94 regression tests and all 8 independent-review
criteria passed. Dedicated branch above verified W1; live queue not started.

The operator approves an exact queue snapshot and authority inputs before execution.
A local receipt records the decision reference, queue SHA and project/contract,
protected files, target AGENTS, documentation policy and decision-record hashes.
It additionally pins each clean target HEAD/content manifest, dedicated branch,
and observed remote base SHA; pending work must still match these at dispatch.
It records authorization supplied by the owner; it is not a human-authentication
system. Agents must not create receipts from their own generated suggestions.

Tasks use separate clean target worktrees and distinct publication heads. Only W1
branch_report projects without parent_budget are supported. `depends_on` is a DAG
of verified deliveries, not permission to merge or evidence that predecessor code
was integrated. A task requiring that code needs integration and new approved inputs.
Ready independent tasks run in input order; failures stop this invocation. A blocked
predecessor blocks its dependents. No PR/merge or goal/contract selection occurs.

Queue window/deadline, max_tasks and reserved seconds/cycles are durable. Per-repo
limits aggregate all its tasks. Reservations are made before dispatch and are never
refunded, even after early success. A task's absolute deadline is capped by the
original queue deadline. Restarts do not renew the window or reservation. This is
conservative time/cycle accounting, not monetary measurement or a rolling daily
account across separately approved queues. Use one approved window for a workday.

Queue and W1 target locks serialize cooperative local work. Target locks cover
engine execution, dependency checks, receipt validation and checkpoint writes;
final handoff rechecks all delivered targets under ordered locks. Remote refs
cannot be locked by this local controller. Handoff timestamps describe point-in-time
observations, not permanent freshness; exact refs must be revalidated before merging. Durable dispatch precedes W1 execution.
On restart, a valid terminal W1 receipt can reconcile an interrupted parent update.
A dispatch without a trustworthy terminal receipt needs operator reconciliation;
it is never automatically replayed. Deleting an individual child state is not a
reset. State/receipt files remain trusted controller-owned records; tampering by a
user with filesystem access is outside the isolation claim.

`run` drains the bounded approved queue in the foreground and exits on completion,
attention or exhaustion. It can be invoked by an external scheduler; this delivery
does not install one or claim a resident service. Pending approval is a normal stop.
Status is historical; dispatch revalidates authority hashes and published receipts.

## Operator workflow

1. Prepare explicit W1 contracts/projects and separate clean target worktrees.
   Select task-specific branch_report heads, push CI gates and available browser.
2. Copy `queues/example.json` to a new window file and replace all placeholders.
   Its two-task example is deliberately non-executable until real inputs exist.
   Choose queue/project reservation caps and task budgets; this is the reviewable
   plan the owner approves. No examples here grant approval for live CoRA work.
3. After an actual owner decision, record its reference with `approve`. Receipts
   are exclusive and immutable. Keep approvals/configs outside mutable run state
   and approvals outside target worktrees.
4. Invoke `run` using one stable external state directory. Repeat that invocation
   for recovery/status, not a new directory. The CLI serializes by queue-file
   identity and permanently allocates its state directory and initial run/binding/
   deadline identity. Empty, partial, replaced, missing state or missing allocation
   receipts cannot renew a started window. Missing allocated state
   requires attention, not a regenerated allowance. Concurrent calls exit blocked.
5. Review task reports at `delivered_awaiting_merge`; authorize each concrete merge
   separately. Stop/approval packets include reason, evidence location and options.

```sh
python3 tools/approved_queue.py approve --queue /ABS/approved-window.json --approval /ABS/approvals/window.json --decision-reference 'reference to the actual owner decision'
python3 tools/approved_queue.py run --queue /ABS/approved-window.json --approval /ABS/approvals/window.json --state-dir /ABS/runs/window
python3 tools/approved_queue.py status --queue /ABS/approved-window.json --state-dir /ABS/runs/window
```

Queue/approval/controller or task-authority drift blocks dispatch. Do not edit
receipts/state to clear a gate. An ambiguous dispatch requires inspecting whether
its worker still exists and preserving its logs/branch; W2 deliberately does not
provide a blind retry/approval-bypass switch. A revised window/contract requires
another explicit owner decision. Owner approval recording is trusted operator
input, not proof of the identity behind a typed decision reference.


The first independent audit rejected initial directory-validation order, partial
state reset, missing baseline approval pins, insufficient browser reconstruction,
and overly broad freshness assumptions. These were corrected before publication.
Invalid target-overlapping state paths are rejected before directory creation.
Preapproval attention uses a separate attention receipt and allocates no run.
Started state must retain its original identity and allocation; CLI never adopts
an existing state as a new grant. Browser receipts reconstruct raw DOM results,
version/engine, harness hashes, executable command records and report observations,
rather than trusting a copied digest/pass field. This is consistency validation
of trusted local records, not cryptographic attestation of an adversarial machine.

---

<!-- document-language: ko -->
# 한국어 번역

# W2 승인된 순차 작업 대기열

상태: 구현 완료. 회귀 검사 94개와 독립 검토 기준 8개가 모두 통과했다.
검증된 W1 위의 전용 브랜치에 있으며 실제 작업 대기열은 시작하지 않았다.

운영자는 실행 전에 정확한 대기열 스냅샷과 작업 권한 입력을 승인한다.
로컬 승인 기록에는 결정 참조, 대기열 SHA, 프로젝트/계약·보호 파일·대상 AGENTS·
문서 정책·결정 원장의 해시를 담는다. 깨끗한 대상의 HEAD·내용 manifest·전용 브랜치·
관측한 원격 기준 SHA도 고정하며, 대기 작업은 시작 시에도 이 값과 일치해야 한다.
이 기록은 사용자가 내린 승인을 기록할 뿐 사람의 신원을 인증하는 시스템은 아니다.
에이전트가 스스로 생성한 제안을 승인 기록으로 만들면 안 된다.

작업마다 분리된 깨끗한 작업 트리와 서로 다른 게시 브랜치를 사용한다.
parent_budget이 없는 W1 branch_report 프로젝트만 지원한다.
`depends_on`은 검증된 결과 전달 사이의 DAG이며 병합 권한이나 선행 코드가 통합됐다는
증거가 아니다. 그 코드가 필요한 작업은 통합과 새 승인 입력이 필요하다.
준비된 독립 작업은 입력 순서로 실행하고 실패하면 이번 호출을 중단한다.
선행 작업이 막히면 의존 작업도 막힌다. PR/병합이나 목표/계약 선택은 하지 않는다.

대기열 실행 창·마감 시각·max_tasks·예약 시간/횟수는 영속 상태로 유지한다.
저장소별 한도는 해당 저장소의 모든 작업을 합산한다. 시작 전에 예약하며 일찍 성공해도
환급하지 않는다. 작업의 절대 마감은 원래 대기열 마감 시각을 넘지 않는다.
재시작해도 실행 창이나 예약이 갱신되지 않는다. 이는 보수적인 시간/횟수 계측이며
금액 계측이나 서로 다른 승인 대기열을 합친 이동식 일일 계정은 아니다.
하루 작업에는 하나의 승인된 실행 창을 사용한다.

대기열과 W1 대상 잠금은 협조적인 로컬 작업을 직렬화한다. 대상 잠금은 엔진 실행·
의존성 검사·증거 검증·체크포인트 저장을 포함하며, 최종 전달 전에 정렬된 잠금 아래
모든 완료 대상을 재확인한다. 이 로컬 컨트롤러로 원격 ref를 잠글 수는 없다.
전달 시각은 특정 시점의 관측이며 영구적 최신성을 뜻하지 않는다. 병합 전 정확한 ref를
재검증해야 한다. W1 실행에 앞서 dispatch 상태를 영속 저장한다.
재시작 시 유효한 W1 최종 증거가 있으면 중단된 부모 기록을 복구한다.
신뢰할 수 있는 최종 증거가 없는 dispatch는 운영자 확인이 필요하며 자동 재실행하지 않는다.
개별 자식 상태를 삭제해도 초기화되지 않는다. 상태·승인 기록은 컨트롤러 소유의 신뢰된
로컬 기록이며, 파일시스템 권한을 가진 사용자의 변조는 격리 보장 범위 밖이다.

`run`은 승인된 제한 대기열을 포그라운드에서 처리하고 완료·확인 필요·한도 소진 시 종료한다.
외부 스케줄러가 호출할 수 있지만 이번 구현에서 스케줄러를 설치하거나 상주 서비스를
제공한다고 주장하지 않는다. 승인 대기는 정상적인 중단 사유다.
상태 조회는 과거 스냅샷이며, dispatch 시 권한 해시와 게시 증거를 다시 확인한다.

## 운영 절차

1. 명시적인 W1 계약/프로젝트와 분리된 깨끗한 대상 작업 트리를 준비한다.
   작업별 branch_report 브랜치·push CI 게이트·사용 가능한 브라우저를 선택한다.
2. `queues/example.json`을 새 실행 창 파일로 복사하고 모든 자리표시자를 바꾼다.
   두 작업 예제는 실제 입력이 생기기 전에는 일부러 실행할 수 없게 해 두었다.
   대기열/프로젝트 예약 한도와 작업 예산을 정한다. 이것이 사용자가 검토해 승인할 계획이다.
   이 예제는 실제 CoRA 작업에 대한 승인을 부여하지 않는다.
3. 사용자의 실제 결정이 있은 뒤 `approve`로 참조를 기록한다.
   승인 기록은 배타적으로 생성하고 변경하지 않는다. 승인/설정은 변경 가능한 실행 상태 밖에,
   승인 기록은 대상 작업 트리 밖에 둔다.
4. 고정된 외부 상태 디렉터리 하나로 `run`을 호출한다. 복구/상태 확인에는 같은 호출을
   반복하며 새 디렉터리를 쓰지 않는다. CLI는 대기열 파일 식별자로 직렬화하고 상태 디렉터리와
   최초 실행/입력 연결/마감 식별값을 영구 할당한다. 비어 있거나 일부만 남거나 교체·누락된
   상태 및 누락된 할당 기록으로 이미 시작한 실행 창을 갱신할 수 없다. 할당된 상태의 누락은
   확인이 필요한 문제이며 한도를 재생성하지 않는다. 동시 호출은 차단 상태로 종료한다.
5. `delivered_awaiting_merge`에서 작업 보고서를 검토하고 각 구체적 병합을 별도 승인한다.
   중단/승인 자료에는 이유·증거 위치·선택지를 담는다.

```sh
python3 tools/approved_queue.py approve --queue /ABS/approved-window.json --approval /ABS/approvals/window.json --decision-reference 'reference to the actual owner decision'
python3 tools/approved_queue.py run --queue /ABS/approved-window.json --approval /ABS/approvals/window.json --state-dir /ABS/runs/window
python3 tools/approved_queue.py status --queue /ABS/approved-window.json --state-dir /ABS/runs/window
```

대기열·승인·컨트롤러·작업 권한 입력이 달라지면 dispatch를 막는다.
게이트를 지우려고 승인/상태 파일을 편집하지 않는다. 불명확한 dispatch는 작업자가 아직
존재하는지 확인하고 로그/브랜치를 보존해야 한다. W2는 무조건 재시도나 승인 우회 스위치를
제공하지 않는다. 실행 창/계약을 바꾸려면 사용자의 새 명시적 결정이 필요하다.
승인 기록은 신뢰된 운영자 입력이며, 입력한 결정 참조 뒤에 누가 있는지 증명하지 않는다.

첫 독립 감사는 디렉터리 검사 순서·부분 상태 초기화·승인 기준 버전 고정 누락·부족한
브라우저 증거 복원·과도한 최신성 가정을 지적했다. 게시 전에 수정했다.
대상과 겹치는 잘못된 상태 경로는 디렉터리 생성 전에 거부한다.
승인 전 확인 자료는 별도 기록으로 저장하며 실행을 할당하지 않는다.
시작된 상태는 원래 식별값과 할당을 유지해야 하며 CLI가 기존 상태를 새 한도로 채택하지 않는다.
브라우저 증거는 복사된 digest/통과 필드만 신뢰하지 않고 원본 DOM 결과·버전/엔진·
하네스 해시·실행 파일 명령 기록·보고서 관측을 복원한다. 이는 신뢰된 로컬 기록의 일관성
검증이며 적대적 컴퓨터에서의 실행을 암호학적으로 증명하는 것은 아니다.
