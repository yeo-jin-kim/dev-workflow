<!-- document-language: en -->
# Reviewable delivery workflow design

**Status, 2026-11-05:** W1 revision 2 implementation candidate exists in the separate development checkout. Actual Chrome adapter, durable evidence/state and branch publisher are implemented as a candidate. The real pilot exhausted three cumulative cycles and remains unaccepted; an additional authorized trial is required. PR creation and scheduler are not implemented or activated. The contract and frozen
acceptance scenarios are in `contracts/dev-workflow/W1-reviewable-delivery.*`.

## Existing behavior and proposed boundary

`tools/development_loop.py` already runs bounded worker/check/reviewer cycles,
locks a target, injects documentation review and rejects overlapping controller/
target trees. It records external logs and detects some target/control changes.
Its budgets reset per invocation, control fingerprints enumerate specific files,
and `complete` means local checks/review rather than remote publication readiness.
`tools/evaluate_f1.py` checks F1 evidence after a parent supplies actual browser
results; it is project-specific and does not provide a general browser driver.

W1 extends these mechanisms without importing target source or moving orchestration
into CoRA. The worker edits task files; the read-only reviewer judges fixed
criteria; a controller-owned verifier records observations; a separate publisher
handles authorized Git/GitHub side effects. This is a process/ownership boundary,
not proof of OS isolation from hostile code. Trusted local checks remain trusted
code; unattended use does not grant extra filesystem or network permissions.

## Evidence identity

Capture run/project/contract IDs; target root, repository identity, base/head refs
and commits; tracked/nonignored content/modes; relevant configuration, dependency
locks, generated runtime and fixture hashes; controller and protected-evaluator
versions; check argv/cwd/environment; timestamps/deadlines/exit codes; raw artifacts.
Keep Git commit identity distinct from content/tree identity. A commit does not
by itself prove all nonignored working files were tested or reviewed.

Every check/browser/review/publication/remote-check observation references its
input manifest. Evidence is append-only by attempt; invalidation creates a new
observation, never rewrites the old attempt to pass. Define dependencies explicitly:
source/runtime/fixture changes rerun affected execution; doc changes require final
doc review; acceptance/control changes stop for decision. Reuse unchanged evidence
only with verified input equality and recorded rationale. Before publication,
confirm the reviewed content is exactly the candidate, with no hidden/unrelated
staged files. Before owner handoff, verify exact head and relevant target/merge
state match the successful remote checks. Target movement requires fresh integration
review/validation where affected, never a blind merge or force push.

Evidence files remain outside targets and are excluded from publication by default.
The publisher uses explicit reviewed task paths and retains unrelated original
checkout contents. Owner-facing reports and optional public PR descriptions contain concise validation summaries,
not private raw sources or full execution logs.

## Default delivery and owner handoff

`branch_report` is the default. PR support may be opted into explicitly; it is
not required to complete W1 and is not automatically activated on missing gates.
The report binds repository, source and target refs/SHAs, comparison link and
summary, local/browser/review/remote evidence, limits, unresolved findings and
proposed merge action. Report generation is durable and retryable. Updating it
creates a new version; it does not silently carry approval over to a new source
or target commit. The real pilot must demonstrate zero PR creation/update calls
in default mode, while preserving all independent-review and CI requirements.

## Proposed phase machine

Names below describe W1; existing state formats are not silently migrated.

| Phase / outcome | Required transition |
| --- | --- |
| `preflight` | Freeze inputs/authorization, prepare isolated baseline, probe required check/browser/GitHub capabilities and time allocation. |
| `implementing` | Worker follows fixed task and prior failure evidence; no contract changes or publication. |
| `checking` | Execute trusted task checks; deterministic failure returns to implementation within cumulative budget. |
| `browser_verifying` | Run project harness in actual supported browser and collect bound raw observations. |
| `reviewing` | Independent reviewer inspects actual diff, negative cases, records and docs. Rejection returns to implementation. |
| `locally_accepted` | All local required evidence and review correspond to the current candidate. This does not mean published or merge-ready. |
| `publishing` | Idempotent commit/push and version-bound report; confirm repo/base/head and side-effect receipts. |
| `remote_checking` | Observe required named gates on exact revision and integration state; failure returns logs to repair. |
| `reporting` | Atomically create/recover the deterministic versioned report; ready state is persisted only after report receipt succeeds. |
| `ready_for_merge_approval` | Validated pushed branch, merge-decision report and successful current required push gates; actual merge requires owner authorization. |
| `decision_required` | Persist question/options/impact/recommendation and explicit authorization requirement. |
| `capability_blocked` | Required tool/environment unavailable after bounded recovery; include reproducible diagnostic and next action. |
| `budget_exhausted` | Preserve cumulative usage and all attempts; do not implicitly replenish on restart. |
| `publication_blocked` | Safe file scope/remote identity or credentials unavailable; retain local artifacts, no unsafe push. |
| `incomplete_published` | Safe reviewed task changes saved on a dedicated branch with version-bound report, failed/missing gates visibly retained. |

