# Controller separation implementation record

## 2026-11-05 — independent repository

Migrated the original local runner, schemas, automation tests and CoRA milestone
contracts from the CoRA working tree. No CoRA cognitive source code or runtime
package is copied or imported. CoRA's domain decision ledger remains in its own
`docs/implementation/decisions.json`; project-specific configuration references it.

The controller accepts an explicit `--project`, resolves target location from that
configuration, executes worker/check/review processes in the target, and uses its
own schemas/contracts/state outside the target. The configuration supplies the
project's documentation/decision paths to task context. Documentation review is
mandatory and cannot be overridden by a contract.

Added rejection of overlapping controller/target trees and state under the target;
added controller-version/target identity checks for resume and a target-level lock
across milestone directories. Fingerprints cover controller code, project/contract
configuration, schemas and controller guidance. Historical logs were moved to
ignored `.local/archive/cora/development-loop`; migration.json records SHA-256
checksums. Original absolute paths in old state are retained as historical data,
not active resume instructions.

## Validation

- Controller: `python3 -m unittest discover -s tests -q`: **15 passed**.
- Tests exercise external schemas and process target root, external run state,
  target/controller overlap rejection, documentation/completion gates, decision
  waiting, locks, contract changes and source-version invalidation.
- CoRA independently: **453 passed in 31.40 seconds**. Its prior 465 count included
  12 controller tests; those moved here and gained 3 separation cases.
- `status --project projects/cora.json`: Not started for the current F1 goal.
- Archive file contents were checked against migration SHA-256 hashes; `.local/`
  is excluded from Git. No new live Codex development run was started.
- Link/format validation and Git whitespace checks completed after documentation.

## Remaining limits

Path separation and workspace-write/read-only CLI modes do not prove hostile
process isolation. Trusted check commands still run with the user's permissions.
No external scheduler, notification loop, monetary budget, protected-test service
or OS security boundary is added. The independent repository has no remote
configured and no publishing/deployment behavior. Historical notes are retained
under docs/original-runner-notes.md; README is the current operating guide.
