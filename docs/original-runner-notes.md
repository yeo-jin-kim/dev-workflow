<!-- document-language: en -->
> Historical pre-separation notes. Paths/commands below are obsolete; use ../README.md.

# CoRA development loop — first local version

This is an opt-in bounded runner, not a background daemon. No automatic merge,
publication, deployment, theory adoption or Knowledge approval is authorized.

## Run

From the repository root:

```sh
python3 tools/development_loop.py status
python3 tools/development_loop.py run --max-cycles 3 --total-seconds 1800
```

Requires an authenticated `codex` executable on PATH. The installed CLI's
`exec`, workspace-write/read-only sandbox, output-schema and final-message
options are used. No model override or approval bypass is supplied.
Implementation and review are separate fresh CLI sessions, run sequentially.
Run in a dedicated clean checkout; do not concurrently edit that checkout.
Private logs and durable state live in ignored `.local/development-loop/`.

## Contract and completion

A contract fixes goal, allowed scope, criterion IDs and check argument arrays.
Checks run directly, without a shell. Use only trusted contracts: commands execute
with the controller's local permissions. The initial pilot only creates a document
authority audit and proposals; it does not resolve policy conflicts itself.

A worker produces implementation results and any decision requests. The controller
runs every required check, then starts an independent read-only reviewer. Completion
requires every criterion exactly once with a pass and concrete evidence, no blocking
findings, no decision requests, all checks successful, and an unchanged source digest
between checks and review. Digests cover tracked and nonignored untracked files,
deletions, symlinks and modes. Workflow controls are checked for changes too.

A failed check or review feeds the next bounded implementation attempt. Process
errors, malformed output, timeouts, source changes and policy changes never complete.
An exclusive local lock prevents overlapping runners. Logs and attempts survive restart;
interrupted work restarts with a fresh attempt rather than resuming partial processes.
A completed run is reusable only while its source digest remains identical.
Limits apply per invocation; there is no monetary budget metering in this version.
Timeout/interruption terminates the subprocess group. Do not use a shell around
this runner that retries indefinitely.

## Human decisions

Adopted owner decisions are recorded in `workflow/decisions.json` and the relevant
authoritative document. Consult that ledger before repeating an old decision request;
old run states are historical records, not evidence that a resolved decision is pending.

Decisions include conceptual changes, acceptance/evaluation label changes, changing
empirical support requirements, broadening scope, and major cost/quality tradeoffs.
A decision request must describe evidence, alternatives, recommendation and blocked work.
`decision_required` cannot automatically resume. A human response is recorded in a
revised contract, with a new state directory and a reference to the prior decision.
Never interpret no reply as consent. Other milestones can run separately if independent.

## Limits and rollout

Instruction following and semantic review remain fallible: a pass is not proof of
scientific correctness. The controller detects final control-file changes, but it is
not a tamper-proof security boundary against a malicious worker. A production setup
should keep controller/contracts and protected evaluation outside worker write access,
use a separate checkout per task, enforce path scope and protected tests externally,
and add CI/human policy enforcement. Presently allowed paths are reviewer-enforced,
not an OS-level allowlist. Ignored local data changes are outside the source digest.

No automatic next-milestone selection, scheduling, notifications, GUI, spend metering,
or live private-data experiment is included yet. Validate this pilot before adding them.
For later Knowledge goals, require actual generation/negative/abstention evaluations;
the runner's own unit tests alone are not a Knowledge quality gate.

## Mandatory documentation completion gate — 2026-11-05

Every effective contract receives reserved criterion `documentation_sync` from
`tools/development_loop.py`, regardless of task-supplied criteria. Worker and
reviewer must follow [the documentation rule](implementation.md).
Implementation records and related design status must be updated together;
missing/failed documentation review prevents completion. Documentation-only
or genuinely unaffected scope requires an evidence-based explanation. This is
an explicit review gate, not automatic proof of semantic consistency or a Git hook.

---

<!-- document-language: ko -->
# 한국어 번역

> 저장소 분리 전의 과거 기록이다. 아래 경로와 명령은 더 이상 유효하지 않으며 ../README.md를 따른다.

# CoRA 개발 반복 실행기 — 첫 로컬 버전

명시적으로 선택하는 제한된 실행기이며 백그라운드 데몬이 아니다.
자동 병합·게시·배포·이론 채택·Knowledge 승인은 허용되지 않는다.

## 실행

저장소 루트에서 실행한다.

```sh
python3 tools/development_loop.py status
python3 tools/development_loop.py run --max-cycles 3 --total-seconds 1800
```