An incomplete publication is a separate receipt from its originating decision,
capability or budget outcome: preserve both, rather than overwriting the reason
with a generic published status. Existing historical `complete` states retain their
old meaning; report legacy local acceptance explicitly instead of certifying new
publication gates retroactively. No automatic transition performs a target merge.

## Browser capability and adapter

Use a project-independent adapter protocol with explicit command/capability and
result schema. The target owns its test harness/fixture; the controller starts it,
launches a real available supported browser and saves results with input identity.
Probe a small actual execution during preflight. Do not assume app-only computer
use tools are exposed to a standalone CLI. Choose the concrete local backend from
verified installed capabilities during implementation; record optional prerequisites.
A manually copied DOM result can support a disclosed manual run, but cannot pass
W1's unattended pilot. Node-only JS or screenshots do not count as actual-browser
execution. Browser availability failure blocks required route completion honestly.

## Publication, remote repair and recovery

Bind publisher authorization to project/repository, remote identity, dedicated
head and expected base. Read-only credentials/status probes precede worker time.
Implementation workers never publish. A final controller check verifies reviewed
paths and current manifest, then records commit, push and report receipts separately (plus PR receipt only in opted-in mode).
Inspect the remote after ambiguous network outcomes before retrying: the operation
may already have succeeded. Preserve branch identity and versioned report history across repairs; no duplicate commits,
force push, deletion or unrelated staging. Existing owner per-delivery publication
policy also applies to incomplete work, with truthful failed/missing gate status.
Safe publication itself must be established before publishing incomplete changes.

Default mode requires configured push gates, with their exact head/integration
identities. No pull-request event or PR identity is needed. Optional PR mode must
be explicitly selected for a project/task. If the repository enforces PR-only
gates, return an actionable configuration decision without silently bypassing
the gate or creating a PR. Define required gate names/events in preflight. Never treat absent,
pending, cancelled or unknown gates as passed. A missing test dependency is a
routine repair within scope; changing the test's expectations is a protected
criterion decision. Remote failures feed the same bounded repair/review chain;
new commits invalidate older remote success. Poll at bounded intervals and retain
last known state at timeout. A timeout cannot cancel the need for remote evidence.

Checkpoint durable cumulative cycle/time use before phases and side effects.
Include worker, verification, browser, review, publication and remote waits, plus
restarts. Monotonic deadlines enforce a running phase; persisted usage and wall
timestamps conservatively account for downtime. Specify crash handling/clock
anomalies rather than resetting the allowance. Terminate local child process
groups on timeout and reserve time for review/finalization. Monetary/token metering
is not provided; do not imply the wall-clock limit is a monetary spending cap.

## Bootstrap, pilot and completion

The current controller cannot target itself. Preserve that guard. Maintain this
implementation in an isolated dev-workflow development checkout while the owning
contract/evaluator manifest and evidence stay outside worker control; freeze these
inputs before implementation. Do not enable a project configuration until actual
bootstrap/capability preparation exists. Fixed hashes detect accidental/unauthorized
changes; path separation alone is not a secure protected-test service.

Run fault scenarios W01-W18 in synthetic repositories/local bare remotes, preserving
mock/real distinctions. Then execute the constrained CoRA state-type invariance
regression task from the W1 contract, including actual browser evidence, checks,
independent review, real GitHub branch push/remote validation and report generation, without manual
stage handoffs. The existing CoRA checkout and source behavior remain unchanged.
Independent review assesses this design, final implementation, actual negative
runs and documentation. Missing capabilities or manual completion yield partial
implementation, not a claim of fully automatic delivery.


## Implementation candidate anchors — 2026-11-05

- `tools/delivery_evidence.py`: canonical content manifests, external raw command
  records, cumulative persisted deadline/cycles, actual Chrome headless execution
  of a loopback project harness, runtime/fixture/result/version bindings.
- `tools/delivery_loop.py`: explicit schema-version-2 opt-in runner, original
  self-target guard, preflight probes, worker/check/browser/read-only review,
  stale-evidence invalidation and safe incomplete-delivery handling.
- `tools/delivery_publish.py`: exact-path staging, crash-aware commit/push receipts,
  candidate-only base integration followed by revalidation, exact-head named push
  CI and append-only external JSON/Markdown merge-decision reports.
- `schemas/publication.schema.json`: independent incomplete-publication safety
  review, separate from failed semantic acceptance. Time exhaustion cannot grant
  extra review budget; if safe publication cannot be established it stays blocked.
- `projects/cora-w1-pilot.json`, `contracts/cora/W1-state-type-pilot.json`: narrow
  authorized real trial. Existing W1/F1 protected definitions remain unchanged.
- `tests/test_delivery_loop.py`: real temporary Git/bare-remote operations,
  explicit synthetic model/GitHub faults, and actual Chrome execution where
  available. Synthetic fixtures are not the real-pilot evidence.

Existing legacy CLI/tests are unchanged. Controller core remains Python 3.9+
standard library; adapters require installed Chrome, Codex CLI, gh and task test
Python dependencies. Chrome is an actual headless browser, with separate fresh
profile and loopback harness; no OS/browser sandbox weakening flags are used.
No app-only computer-use interface is assumed. PR mode is optional in the
contract but not implemented here; selecting it returns a decision request and
cannot silently activate PR creation. Automatic target merge stays absent.

