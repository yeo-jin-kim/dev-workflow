<!-- document-language: en -->
# Development workflow controller

This repository contains project-independent orchestration, not CoRA code.
Keep controller, contracts, schemas and logs outside target repositories.
Project-specific locations and policies belong in projects/ and contracts/.
Do not import target source packages or require a target to import this project.
Preserve decision/validation/documentation gates and archived evidence.
Update README and docs/implementation.md with behavior, validation and limitations.
Never claim OS isolation or independent semantic proof from ordinary path separation.

## Commit and push after each delivery
User instruction: commit and push changes after each work delivery. The parent
controller/maintaining agent finalizes publication after validation; workers do
not change their own contracts or publish while implementation/review is running.
Keep unrelated work separate. Use a dedicated branch for incomplete/experimental
work and record passing checks, failed/missing checks and review status truthfully.
Commit/push does not mean acceptance, merge or deployment. Never force-push,
publish private logs/source data, or bypass review to claim completion.

## Solo-development delivery policy
Owner approved branch/report delivery as the default. Prepare a verified dedicated
branch, commit/push and a revision-bound merge-decision report. Keep independent
review, documentation and required push-CI gates. PRs are optional and created
only when explicitly selected for the project/task; a missing PR is not a failure.
Actual target merge still requires owner authorization for the concrete revision.


## Bilingual documentation

User preference: every human-readable document starts with the complete English
version, followed by the complete Korean translation under `# 한국어 번역`.
Use `<!-- document-language: en -->` and `<!-- document-language: ko -->` markers.
Translate the whole document, including historical entries, tables and limits;
do not substitute a summary. Keep both languages synchronized in the same change.
Preserve commands, paths, identifiers, hashes, numbers and original evidence.
Machine-readable JSON contracts/schemas and immutable historical run artifacts
remain structurally intact; do not duplicate keys or rewrite accepted evidence.
Future generated Markdown reports use English first and Korean second. Raw
machine fields can be quoted verbatim as evidence, clearly labeled in each
language. Apply this policy to new and updated documents and check both versions.

---

<!-- document-language: ko -->
# 한국어 번역

# 개발 워크플로 컨트롤러

이 저장소는 프로젝트와 독립된 실행 제어 기능을 담으며 CoRA 코드가 아니다.
컨트롤러·계약·스키마·로그는 대상 저장소 밖에 둔다.
프로젝트별 위치와 정책은 projects/ 및 contracts/에 둔다.
대상 소스 패키지를 가져오거나 대상 프로젝트가 이 저장소를 가져오도록 요구하지 않는다.
결정·검증·문서 게이트와 보관된 증거를 유지한다.
동작·검증·한계를 바꾸면 README와 docs/implementation.md를 갱신한다.
일반적인 경로 분리만으로 운영체제 수준 격리나 독립적인 의미 정확성이 입증됐다고 주장하지 않는다.

## 결과 전달마다 commit/push

사용자 지시: 작업 결과를 전달할 때마다 변경을 commit/push한다. 상위 컨트롤러 또는
유지보수 담당 에이전트가 검증 후 게시를 마무리한다. 구현·검토 중에는 작업자가 자기 계약을
바꾸거나 직접 게시하지 않는다. 관련 없는 작업은 분리한다. 미완료·실험 작업은 전용 브랜치에
보존하고 통과·실패·누락 검사와 검토 상태를 사실대로 기록한다.
commit/push는 승인·병합·배포를 뜻하지 않는다. 강제 push, 비공개 로그·원문 데이터 게시,
검토 우회를 통한 완료 주장을 하지 않는다.

## 1인 개발 결과 전달 정책

사용자는 브랜치·보고서 전달을 기본값으로 승인했다. 검증된 전용 브랜치를 준비해
commit/push하고 해당 버전에 연결된 병합 결정 보고서를 만든다. 독립 검토·문서 검토·필수
push CI 게이트는 유지한다. PR은 선택 사항이며 프로젝트·작업에서 명시적으로 선택했을 때만
만든다. PR이 없다는 이유로 실패 처리하지 않는다.
대상에 실제 병합하려면 구체적인 버전에 대한 사용자 승인이 여전히 필요하다.

## 영문·한글 병기 문서

사용자 선호: 사람이 읽는 모든 문서는 완전한 영어 버전을 먼저 두고, `# 한국어 번역`
아래에 전체 한국어 번역을 둔다. 언어 구분에는 `<!-- document-language: en -->`와
`<!-- document-language: ko -->` 표시를 사용한다.
과거 이력·표·한계를 포함한 문서 전체를 번역하며 요약으로 대신하지 않는다.
두 언어는 같은 변경에서 함께 갱신한다. 명령·경로·식별자·해시·숫자·원본 증거는 유지한다.
기계 판독 JSON 계약·스키마와 변경 불가인 과거 실행 증거는 구조를 유지하며,
키를 중복하거나 승인된 증거를 다시 쓰지 않는다.
앞으로 생성하는 Markdown 보고서도 영어를 위, 한국어를 아래에 둔다. 기계 필드의 원문은
각 언어에서 증거임을 명확히 표시해 그대로 인용할 수 있다.
새 문서와 갱신 문서에 이 정책을 적용하고 두 버전을 모두 확인한다.