PATH에 인증된 `codex` 실행 파일이 필요하다. 설치된 CLI의 `exec`,
workspace-write/read-only 샌드박스, output-schema 및 최종 메시지 옵션을 사용한다.
모델 설정을 덮어쓰거나 승인 절차를 우회하지 않는다. 구현과 검토는 각각 새로운 CLI 세션으로
분리해 순서대로 실행한다. 전용의 깨끗한 체크아웃을 쓰고 실행 중 동시에 편집하지 않는다.
비공개 로그와 영속 상태는 Git에서 제외한 `.local/development-loop/`에 둔다.

## 계약과 완료

계약은 목표·허용 범위·기준 ID·검사 인자 배열을 고정한다. 검사는 셸 없이 직접 실행한다.
명령이 컨트롤러의 로컬 권한으로 실행되므로 신뢰할 수 있는 계약만 사용한다.
첫 파일럿은 문서 권한 감사와 제안만 만들며 정책 충돌을 스스로 해결하지 않는다.

작업자는 구현 결과와 필요한 결정 요청을 만든다. 컨트롤러는 필수 검사를 모두 실행한 뒤
독립적인 읽기 전용 검토자를 시작한다. 완료하려면 모든 기준이 정확히 한 번씩 통과하고
구체적 근거가 있어야 하며, 차단 지적·결정 요청이 없고 모든 검사가 성공해야 한다.
검사와 검토 사이의 소스 digest도 같아야 한다. digest는 추적 파일·무시되지 않은 미추적
파일·삭제·심볼릭 링크·모드를 포함한다. 워크플로 제어 파일 변경도 확인한다.

검사 또는 검토 실패는 다음의 제한된 구현 시도로 전달한다. 프로세스 오류·잘못된 출력·
시간 초과·소스 변경·정책 변경을 완료로 처리하지 않는다. 배타적 로컬 잠금으로 중복 실행을
막는다. 재시작 후에도 로그와 시도 기록은 남으며, 중단 작업은 부분 프로세스를 이어 실행하지
않고 새 시도로 시작한다. 완료 실행의 재사용은 소스 digest가 같을 때만 가능하다.
이 버전의 한도는 호출별이며 금액 사용량 계측은 없다. 시간 초과·중단 시 자식 프로세스
그룹을 종료한다. 무한 재시도하는 셸로 이 실행기를 감싸지 않는다.

## 사람의 결정

채택한 사용자 결정은 `workflow/decisions.json`과 관련 권위 문서에 기록한다.
과거 결정 요청을 반복하기 전에 이 원장을 확인한다. 과거 실행 상태는 역사 기록이며,
해결된 결정이 아직 대기 중이라는 근거가 아니다.

결정 대상에는 개념·수용 기준/평가 라벨·경험적 support 요건·범위 확대·주요 비용/품질
절충이 포함된다. 요청에는 증거·대안·권고·막힌 작업을 설명한다.
`decision_required`는 자동 재개할 수 없다. 사람의 답변은 이전 결정을 참조하는 개정 계약과
새 상태 디렉터리에 기록한다. 무응답을 동의로 해석하지 않는다.
서로 독립적인 다른 마일스톤은 별도로 실행할 수 있다.

## 한계와 확대 적용

지시 이행과 의미 검토는 틀릴 수 있으므로 통과가 과학적 정확성의 증명은 아니다.
컨트롤러는 최종 제어 파일 변경을 탐지하지만 악의적 작업자에 대한 변조 방지 보안 경계는
아니다. 실제 운영에서는 컨트롤러·계약·보호 평가를 작업자의 쓰기 권한 밖에 두고,
작업마다 별도 체크아웃을 사용하며, 경로 범위와 보호 검사를 외부에서 강제하고
CI·사람의 정책 집행을 추가해야 한다. 현재 허용 경로는 검토자가 확인하며 운영체제 수준
허용 목록이 아니다. 무시된 로컬 데이터 변경은 소스 digest에 포함되지 않는다.

다음 마일스톤 자동 선택·스케줄링·알림·GUI·금액 계측·실제 비공개 데이터 실험은
아직 포함하지 않는다. 추가하기 전에 이 파일럿을 검증한다. 후속 Knowledge 작업에는
실제 생성·부정 사례·응답 보류 평가를 요구한다. 실행기 단위 검사만으로 Knowledge 품질
게이트를 대신할 수 없다.

## 필수 문서 완료 게이트 — 2026-11-05

작업이 제공한 기준과 관계없이 `tools/development_loop.py`가 모든 유효 계약에
예약 기준 `documentation_sync`를 추가한다. 작업자와 검토자는
[문서 규칙](implementation.md)을 따른다. 구현 기록과 관련 설계 상태를 함께 갱신하며,
문서 검토 누락·실패는 완료를 막는다. 문서만 바꾸거나 실제로 영향이 없는 범위라면
근거를 갖춘 설명이 필요하다. 이는 명시적 검토 게이트이며 의미 정합성의 자동 증명이나
Git 훅은 아니다.