Each run pins the complete controller manifest and owning protected files, so
controller edits require a new linked run rather than silently adopting new
policy. Reports/command/browser artifacts remain in the explicitly external
state directory. Final source/docs changes invalidate acceptance; report generation
itself is external and does not create a source-review feedback loop. Published
branches are incomplete until required push gates succeed and the exact base/head
are reconfirmed. Pending remote gates/clock anomalies exhaust or block the run
honestly, preserving all attempts and any safe incomplete publication receipt.

### Bootstrap corrections and linked validation

The first actual pilot produced an internally inconsistent reviewer output:
all criteria/verdict passed, but decision_requests contained a statement saying
there was no new decision. The controller correctly withheld completion, then
publication-safety review timed out; no pass was fabricated. An independent
format-only clarification returned the same semantic findings with an empty
decision list. Original stopped state/logs remain unchanged.

The implementation now treats contradictory pass/blocker/decision output as
invalid formatting and requests one independent clarification, preserving both
artifacts. It never retries a valid negative semantic judgment merely to obtain
pass, removes decisions itself, or treats generated text as owner authorization.
Malformed result types fail rather than throwing an unhandled acceptance error.
Browser harness hashes are compared before/after actual execution; mutation
invalidates results. Read-only remote probes have one durable infrastructure
retry; writes rely on side-effect identity inspection, not blind retry.

A separate explicitly linked bootstrap revalidation profile preserves the exact
pilot task contract and copies the original cumulative deadline/cycle usage.
Linking is allowed only from accepted runs, or a contradictory-pass stop with
independently corrected review bound to unchanged original reviewed contents.
Genuine unresolved decisions cannot be bypassed. Both prior state and resolution
are pinned; old states are not rewritten, budgets not replenished, and the new
isolated pilot still performs its own full worker/check/browser/review/publication
chain. `projects/cora-w1-pilot-v2.json` records this concrete linked validation;
its absolute evidence paths are host-specific, not a portable default.


### Source-review fixes and current verification boundary

A separate code reviewer requested stronger environment binding, retention of
pending CI at timeout and crash-idempotent reports. Command records now contain
the inherited environment fingerprint (no credential values), resolved executable
content identity and deterministic project dependency probes. Review/publication
compare the current environment/dependency binding. Browser failures carry exact
raw log, execution-record and project-observation paths back to the worker.
This corrects the missing diagnosis context found in the real trial.

CI saves its last known result on every poll. Report IDs derive from immutable
run/source/target/review/CI identity; orphan JSON/Markdown receipts are recovered
without duplicate versions. Reports include change goal, task summaries, all
verification references, cumulative budget and linked failure history. A failed
report cannot persist a ready status. Starting new implementation/review clears
previous acceptance; the publisher independently rejects a current negative
review even if an old digest survives. Parent-budget allocation also has an
exclusive sidecar receipt, preventing new state directories from multiplying the
same allowance; original histories stay untouched.

Latest local evaluation: 58 tests passed, including real Chrome and real temporary
Git/bare-remotes with explicitly synthetic model/GitHub fault responses. W02-W16
and W18 currently pass those mapped rehearsals; W01/W17 remain incomplete because
the actual CoRA task never reached accepted publication/push CI. A new directory
or fabricated pass cannot resolve that. No PR or target merge was performed.


Linked allowance claims use a fully written, atomically linked journal containing
initial state and source/controller/project/external-policy bindings. A crash
before child persistence can restore that exact run ID and budget; activation
occurs only after state persistence. Once active, missing/deleted state is not
a license to regenerate allowance. Distinct child directories cannot reuse the
same parent grant. Current acceptance remains incomplete at the exhausted live
trial; manual parent WIP preservation does not satisfy autonomous publication.

Both sides of child-state persistence use one original journal-binding function.
Controls are durable and guarded before activation, with a final binding recheck.
Tests cover unchanged recovery and changed-policy rejection after persistence.
Latest local verification is 58 passed; live W01/W17 remain incomplete.

Final independent re-review found the corrected source crash/binding paths
sound under the recorded tests. Overall W1 acceptance is still blocked by the
missing successful real pilot and explicit owner authorization for further trial.


### Additional trial: provenance loop remains a live acceptance failure

The owner authorized a fresh bounded 1800-second/three-cycle trial, with prior
failures linked in `projects/cora-w1-approved-trial.json`. It consumed all three
cycles: checks and real Chrome/frozen F1 validation passed each time, while
independent documentation review rejected stale provenance. W01/W17 remain
incomplete. The cumulative actual history is six cycles; no PR/target merge.

Document updates precede verification, so final exact-source check results belong
in external run evidence and the final report. Target documents describe current
behavior/progress/limits and may cite explicitly historical observations. They
must link stable run evidence rather than embed a self-referential final digest.
Current acceptance always uses current manifests and executed evidence; earlier
passes never replace current verification. Reviewer guidance now makes this
separation explicit without removing documentation or semantic gates. This
correction has no successful post-fix actual trial yet. Earlier status entries
above are chronological evidence, not current acceptance.


