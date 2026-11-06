"""W2: bounded owner-approved sequential dispatch over the unchanged W1 engine."""
import argparse
import contextlib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid

from development_loop import lock, save, effective_contract, valid_review
from delivery_evidence import fingerprint, git, manifest, ResultParser
from delivery_loop import Delivery

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object: ' + str(path))
    return value


def positive(value):
    if type(value) is not int or value < 1:
        raise ValueError('Limits must be positive integers.')
    return value


def model(path):
    path = Path(path).resolve()
    q = read(path)
    if q.get('schema_version') != 1 or not q.get('id') or not q.get('tasks'):
        raise ValueError('A version-1 nonempty explicit queue is required.')
    keys = ['max_tasks', 'max_reserved_seconds', 'max_reserved_cycles']
    for key in ['window_seconds', *keys]:
        positive(q['limits'][key])
    for limits in q['project_limits'].values():
        for key in keys:
            positive(limits[key])
    tasks, inputs, targets, heads = {}, [path], set(), set()
    for item in q['tasks']:
        name = item['id']
        if not isinstance(name, str) or not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in name) or name in tasks:
            raise ValueError('Unique safe task IDs are required.')
        project = (ROOT / item['project']).resolve()
        cfg = read(project)
        target = (ROOT / cfg['root']).resolve()
        contract = (ROOT / cfg['contract']).resolve()
        effective_contract(read(contract))
        delivery = cfg['delivery']
        if cfg.get('schema_version') != 2 or cfg.get('parent_budget') or delivery['mode'] != 'branch_report':
            raise ValueError('Queue dispatch requires fresh W1 branch_report projects without parent_budget.')
        if delivery['head'] == delivery['base'] or not delivery.get('required_gates'):
            raise ValueError('Dedicated branch and explicit remote gates required.')
        if target == ROOT or ROOT in target.parents or target in ROOT.parents:
            raise ValueError('Controller/target must be disjoint.')
        head = (delivery['repository'], delivery['head'])
        if target in targets or head in heads or any(target in p.parents or p in target.parents for p in targets):
            raise ValueError('Tasks require disjoint worktrees and distinct publication heads.')
        targets.add(target); heads.add(head)
        group = delivery['repository']
        if group not in q['project_limits']:
            raise ValueError('Every repository requires an explicit project limit.')
        for key in ['max_cycles', 'total_seconds']:
            positive(item[key])
        deps = item.get('depends_on', [])
        if not isinstance(deps, list) or len(deps) != len(set(deps)):
            raise ValueError('Dependencies must be a list of unique task IDs.')
        paths = [project, contract, target / 'AGENTS.md']
        paths += [Path(p).resolve() for p in cfg.get('protected_files', [])]
        for key in ['documentation_policy', 'decision_record']:
            if cfg.get(key):
                paths.append((target / cfg[key]).resolve())
        if not all(p.is_file() for p in paths):
            raise ValueError('Missing task authority input.')
        inputs += paths
        tasks[name] = dict(item, project_path=str(project), target=str(target), group=group, depends_on=deps)
    visiting, visited = set(), set()
    def visit(name):
        if name not in tasks or name in visiting:
            raise ValueError('Unknown or cyclic dependency.')
        if name in visited:
            return
        visiting.add(name)
        for dep in tasks[name]['depends_on']:
            visit(dep)
        visiting.remove(name); visited.add(name)
    for name in tasks:
        visit(name)
    return q, tasks, fingerprint(inputs)


def baseline(task):
    root = Path(task['target']); cfg = read(task['project_path'])['delivery']
    if git(root, 'status', '--porcelain'):
        raise ValueError('Approval/dispatch requires a clean target baseline.')
    branch = git(root, 'branch', '--show-current')
    if branch != cfg['head']:
        raise ValueError('Approved target must already be on its dedicated branch.')
    remote = git(root, 'ls-remote', cfg['remote'], 'refs/heads/' + cfg['base']).split()
    if len(remote) != 2:
        raise ValueError('Cannot pin approved remote base.')
    return {'target': str(root), 'head': git(root, 'rev-parse', 'HEAD'),
            'digest': manifest(root)['digest'], 'branch': branch, 'base': remote[0]}


@contextlib.contextmanager
def target_locks(tasks):
    folder = ROOT / '.local/locks'; folder.mkdir(parents=True, exist_ok=True)
    with contextlib.ExitStack() as stack:
        for root in sorted({task['target'] for task in tasks}):
            stack.enter_context(lock(folder / hashlib.sha256(root.encode()).hexdigest()))
        yield


