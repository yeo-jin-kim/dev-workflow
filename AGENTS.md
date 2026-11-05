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