Review phase caps are separate from total allowance. Missing review after a phase
cap is retried only within the same persistent deadline/cycle counter. Historical
misclassified review timeouts may link once through protected raw timeout/input
records, unchanged source, no final review/decisions and remaining budget. This
uses the existing crash-safe exclusive journal; recovery never resets limits.
The owner-approved 60-minute/five-cycle profile and its recovery profile record
this bounded case. A completed negative review cannot use timeout recovery.


### Bounded actual recovery handoff

With the reviewed timeout/provenance corrections, the final child completed all
actual stages through exact-head CI and immutable report at CoRA 81b1e21, using
cumulative cycle two of the original 3600-second/five-cycle grant. Bootstrap
manual WIP preservation/controller repairs preceded that child and are explicitly
retained as setup/failure history; no manual copying or publication completed a
missing stage inside the final child. Task review passed; W1 final evaluator and
milestone review are separate. CoRA and controller target branches await owner
merge authorization. Historical incomplete entries above remain stage records.


Final acceptance: frozen W1 evaluation passed **18/18**, all **63 tests** passed,
and the independent final milestone audit passed **12/12 criteria** with no
blockers/decisions. This establishes the constrained W1 revision-2 milestone,
with the bootstrap/manual boundary above preserved. Merge remains owner-gated.

---

<!-- document-language: ko -->
# 한국어 번역

# 검토 가능한 개발 결과 전달 워크플로 설계

**2026-11-05 상태:** W1 revision 2 구현 후보가 별도 개발 체크아웃에 있다.
실제 Chrome 어댑터·영속 증거/상태·브랜치 게시기를 후보로 구현했다.
실제 파일럿은 누적 3회를 소진해 아직 수용되지 않았으며 추가 승인 시험이 필요하다.
PR 생성과 스케줄러는 구현·활성화하지 않았다. 계약과 고정 수용 사례는
`contracts/dev-workflow/W1-reviewable-delivery.*`에 있다.

## 기존 동작과 제안 경계

`tools/development_loop.py`는 이미 제한된 작업자/검사/검토 사이클, 대상 잠금,
필수 문서 검토 주입, 컨트롤러/대상 중첩 거부를 제공한다. 외부 로그를 기록하고 일부 대상/
제어 파일 변경을 탐지한다. 한도는 호출마다 초기화되고 제어 지문은 특정 파일을 나열한다.
`complete`는 원격 게시 준비가 아니라 로컬 검사/검토 완료를 뜻한다.
`tools/evaluate_f1.py`는 부모가 실제 브라우저 결과를 제공한 뒤 F1 증거를 검사하는
프로젝트 전용 도구이며 일반 브라우저 드라이버는 아니다.

W1은 대상 소스를 가져오거나 CoRA에 실행 제어를 넣지 않고 이 기능을 확장한다.
작업자는 작업 파일을 편집하고 읽기 전용 검토자는 고정 기준을 판단한다.
컨트롤러 소유 검증기는 관측을 기록하고 별도 게시기가 승인된 Git/GitHub 부수 효과를 처리한다.
이는 프로세스/소유권 경계이며 적대적 코드에 대한 OS 격리의 증명은 아니다.
신뢰된 로컬 검사는 여전히 신뢰해야 하는 코드이며 무인 사용으로 파일시스템/네트워크 권한이
추가 부여되지는 않는다.

## 증거 식별값

실행/프로젝트/계약 ID, 대상 루트·저장소 식별값·기준/작업 ref와 커밋, 추적/무시되지 않은
내용과 모드, 관련 설정·의존성 잠금·생성 런타임/fixture 해시, 컨트롤러/보호 평가 버전,
검사 argv/cwd/환경, 시각/마감/종료 코드, 원본 자료를 수집한다.
Git 커밋 식별값과 내용/트리 식별값은 구분한다. 커밋만으로 무시되지 않은 모든 작업 파일이
검사·검토됐다고 입증할 수 없다.

모든 검사/브라우저/검토/게시/원격 검사 관측은 입력 manifest를 참조한다.
증거는 시도별로 추가만 한다. 무효화되면 새 관측을 만들며 옛 시도를 통과로 다시 쓰지 않는다.
의존성을 명시한다. 소스/런타임/fixture 변경은 영향 실행을 다시 수행하고 문서 변경은 최종
문서 검토를 요구하며 수용/제어 변경은 결정을 기다린다. 입력이 같음을 검증하고 이유를
기록했을 때만 변경 없는 증거를 재사용한다. 게시 전 검토 내용과 후보가 정확히 같고 숨은/
무관한 staged 파일이 없는지 확인한다. 사용자 전달 전 정확한 HEAD와 관련 대상/병합 상태가
성공한 원격 검사와 일치하는지 확인한다. 대상 이동은 영향 범위의 새 통합 검토/검증을 요구하며
무조건 병합이나 강제 push로 대체하지 않는다.