def approve(queue, output, decision_reference):
    """Operator records an already supplied owner decision, never model approval."""
    if not decision_reference.strip():
        raise ValueError('A real owner decision reference is required.')
    q, tasks, inputs = model(queue)
    output = Path(output).resolve()
    if any(output.is_relative_to(Path(t['target'])) for t in model(queue)[1].values()):
        raise ValueError('Approval records must stay outside target worktrees.')
    if output.exists():
        raise ValueError('Approval receipts are immutable; choose a new receipt for a new decision.')
    output.parent.mkdir(parents=True, exist_ok=True)
    data = {'schema_version': 1, 'queue_id': q['id'], 'inputs': inputs,
            'decision_reference': decision_reference, 'approved_at': time.time(),
            'baselines': {name: baseline(task) for name, task in tasks.items()}}
    # Exclusive creation: another operator cannot overwrite this receipt.
    with output.open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
    return data


def verify_browser(attempt, cfg, digest, reported):
    binding = read(attempt / 'browser-binding.json')
    result_path = attempt / 'browser-result.json'; result = read(result_path)
    directory = attempt / 'browser'
    if (binding.get('target_digest') != digest or binding.get('engine') != 'actual Chrome headless'
            or not binding.get('browser_version') or not binding.get('harness')
            or binding.get('result_sha256') != hashlib.sha256(result_path.read_bytes()).hexdigest()
            or result.get('status') != 'PASS' or reported != result
            or (attempt / 'browser-version.log').read_text().strip() != binding['browser_version']):
        raise ValueError('Browser engine/result/version binding is invalid.')
    files = {}
    for path in directory.rglob('*'):
        if path.is_file():
            if not path.resolve().is_relative_to(directory):
                raise ValueError('Browser harness escapes its evidence directory.')
            files[str(path.relative_to(directory))] = hashlib.sha256(path.read_bytes()).hexdigest()
    # W1 copies the browser result into the project harness only after execution.
    copied = cfg.get('result_file', 'browser-result.json')
    if read(directory / copied) != result:
        raise ValueError('Project validator input differs from actual browser result.')
    files.pop(copied, None)
    expected = dict(binding['harness']); expected.pop(copied, None)
    if files != expected:
        raise ValueError('Browser harness is missing or changed.')
    for label in ['browser-prepare', 'browser-version', 'browser-dom', 'browser-validate']:
        record = read(attempt / (label + '-execution.json'))
        if record.get('exit_code') != 0 or record.get('input_digest') != digest:
            raise ValueError('Browser execution evidence is incomplete or stale.')
        if label in ['browser-version', 'browser-dom'] and record['argv'][0] != cfg['executable']:
            raise ValueError('Browser executable is not the configured engine.')
    if not (attempt / 'browser-dom.log').is_file():
        raise ValueError('Browser raw output is missing.')
    parser = ResultParser(); parser.feed((attempt / 'browser-dom.log').read_text())
    if json.loads(''.join(parser.parts)) != result:
        raise ValueError('Raw browser DOM does not match the recorded result.')


