# dev-workflow

Independent local development orchestration. Target repositories do not import
or depend on this repository. Python 3.9+ on macOS/Linux; standard library only.

## Usage

Run from this repository (the script resolves defaults from its own location):

```sh
python3 tools/development_loop.py status --project projects/cora.json
python3 tools/development_loop.py run --project projects/cora.json --max-cycles 3 --total-seconds 1800
python3 -m unittest discover -s tests -q
```

`run` invokes the installed/authenticated Codex CLI and executes trusted contract
checks in the target checkout. Default model settings are preserved. The project files still point to historical F1; F1 has since completed and merged.
Select an explicit new authorized contract/isolated target before a new run; the
example command is not a newly selected goal. `pilot.json` is historical.

## Layout

- `tools/`: project-independent runner.
- `schemas/`: worker/reviewer output contracts.
- `projects/`: target root and project-specific policy/decision references.
- `contracts/<project>/`: approved goal, scope, checks, acceptance criteria.
- `.local/runs/`: durable state, subprocess logs, check and review results (ignored).
- `.local/archive/`: original historical run artifacts and migration checksums (ignored).
- `docs/implementation.md`: behavior, verification and remaining limitations.

Project root paths are relative to this repository unless absolute. Check command
arguments run relative to the target root. The project policy and decision paths
are target-relative. Add another project configuration/contract without importing
its source code into the controller. A contract cannot redefine the mandatory
`documentation_sync` review criterion. Missing/failed evidence blocks completion.

The worker uses the target as its workspace-write root; the separate reviewer
uses read-only mode. Schemas, contracts and output files are controller-owned.
Locks cover target identity across milestone runs. Target/controller trees must
be disjoint, and state must remain external. Reusing state after target or
controller changes is rejected; start a new state directory. Human decisions
remain pending until explicitly resolved in a new contract/state directory.

## Boundaries and limitations

This is path/ownership separation plus CLI workspace sandboxing, not a proof of
OS-level isolation. Local checks execute with the controller user's permissions;
use trusted checks. Protect the controller from target scripts, symlink attacks,
and arbitrary external commands with stronger OS/CI isolation before unattended
operation. Target code cannot legitimately edit contracts, controller or logs.
The legacy runner has per-invocation limits; the opt-in W1 runner persists
cumulative deadlines/cycles. Monetary budgets, background scheduling,
notifications, next-goal selection and a dedicated approval UI are not implemented.
No target merge/deploy is automatically authorized. W1 publication is limited
to the explicitly configured task repository/branch and reviewed task files.

The preserved archive is historical: original state files contain old absolute
paths. Do not resume them or rewrite their evidence. See migration.json.

## CoRA F1 history and current next milestone

F1 completed synthetic verification and merged in
[CoRA PR #1](https://github.com/yeo-jin-kim/cora/pull/1) to
`codex/workflow-foundation` (`fe4aac5`). Parent intervention supplied browser,
review/publication handoffs and a CI prerequisite fix; this was not a fully
unattended run. Its contracts and run histories remain preserved.

W1 revision 2 has an **opt-in implementation candidate; live acceptance remains incomplete after the additional authorized trial**:
[task contract](contracts/dev-workflow/W1-reviewable-delivery.md),
[design and status](docs/01-reviewable-delivery-design.md).
`tools/delivery_loop.py` adds actual Chrome execution, version-bound evidence,
durable repair/review, dedicated-branch commit/push, exact-head push CI and a
versioned merge-decision report. No PR is created and target merge remains an
explicit owner action. The legacy runner and its historical states are unchanged.

```sh
python3 tools/delivery_loop.py run --project projects/cora-w1-pilot-v2.json --state-dir /ABSOLUTE/EXTERNAL/RUN --max-cycles 3 --total-seconds 3600
python3 tools/delivery_loop.py status --project projects/cora-w1-pilot-v2.json --state-dir /ABSOLUTE/EXTERNAL/RUN
```

The shown invocation is historical: its three-cycle allowance is exhausted.
Do not use another state directory to replenish it. The owner subsequently authorized one additional 30-minute/three-cycle trial;
that allowance is also exhausted without live acceptance. A further real pilot
needs explicit owner budget authorization. The linked v2 pilot config preserves the
original failed trial and its cumulative budget (see the implementation record). It is opt-in and host-specific (existing Chrome and CoRA Python
test environment). Use the implementation checkout described in the design.
Do not run against the original/dirty checkout or the controller itself. `status`
reports a historical snapshot; `run` rechecks current inputs/remote state, honors
persisted cumulative limits and refuses pending decisions. Browser, reviewer or
GitHub capability failures remain incomplete with actionable evidence; no manual
result-copy shortcut qualifies as unattended success. New dependencies are not
installed by the runner. Live-pilot/final-review results are recorded in
`docs/implementation.md`; do not infer completion from code presence.

## Delivery publication policy

The owner requests commit/push after each delivery. The maintaining parent
performs finalization after checking results. Incomplete milestones are pushed
to dedicated branches with their failed/missing gates stated, never merged or
reported accepted merely because they were published. Private .local logs stay
excluded; implementation workers do not push during their runs.

F1 synthetic evidence verification is available through `tools/evaluate_f1.py`.
It checks protected definitions, recorded source fingerprints and actual browser
results; see `docs/implementation.md`. Evidence completion does not bypass the
independent review gate.


The owner approved a further bounded 60-minute/five-cycle actual trial, recorded
in `projects/cora-w1-approved-trial-60m.json`. Its first review hit a phase cap;
the recovery profile preserves the same deadline/consumed cycles and guarded
missing-review evidence. This does not automatically renew either trial's budget.
Current actual outcome is recorded in the implementation record.