증거 파일은 대상 밖에 두고 기본적으로 게시에서 제외한다. 게시기는 명시적으로 검토한 작업
경로만 사용하며 원본 체크아웃의 무관한 내용은 유지한다. 사용자 보고서와 선택적인 공개 PR
설명에는 간결한 검증 요약을 담고 비공개 원문이나 전체 실행 로그는 넣지 않는다.

## 기본 전달과 사용자 인계

기본값은 `branch_report`다. PR 지원은 명시적으로 선택할 수 있지만 W1 완료에 필요하지
않으며 누락된 게이트 때문에 자동 활성화하지 않는다. 보고서는 저장소·소스/대상 ref/SHA·
비교 링크/요약·로컬/브라우저/검토/원격 증거·한계·미해결 지적·제안 병합 동작을 연결한다.
생성은 영속적이며 재시도 가능하다. 갱신은 새 버전을 만들며 새 소스/대상 커밋에 이전
승인을 조용히 이어 붙이지 않는다. 실제 파일럿은 기본 모드에서 PR 생성/갱신 호출이 0회임을
보이면서 모든 독립 검토·CI 요구를 유지해야 한다.

## 제안 단계 상태 기계

아래 이름은 W1을 설명하며 기존 상태 형식을 조용히 이전하지 않는다.

| 단계 / 결과 | 필수 전이 |
| --- | --- |
| `preflight` | 입력/승인을 고정하고 분리 기준 작업 공간을 준비하며 검사/브라우저/GitHub 기능과 시간 배분을 확인한다. |
| `implementing` | 작업자는 고정 작업과 과거 실패 근거를 따르며 계약 변경·게시를 하지 않는다. |
| `checking` | 신뢰된 작업 검사를 실행한다. 결정적 실패는 누적 한도 안에서 구현으로 돌아간다. |
| `browser_verifying` | 실제 지원 브라우저에서 프로젝트 하네스를 실행하고 입력에 연결된 원본 관측을 모은다. |
| `reviewing` | 독립 검토자가 실제 차이·부정 사례·기록·문서를 본다. 거절되면 구현으로 돌아간다. |
| `locally_accepted` | 모든 필수 로컬 증거와 검토가 현재 후보에 대응한다. 게시·병합 준비 완료를 뜻하지 않는다. |
| `publishing` | 멱등적인 commit/push와 버전 연결 보고서. 저장소/기준/작업 ref와 부수 효과 기록을 확인한다. |
| `remote_checking` | 정확한 버전과 통합 상태의 필수 명명 게이트를 관측한다. 실패 로그는 수정으로 전달한다. |
| `reporting` | 결정적 버전 보고서를 원자적으로 생성/복구한다. 보고서 기록 성공 후에만 준비 상태를 저장한다. |
| `ready_for_merge_approval` | 검증된 push 브랜치·병합 결정 보고서·성공한 현재 필수 push 게이트. 실제 병합은 사용자 승인이 필요하다. |
| `decision_required` | 질문/선택지/영향/권고와 명시적 승인 요건을 저장한다. |
| `capability_blocked` | 제한된 복구 후에도 필수 도구/환경이 없다. 재현 가능한 진단과 다음 행동을 담는다. |
| `budget_exhausted` | 누적 사용량과 모든 시도를 보존하며 재시작으로 한도를 보충하지 않는다. |
| `publication_blocked` | 안전한 파일 범위/원격 식별값/인증을 확보하지 못했다. 로컬 자료를 유지하고 위험한 push를 하지 않는다. |
| `incomplete_published` | 안전하게 검토한 변경을 전용 브랜치와 버전 연결 보고서에 보존하고 실패/누락 게이트도 드러낸다. |

미완료 게시는 원래 결정/기능/예산 결과와 별도 기록이다. 일반적인 게시 상태로 원인을
덮어쓰지 말고 둘 다 보존한다. 과거 `complete` 상태는 옛 의미를 유지한다.
기존 로컬 수용을 명시적으로 보고하며 새 게시 게이트를 소급 인증하지 않는다.
대상 병합을 수행하는 자동 전이는 없다.

## 브라우저 기능과 어댑터

명시적인 명령/기능과 결과 스키마를 갖춘 프로젝트 독립 어댑터 규약을 사용한다.
대상은 검사 하네스/fixture를 소유하며 컨트롤러가 시작하고 실제 사용 가능한 지원 브라우저를
실행해 입력 식별값과 결과를 저장한다. 사전 점검에서 작은 실제 실행을 확인한다.
앱 전용 컴퓨터 사용 도구가 독립 CLI에 노출된다고 가정하지 않는다.
구현 때 설치 기능을 검증해 구체적 로컬 백엔드를 고르고 선택적 사전 요건을 기록한다.
수동 복사 DOM 결과는 수동 실행임을 밝히면 근거가 될 수 있지만 W1 무인 파일럿 통과 근거는
아니다. Node 전용 JS나 화면 캡처는 실제 브라우저 실행으로 세지 않는다.
브라우저 부재는 필수 경로 완료를 사실대로 차단한다.

## 게시·원격 실패 수정·복구

