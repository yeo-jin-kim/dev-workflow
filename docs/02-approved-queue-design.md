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