def verify_delivery(task, folder, grant):
    """Read W1 evidence, not its process exit code or a worker's success claim."""
    folder = Path(folder).resolve()
    state = read(folder / 'state.json')
    cfg = read(task['project_path']); contract = effective_contract(read((ROOT / cfg['contract']).resolve()))
    expected = fingerprint([Path(task['project_path']), (ROOT / cfg['contract']).resolve()])
    if (any(state.get('controls', {}).get('protected', {}).get(p) != digest for p, digest in expected.items())
            or state.get('controls', {}).get('controller') != manifest(ROOT)['digest']):
        raise ValueError('W1 receipt was produced with different authority/controller inputs.')
    digest = manifest(Path(task['target']))['digest']
    budget = state.get('budget', {})
    if (state.get('status') != 'ready_for_merge_approval' or state.get('target') != task['target']
            or state.get('state_dir') != str(folder) or state.get('accepted_digest') != digest
            or budget.get('deadline', float('inf')) > grant['deadline']
            or budget.get('max_cycles') != grant['cycles'] or not 0 < budget.get('cycles', 0) <= grant['cycles']
            or not valid_review(state.get('last_review', {}), contract['criteria'])):
        raise ValueError('Missing, stale or unaccepted W1 delivery evidence.')
    report_path = Path(state['report']).resolve()
    if report_path.parent != folder / 'reports':
        raise ValueError('Report is outside this task run.')
    report = read(report_path); identity = report['identity']
    report_id = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    head, base = state['published_sha'], state['base_sha']
    if (report_path.name != report_id + '.json' or report.get('report_id') != report_id
            or report.get('status') != 'ready_for_merge_approval'
            or identity.get('status') != report['status'] or identity.get('review') != state['last_review']
            or identity.get('ci') != state.get('last_ci')
            or identity.get('run_id') != state['run_id'] or identity.get('contents') != digest
            or identity.get('head') != head or identity.get('base') != base
            or report.get('source_sha') != head or report.get('target_sha') != base
            or report.get('repository') != cfg['delivery']['repository']
            or report.get('source_branch') != cfg['delivery']['head'] or report.get('target_branch') != cfg['delivery']['base']
            or report.get('created_at', float('inf')) > grant['deadline']
            or report.get('review') != state['last_review'] or report.get('ci') != state.get('last_ci')):
        raise ValueError('Report identity does not match W1 state.')
    ci = state['last_ci']; delivery = cfg['delivery']
    expected = delivery['required_gates']
    if (ci.get('status') != 'success' or ci.get('head') != head or ci.get('base') != base
            or len(ci.get('gates', [])) != len(expected)
            or any(not any(g.get('gate') == gate and g.get('passed') is True for g in ci['gates']) for gate in expected)):
        raise ValueError('Exact-head required CI gates did not pass.')
    attempt = Path(state['attempts'][-1]['folder']).resolve()
    if attempt.parent != folder:
        raise ValueError('Attempt does not belong to this task.')
    checks = sorted(attempt.glob('check-*-execution.json'))
    if len(checks) != len(contract['checks']) or any(read(p).get('exit_code') != 0 or read(p).get('input_digest') != digest for p in checks):
        raise ValueError('Current checks are missing or stale.')
    verification = report.get('verification', [])
    if (not verification or verification[-1].get('evidence_directory') != str(attempt)
            or verification[-1].get('checks') != [read(p) for p in checks]):
        raise ValueError('Report check receipts differ from raw execution evidence.')
    verify_browser(attempt, cfg['browser'], digest, verification[-1].get('browser'))
    target = Path(task['target'])
    if git(target, 'rev-parse', 'HEAD') != head or git(target, 'status', '--porcelain'):
        raise ValueError('Published checkout moved or is dirty.')
    remote = git(target, 'ls-remote', delivery['remote'], 'refs/heads/' + delivery['head'], 'refs/heads/' + delivery['base'])
    refs = {line.split()[1]: line.split()[0] for line in remote.splitlines()}
    if refs.get('refs/heads/' + delivery['head']) != head or refs.get('refs/heads/' + delivery['base']) != base:
        raise ValueError('Remote head/base moved; owner must revalidate integration.')
    return {'head': head, 'base': base, 'report': str(report_path), 'report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest()}


def w1_engine(task, folder, grant):
    """Called under Queue's target lock through verification and checkpoint."""
    if folder.exists():
        raise ValueError('Fresh dispatch must not adopt existing child state/evidence.')
    delivery = Delivery(Path(task['project_path']), folder, grant['seconds'], grant['cycles'])
    delivery.state['budget']['deadline'] = min(delivery.state['budget']['deadline'], grant['deadline'])
    delivery.persist()
    return delivery.run()


class Queue:
    def __init__(self, queue, approval, state_dir, engine=None, verifier=None):
        self.path, self.approval = Path(queue).resolve(), Path(approval).resolve()
        self.dir = Path(state_dir).resolve()
        self.file = self.dir / 'state.json'
        self.q, self.tasks, self.inputs = model(self.path)
        if any(Path(p).is_relative_to(self.dir) for p in [*self.inputs, str(self.approval)]):
            raise ValueError('Approval/configuration inputs cannot live inside mutable queue state.')
        if self.dir == ROOT or self.dir in ROOT.parents or any(self.dir == Path(t['target']) or Path(t['target']) in self.dir.parents or self.dir in Path(t['target']).parents for t in self.tasks.values()):
            raise ValueError('Queue evidence must be outside target trees and not a controller ancestor.')
        self.dir.mkdir(parents=True, exist_ok=True)
        self.engine, self.verifier = engine or w1_engine, verifier or verify_delivery
        self.state = read(self.file) if self.file.exists() else {}
        if self.file.exists() and (self.state.get('schema_version') != 1 or not self.state.get('binding') or not self.state.get('run_id')
                                   or not all(k in self.state for k in ['started_at', 'deadline', 'jobs'])):
            raise ValueError('Started/corrupt state without its binding cannot regenerate allowance.')
        self.start_wall, self.start_mono = time.time(), time.monotonic()

    def persist(self):
        save(self.file, self.state)

    def stop(self, status, message, task=None):
        self.state['status'] = status
        self.state['handoff'] = {'reason': message, 'task': task,
                                 'evidence_state': str(self.file),
                                 'task_evidence': self.state.get('jobs', {}).get(task, {}).get('folder'),
                                 'recommendation': 'Inspect evidence; record a new owner-approved plan if inputs, allowance or integration must change.',
                                 'options': ['Review the preserved task evidence.', 'Approve revised inputs/limits in a separate queue; do not replay ambiguous work.'],
                                 'merge_authorized': False}
        if self.state.get('binding'):
            self.persist()
        else:
            save(self.dir / 'attention.json', self.state)
        return self.state

    def guard(self):
        _, _, inputs = model(self.path)
        if inputs != self.inputs:
            raise ValueError('Inputs changed after queue loading; reload and review the new approval.')
        approval = read(self.approval)
        if (approval.get('schema_version') != 1 or approval.get('queue_id') != self.q['id']
                or not approval.get('decision_reference', '').strip() or approval.get('inputs') != inputs):
            raise ValueError('Exact owner approval is missing or task authority inputs changed.')
        if set(approval.get('baselines', {})) != set(self.tasks):
            raise ValueError('Approved baseline identities are missing.')
        self.baselines = approval['baselines']
        binding = {'inputs': inputs, 'approval': fingerprint([self.approval]), 'controller': manifest(ROOT)['digest']}
        if self.state.get('binding') and self.state['binding'] != binding:
            raise ValueError('Queue/controller/approval changed after start; no implicit reapproval.')
        return binding

    def now(self):
        now = max(time.time(), self.start_wall + time.monotonic() - self.start_mono)
        if now + 1 < self.state.get('last_seen', now):
            raise ValueError('Clock moved backwards; allowance cannot be renewed.')
        self.state['last_seen'] = max(now, self.state.get('last_seen', now)); self.persist()
        return self.state['last_seen']

    def reserve(self, task):
        now = self.now(); limits = self.q['limits']; group = task['group']
        jobs = list(self.state['jobs'].values())
        for selected, cap in [(jobs, limits), ([j for j in jobs if j['group'] == group], self.q['project_limits'][group])]:
            if (len(selected) >= cap['max_tasks'] or sum(j['grant']['seconds'] for j in selected) + task['total_seconds'] > cap['max_reserved_seconds']
                    or sum(j['grant']['cycles'] for j in selected) + task['max_cycles'] > cap['max_reserved_cycles']):
                raise ValueError('Queue/project reservation budget exhausted; no automatic expansion.')
        seconds = min(task['total_seconds'], int(self.state['deadline'] - now))
        if seconds < 1:
            raise ValueError('Original queue window expired.')
        grant = {'seconds': seconds, 'cycles': task['max_cycles'], 'deadline': min(self.state['deadline'], now + seconds)}
        job = {'phase': 'reserved', 'group': group, 'grant': grant, 'folder': str(self.dir / 'tasks' / task['id'])}
        self.state['jobs'][task['id']] = job; self.persist()
        return job

    def initialize(self, binding):
        now = time.time()
        self.state = {'schema_version': 1, 'run_id': uuid.uuid4().hex, 'status': 'running', 'binding': binding,
                      'started_at': now, 'last_seen': now, 'deadline': now + self.q['limits']['window_seconds'], 'jobs': {}}

    def reconcile(self, name, job):
        receipt = self.verifier(self.tasks[name], Path(job['folder']), job['grant'])
        if job['phase'] == 'delivered' and receipt != job['receipt']:
            raise ValueError('Previously delivered receipt changed.')
        job.update(phase='delivered', receipt=receipt, verified_at=time.time()); self.persist()

    def run(self):
        try:
            binding = self.guard()
            if not self.state.get('binding'):
                self.initialize(binding); self.persist()
            for name, job in self.state['jobs'].items():
                if job['phase'] in {'dispatching', 'delivered'}:
                    try:
                        with target_locks([self.tasks[name]]):
                            self.reconcile(name, job)
                    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
                        return self.stop('decision_required', 'Dispatch cannot be safely reconciled: ' + str(error), name)
                elif job['phase'] == 'blocked':
                    return self.stop('decision_required', 'Previous task failed; no automatic replay.', name)
            while True:
                self.guard()
                if all(self.state['jobs'].get(n, {}).get('phase') == 'delivered' for n in self.tasks):
                    with target_locks(list(self.tasks.values())):
                        for name, job in self.state['jobs'].items():
                            self.reconcile(name, job)
                        self.state.update(status='delivered_awaiting_merge', handoff={
                            'merge_authorized': False, 'verified_at': time.time(),
                            'freshness': 'Point-in-time remote observations, not a remote lock. Revalidate exact refs before owner-authorized merging.',
                            'recommendation': 'Owner may review exact task reports and authorize each merge separately.'})
                        self.persist()
                    return self.state
                ready = [t for n, t in self.tasks.items() if self.state['jobs'].get(n, {}).get('phase') != 'delivered'
                         and all(self.state['jobs'].get(d, {}).get('phase') == 'delivered' for d in t['depends_on'])]
                if not ready:
                    return self.stop('decision_required', 'Dependencies have no verified delivery.')
                task = ready[0]; name = task['id']; job = self.state['jobs'].get(name) or self.reserve(task)
                with target_locks([task, *[self.tasks[d] for d in task['depends_on']]]):
                    for dep in task['depends_on']:
                        self.reconcile(dep, self.state['jobs'][dep])
                    if self.now() >= job['grant']['deadline']:
                        return self.stop('budget_exhausted', 'Reserved task deadline expired.', name)
                    self.guard()
                    if baseline(task) != self.baselines[name]:
                        raise ValueError('Approved target baseline or remote base changed before dispatch.')
                    job['phase'] = 'dispatching'; self.persist()
                    try:
                        self.engine(task, Path(job['folder']), job['grant'])
                        self.guard()
                        self.reconcile(name, job)
                    except Exception as error:
                        job.update(phase='blocked', failure=str(error)); self.persist()
                        return self.stop('decision_required', 'Task did not produce an accepted W1 delivery: ' + str(error), name)
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            return self.stop('approval_or_budget_required', str(error))


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['approve', 'run', 'status'])
    parser.add_argument('--queue', required=True)
    parser.add_argument('--approval')
    parser.add_argument('--state-dir')
    parser.add_argument('--decision-reference')
    args = parser.parse_args()
    if args.action == 'approve':
        if not args.approval or not args.decision_reference:
            parser.error('approve requires --approval and an actual --decision-reference')
        print(json.dumps(approve(args.queue, args.approval, args.decision_reference), ensure_ascii=False)); return
    if not args.state_dir:
        parser.error('--state-dir is required')
    folder = Path(args.state_dir).resolve()
    if args.action == 'status':
        print(json.dumps({'snapshot': read(folder / 'state.json'), 'note': 'Historical snapshot; run revalidates inputs and receipts.'}, ensure_ascii=False)); return
    if not args.approval:
        parser.error('--approval is required')
    # State-directory and queue-identity locks prevent using a fresh directory to
    # run the same approved queue twice concurrently. Durable allocation below
    # prevents a new directory from silently getting another allowance.
    locks = ROOT / '.local/queue-locks'; locks.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(str(Path(args.queue).resolve()).encode()).hexdigest()
    with lock(locks / key):
        allocation = locks / (key + '.json')
        if allocation.exists() and read(allocation)['state_dir'] != str(folder):
            parser.error('This queue already belongs to a different state directory; allowance is not renewed.')
        runner = Queue(args.queue, args.approval, folder)
        runner.guard()  # Do not allocate unapproved input.
        if not allocation.exists():
            if runner.file.exists():
                parser.error('Existing state has no original allocation receipt; allowance cannot be regenerated.')
            runner.initialize(runner.guard())
            save(allocation, {'state_dir': str(folder), 'queue': str(Path(args.queue).resolve()),
                              'initial_identity': {k: runner.state[k] for k in ['run_id', 'started_at', 'deadline', 'binding']}})
            runner.persist()
        elif (not runner.file.exists() or read(allocation).get('initial_identity') !=
              {k: runner.state.get(k) for k in ['run_id', 'started_at', 'deadline', 'binding']}):
            parser.error('Allocated state is missing or replaced; do not regenerate its allowance.')
        state = runner.run()
        print(json.dumps(state, ensure_ascii=False))
        if state['status'] != 'delivered_awaiting_merge':
            sys.exit(2)


def main():
    try:
        cli()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'attention_required', 'reason': str(error), 'merge_authorized': False}))
        sys.exit(2)


if __name__ == '__main__':
    main()