게시 승인은 프로젝트/저장소·원격 식별값·전용 작업 브랜치·예상 기준에 연결한다.
작업자 시간을 쓰기 전에 읽기 전용 인증/상태 점검을 한다. 구현 작업자는 게시하지 않는다.
최종 컨트롤러 검사는 검토 경로와 현재 manifest를 확인한 뒤 commit·push·보고서를 별도
기록한다. PR 기록은 선택한 모드에서만 추가한다. 네트워크 결과가 불명확하면 다시 시도하기
전에 원격을 확인한다. 이미 성공했을 수 있기 때문이다. 수정 중에도 브랜치 식별값과 보고서
버전 이력을 유지하고 중복 커밋·강제 push·삭제·무관한 staging을 하지 않는다.
사용자의 결과별 게시 정책은 미완료 작업에도 적용되며 실패/누락 상태를 사실대로 남긴다.
미완료 변경도 먼저 안전한 게시임을 확인해야 한다.

기본 모드에서는 정확한 HEAD/통합 식별값을 가진 설정된 push 게이트가 필요하다.
pull-request 이벤트나 PR 식별값은 필요하지 않다. 선택적 PR 모드는 프로젝트/작업에서
명시적으로 골라야 한다. 저장소가 PR 전용 게이트를 강제하면 조용한 우회나 PR 생성 대신
실행 가능한 설정 결정을 반환한다. 사전 점검에서 필수 게이트 이름/이벤트를 정한다.
없음·대기·취소·알 수 없음 상태를 통과로 처리하지 않는다. 테스트 의존성 누락은 범위 내의
일상 수정이지만 기대값 변경은 보호 기준에 관한 결정이다. 원격 실패는 같은 제한 수정/검토
체인으로 전달하고 새 커밋은 과거 원격 성공을 무효화한다. 제한된 간격으로 확인하고 시간
초과 시 마지막 상태를 보존한다. 시간 초과로 원격 증거 요건이 없어지지 않는다.

단계와 부수 효과 전에 누적 횟수/시간을 영속 저장한다. 작업자·검증·브라우저·검토·게시·
원격 대기·재시작을 포함한다. 실행 중 단계는 단조 시계 마감으로 제한하고, 저장한 사용량과
벽시계 시각으로 중단 시간을 보수적으로 계산한다. 한도를 초기화하지 말고 충돌/시계 이상
처리를 명시한다. 시간 초과 시 로컬 자식 프로세스 그룹을 종료하며 검토/마무리 시간을 예약한다.
금액/토큰 계측은 제공하지 않는다. 벽시계 제한이 금액 지출 한도라고 암시하지 않는다.

## 사전 구축·파일럿·완료

현재 컨트롤러는 자신을 대상으로 실행할 수 없다. 이 보호를 유지한다.
구현은 분리된 dev-workflow 개발 체크아웃에서 진행하고 소유 계약/평가 manifest와 증거를
작업자 제어 밖에 둔다. 구현 전에 이 입력을 고정한다. 실제 사전 구축/기능 준비가 있기 전에는
실행 프로젝트를 활성화하지 않는다. 고정 해시는 실수/무단 변경을 탐지하지만 경로 분리만으로
안전한 보호 검사 서비스를 제공하는 것은 아니다.

합성 저장소/로컬 bare 원격에서 W01–W18 실패 사례를 실행하며 모의/실제 구분을 유지한다.
그다음 W1 계약의 제한된 CoRA state-type 불변성 작업을 실제 브라우저·검사·독립 검토·
GitHub 브랜치 push/원격 검증·보고서 생성까지 수동 단계 연결 없이 실행한다.
기존 CoRA 체크아웃과 소스 동작은 유지한다. 독립 검토는 이 설계·최종 구현·실제 실패 실행·
문서를 평가한다. 기능 누락이나 수동 완료는 부분 구현이며 완전 자동 전달로 주장하지 않는다.

## 구현 후보 위치 — 2026-11-05

- `tools/delivery_evidence.py`: 표준 내용 manifest, 외부 원본 명령 기록, 누적 영속 마감/횟수, 루프백 프로젝트 하네스의 실제 Chrome headless 실행, 런타임/fixture/결과/버전 연결.
- `tools/delivery_loop.py`: 명시적 schema-version-2 선택 실행기, 원래 자기 대상 보호, 사전 점검, 작업자/검사/브라우저/읽기 전용 검토, 오래된 증거 무효화와 안전한 미완료 처리.
- `tools/delivery_publish.py`: 정확한 경로 staging, 충돌을 고려한 commit/push 기록, 후보에만 기준 통합 후 재검증, 정확한 HEAD의 명명된 push CI와 추가형 외부 JSON/Markdown 병합 결정 보고서.
- `schemas/publication.schema.json`: 실패한 의미 수용과 분리된 독립 미완료 게시 안전 검토. 시간 소진으로 추가 검토 예산이 생기지 않으며 안전한 게시를 확인하지 못하면 차단을 유지한다.
- `projects/cora-w1-pilot.json`, `contracts/cora/W1-state-type-pilot.json`: 좁은 범위로 승인한 실제 시험. W1/F1 보호 정의는 유지한다.
- `tests/test_delivery_loop.py`: 실제 임시 Git/bare 원격 작업, 명시적인 합성 모델/GitHub 실패, 사용 가능한 실제 Chrome 실행. 합성 fixture는 실제 파일럿 증거가 아니다.

기존 CLI/검사는 유지한다. 컨트롤러 핵심은 Python 3.9+ 표준 라이브러리이고 어댑터에는 설치된
Chrome·Codex CLI·gh와 작업용 Python 검사 의존성이 필요하다. Chrome은 별도의 새 프로필과
루프백 하네스를 쓰는 실제 headless 브라우저다. OS/브라우저 샌드박스를 약화하는 플래그는
사용하지 않는다. 앱 전용 컴퓨터 사용 인터페이스를 가정하지 않는다.
PR 모드는 계약에서 선택 가능하지만 여기에는 구현하지 않았다. 선택하면 결정 요청을 반환하고
PR 생성을 조용히 활성화할 수 없다. 자동 대상 병합도 없다.

각 실행은 전체 컨트롤러 manifest와 소유 보호 파일을 고정하므로 컨트롤러 편집에는 새 연결
실행이 필요하며 새 정책을 조용히 채택하지 않는다. 보고서/명령/브라우저 자료는 명시적인 외부
상태 디렉터리에 둔다. 최종 소스/문서 변경은 수용을 무효화하지만 외부 보고서 생성 자체는 소스
검토의 순환을 만들지 않는다. 필수 push 게이트가 성공하고 정확한 기준/HEAD를 재확인할 때까지
게시 브랜치는 미완료다. 원격 게이트 대기/시계 이상은 사실대로 실행을 소진·차단하고 모든
시도와 안전한 미완료 게시 기록을 보존한다.

### 사전 구축 수정과 연결 검증

첫 실제 파일럿에서 모든 기준/판정은 통과했지만 decision_requests에 새 결정이 없다는 문장이
들어간 모순된 검토 출력이 나왔다. 컨트롤러는 올바르게 완료를 보류했고 게시 안전 검토는
시간 초과됐다. 통과를 만들어 내지 않았다. 독립적인 형식 전용 확인은 같은 의미 판단과 빈
결정 목록을 반환했다. 원래 중단 상태/로그는 그대로 유지한다.

구현은 이제 모순된 통과/지적/결정 출력을 잘못된 형식으로 보고 한 번의 독립 확인을 요청하며
두 자료를 모두 보존한다. 단지 통과를 얻기 위해 유효한 부정 의미 판단을 재시도하거나,
결정을 스스로 지우거나, 생성된 문장을 사용자 승인으로 취급하지 않는다.
잘못된 결과 자료형은 처리되지 않은 수용 오류 대신 실패로 처리한다.
브라우저 하네스 해시는 실제 실행 전후 비교하며 변경되면 결과를 무효화한다.
읽기 전용 원격 점검에는 영속적인 인프라 재시도 한 번을 허용하고, 쓰기는 무조건 재시도하지
않고 부수 효과 식별값을 확인한다.

별도의 명시적 연결 사전 재검증 설정은 동일한 파일럿 계약을 유지하고 원래 누적 마감/횟수를
복사한다. 연결은 수용된 실행 또는 원래 검토 내용이 변하지 않았고 독립적으로 수정된 검토가
연결된 모순된 통과 중단에서만 허용한다. 실제 미해결 결정을 우회할 수 없다.
이전 상태와 해결 기록을 모두 고정하고 옛 상태를 다시 쓰거나 예산을 보충하지 않는다.
새 분리 파일럿도 자체 전체 작업자/검사/브라우저/검토/게시 체인을 수행한다.
`projects/cora-w1-pilot-v2.json`이 이 구체적 연결 검증을 기록한다. 절대 증거 경로는
호스트 전용이며 이식 가능한 기본값이 아니다.

### 소스 검토 수정과 당시 검증 경계

별도 코드 검토자가 더 강한 환경 연결, 시간 초과 시 대기 CI 보존, 충돌 후 멱등 보고서를
요청했다. 명령 기록은 상속 환경 지문(인증 값 제외), 해석된 실행 파일 내용 식별값,
결정적인 프로젝트 의존성 점검을 포함한다. 검토/게시는 현재 환경/의존성 연결을 비교한다.
브라우저 실패는 정확한 원본 로그·실행 기록·프로젝트 관측 경로를 작업자에게 전달한다.
이는 실제 시험에서 발견한 진단 맥락 누락을 수정한다.

CI는 매 확인 때 마지막 상태를 저장한다. 보고서 ID는 고정된 실행/소스/대상/검토/CI
식별값에서 만들고 고아 JSON/Markdown 기록을 중복 버전 없이 복구한다.
보고서에는 목표·작업 요약·모든 검증 참조·누적 한도·연결된 실패 이력을 담는다.
보고서 실패로 준비 상태를 저장할 수 없다. 새 구현/검토를 시작하면 이전 수용을 지우고,
옛 digest가 남아 있어도 게시기가 현재의 부정 검토를 별도로 거부한다.
부모 예산 할당에도 배타적 부속 기록을 두어 새 상태 디렉터리로 같은 한도를 늘리지 못하게 하며
원래 이력은 그대로 둔다.

당시 최신 로컬 평가: 검사 58개 통과. 실제 Chrome과 실제 임시 Git/bare 원격을 쓰고,
모델/GitHub 실패 응답은 합성임을 명시했다. W02–W16/W18은 대응 실패 재현을 통과했지만
실제 CoRA 작업이 수용된 게시/push CI에 도달하지 않아 W01/W17은 미완료다.
새 디렉터리나 만들어 낸 통과로 해결할 수 없다. PR이나 대상 병합은 없었다.

연결 한도 청구는 최초 상태·소스/컨트롤러/프로젝트/외부 정책 연결을 담아 완전히 쓴 뒤
원자적으로 연결한 저널을 사용한다. 자식 상태 저장 전 충돌은 정확히 같은 실행 ID와 예산을
복구하며 저장 후에만 활성화한다. 활성화 이후 상태 누락/삭제는 한도 재생성의 허가가 아니다.
다른 자식 디렉터리에서 같은 부모 한도를 재사용할 수 없다. 당시 수용은 소진된 실제 시험에서
미완료이며 부모의 수동 WIP 보존은 자동 게시 요건을 충족하지 않는다.

자식 상태 저장 양쪽에서 같은 원래 저널 연결 함수를 사용한다.
활성화 전에 보호 값을 영속 저장·검증하고 마지막 연결도 재확인한다.
검사는 저장 이후 동일 입력 복구와 정책 변경 거부를 포함한다.
당시 최신 로컬 검사 58개는 통과했지만 실제 W01/W17은 미완료다.

최종 독립 재검토는 수정된 소스 충돌/연결 경로가 기록된 검사 아래 올바르다고 판단했다.
당시 W1 전체 수용은 성공한 실제 파일럿과 추가 시험의 명시적 사용자 승인 부재 때문에
여전히 막혀 있었다.

### 추가 시험: 출처 순환으로 실제 수용이 계속 실패

사용자는 이전 실패를 `projects/cora-w1-approved-trial.json`에 연결한 새 1800초/3회 시험을
승인했다. 세 번을 모두 사용했고 매번 검사와 실제 Chrome/고정 F1 검증이 통과했지만,
독립 문서 검토는 오래된 출처 기록을 거부했다. W01/W17은 미완료다.
실제 누적 이력은 6회이며 PR/대상 병합은 없다.

문서 갱신은 검증보다 앞서므로 최종 정확한 소스 검사 결과는 외부 실행 증거와 최종 보고서에
기록한다. 대상 문서는 현재 동작/진행/한계를 설명하고 명확히 과거임을 밝힌 관측을 인용할 수
있다. 자기 자신을 포함하는 최종 digest 대신 고정된 실행 증거 위치를 연결해야 한다.
현재 수용에는 항상 현재 manifest와 실제 실행 증거를 사용하며 이전 통과로 대체하지 않는다.
검토자 지침은 문서/의미 게이트를 제거하지 않고 이 구분을 명시한다.
이 수정 후 성공한 실제 시험은 당시 아직 없었다. 위의 옛 상태는 시간순 증거이며 현재 수용이
아니다.

검토 단계 한도는 전체 한도와 별개다. 단계 시간 초과로 검토가 없으면 같은 영속 마감/횟수
안에서만 재시도한다. 과거에 잘못 분류한 검토 시간 초과는 보호된 원본 시간 초과/입력 기록,
같은 소스, 최종 검토/결정 부재, 남은 예산이 있을 때 한 번 연결할 수 있다.
기존 충돌 안전 배타 저널을 사용하고 한도를 초기화하지 않는다.
사용자가 승인한 60분/5회 설정과 복구 설정이 이 제한 사례를 기록한다.
완료된 부정 검토에는 이 시간 초과 복구를 사용할 수 없다.

### 제한된 실제 복구 실행의 인계

검토된 시간 초과/출처 수정을 적용한 최종 자식 실행은 원래 3600초/5회 한도 중 누적 2회로
CoRA 81b1e21의 정확한 HEAD CI와 불변 보고서까지 모든 실제 단계를 완료했다.
사전 수동 WIP 보존/컨트롤러 수정은 그 자식 실행보다 앞선 준비/실패 이력으로 명시적으로
유지한다. 최종 자식 안의 누락 단계를 수동 복사나 게시로 대신하지 않았다.
작업 검토는 통과했고 W1 최종 평가와 마일스톤 검토는 별개다.
CoRA/컨트롤러 대상 브랜치는 사용자 병합 승인을 기다린다.
위의 과거 미완료 기록은 각 단계의 기록으로 보존한다.

최종 수용: 고정 W1 평가 **18/18**, 검사 **63개**, 독립 최종 마일스톤 감사 **12/12 기준**을
모두 통과했고 차단 지적/결정은 없다. 위의 사전/수동 경계를 유지하면서 제한된
W1 revision-2 마일스톤이 성립했다. 실제 병합은 여전히 사용자 승인 대상이다.
