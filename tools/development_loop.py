"""Bounded local development loop. Run with Python 3.9+; no dependencies."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def digest(root):
    """Include tracked and untracked nonignored files, including deletions."""
    names = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root
    ).split(b'\0')
    h = hashlib.sha256()
    for name in sorted(set(names) - {b''}):
        p = root / os.fsdecode(name)
        h.update(name + b'\0')
        if p.is_symlink():
            h.update(b'link:' + os.fsencode(os.readlink(p)))
        elif p.is_file():
            h.update(str(p.stat().st_mode).encode() + p.read_bytes())
        else:
            h.update(b'<deleted>')
    return h.hexdigest()


def save(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    tmp.replace(path)


def execute(argv, root, log, timeout, prompt=None):
    with log.open('w') as out:
        proc = subprocess.Popen(argv, cwd=root, stdin=subprocess.PIPE if prompt else subprocess.DEVNULL,
                                stdout=out, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        try:
            proc.communicate(prompt, timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            import signal
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            raise
    return proc.returncode


def valid_review(data, criteria):
    return (data.get('verdict') == 'pass' and data.get('blocking_findings') == []
            and data.get('decision_requests') == []
            and isinstance(data.get('criteria'), list)
            and len(data['criteria']) == len(criteria)
            and {x.get('id') for x in data['criteria']} == {x['id'] for x in criteria}
            and all(x.get('passed') is True and isinstance(x.get('evidence'), str)
                    and x['evidence'].strip() for x in data['criteria']))


@contextlib.contextmanager
def lock(path):
    with path.open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


DOCUMENTATION_CRITERION = {
    'id': 'documentation_sync',
    'requirement': (
        'Update the implementation record and affected design status/progress/remaining work '
        'in the same delivery; update master map where scope/status/navigation changes. '
        'Follow the target project documentation policy supplied by its configuration/AGENTS.md. Inspect actual source '
        'and document changes and cite concrete paths, validation and limits. '
        'Documentation-only/unaffected scope needs a specific evidence-based explanation. '
        'Missing/contradictory updates must fail; a worker assertion is not evidence.'
    ),
}


def effective_contract(contract):
    """Reserve an unremovable documentation review criterion for every task."""
    criteria = list(contract['criteria'])
    if any(x['id'] == DOCUMENTATION_CRITERION['id'] for x in criteria):
        raise ValueError('documentation_sync is reserved by the controller')
    return {**contract, 'criteria': [*criteria, dict(DOCUMENTATION_CRITERION)]}


def run(root, contract_path, state_dir, codex, max_cycles, total_seconds, project_context=None):
    controls = control_fingerprint(ROOT)
    root = root.resolve()
    contract_path = contract_path.resolve()
    state_dir = state_dir.resolve()
    if root == ROOT or ROOT in root.parents or root in ROOT.parents:
        raise ValueError('Target and controller repositories must be disjoint.')
    if root == state_dir or root in state_dir.parents:
        raise ValueError('Controller run state must be outside target repository.')
    contract = effective_contract(json.loads(contract_path.read_text()))
    if project_context:
        contract['project_context'] = project_context
    criteria = contract['criteria']
    assert criteria and len({x['id'] for x in criteria}) == len(criteria)
    assert contract['checks'] and all(isinstance(x, list) and x for x in contract['checks'])
    state_dir.mkdir(parents=True, exist_ok=True)
    with lock(state_dir / 'lock'):
        state_file = state_dir / 'state.json'
        state = json.loads(state_file.read_text()) if state_file.exists() else {'attempts': []}
        contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        execution_identity = {'target_root': str(root), 'controller_fingerprint': controls}
        if state.get('execution_identity') not in (None, execution_identity):
            raise ValueError('Target/controller changed: use a new state directory.')
        state['execution_identity'] = execution_identity
        if state.get('contract_hash') not in (None, contract_hash):
            raise ValueError('Contract changed: use a new state directory for the new contract.')
        if state.get('status') == 'decision_required':
            raise ValueError('Decision pending. Record the human decision in a new contract and use a new state directory.')
        if state.get('status') == 'complete' and state.get('tree') == digest(root):
            print('Already complete for this tree.'); return
        state['contract_hash'] = contract_hash
        started = time.monotonic()
        def remaining():
            value = int(total_seconds - (time.monotonic() - started))
            if value <= 0:
                raise subprocess.TimeoutExpired('total budget', total_seconds)
            return value
        def checkpoint(status):
            state['status'] = status
            save(state_file, state)
        feedback = json.dumps(state.get('last_review', {}), ensure_ascii=False)
        try:
            for _ in range(max_cycles):
                remaining()
                n = len(state['attempts']) + 1
                folder = state_dir / ('attempt-%03d' % n)
                folder.mkdir()
                attempt = {'id': n, 'directory': str(folder)}
                state['attempts'].append(attempt)
                checkpoint('implementing')
                prompt = ('Read target AGENTS.md and the supplied project documentation policy. Fulfill this contract only. '
                          'Do not modify the contract, workflow control files, acceptance criteria, or evaluation labels. '
                          'Do not commit, publish, deploy, or edit original private sources. '
                          'If a human decision is necessary, do only independent preparation, then stop. '
                          'Final JSON must contain decision_requests (array of strings) and summary (string).\n'
                          + json.dumps(contract, ensure_ascii=False) + '\nPrevious review: ' + feedback)
                result = folder / 'implementation.json'
                code = execute([codex, 'exec', '-C', str(root), '-s', 'workspace-write',
                                '--output-schema', str(ROOT / 'schemas/implementation.schema.json'),
                                '-o', str(result), '-'], root, folder / 'implementation.log', remaining(), prompt)
                if code or not result.exists():
                    checkpoint('execution_failed'); return
                output = json.loads(result.read_text())
                if output.get('decision_requests'):
                    state['decision_requests'] = output['decision_requests']
                    checkpoint('decision_required'); return
                # Never let a worker silently rewrite policy or its own completion gate.
                if contract_hash != hashlib.sha256(contract_path.read_bytes()).hexdigest():
                    checkpoint('policy_changed'); return
                if controls != control_fingerprint(ROOT):
                    checkpoint('policy_changed'); return
                tree = digest(root)
                checkpoint('checking')
                results = []
                for i, argv in enumerate(contract['checks']):
                    results.append({'argv': argv, 'exit_code': execute(
                        argv, root, folder / ('check-%d.log' % i), remaining())})
                attempt['checks'] = results
                if tree != digest(root):
                    checkpoint('tree_changed_during_checks'); return
                if any(x['exit_code'] for x in results):
                    feedback = json.dumps(results)
                    state['last_review'] = {'failed_checks': results}
                    checkpoint('changes_requested'); continue
                checkpoint('reviewing')
                review_path = folder / 'review.json'
                prompt = ('Independently audit the current repository against this contract. '
                          'Read original requirements and actual source/test changes, not just worker claims. '
                          'Inspect check logs at ' + str(folder) + '. Do not modify any files. '
                          'Missing or inconclusive evidence must fail. Detect weakened tests, omitted negative controls, '
                          'conceptual drift, and scope expansion. Report human decisions separately. '
                          'For each criterion cite concrete files and observed results.\n' + json.dumps(contract, ensure_ascii=False))
                code = execute([codex, 'exec', '-C', str(root), '-s', 'read-only',
                                '--output-schema', str(ROOT / 'schemas/review.schema.json'),
                                '-o', str(review_path), '-'], root, folder / 'review.log', remaining(), prompt)
                if code or not review_path.exists():
                    checkpoint('review_failed'); return
                review = json.loads(review_path.read_text())
                state['last_review'] = review
                feedback = json.dumps(review, ensure_ascii=False)
                if tree != digest(root) or controls != control_fingerprint(ROOT):
                    checkpoint('tree_changed_during_review'); return
                if review.get('decision_requests'):
                    state['decision_requests'] = review['decision_requests']
                    checkpoint('decision_required'); return
                if valid_review(review, criteria):
                    state['tree'] = tree
                    checkpoint('complete'); return
                checkpoint('changes_requested')
            checkpoint('cycle_limit')
        except subprocess.TimeoutExpired:
            checkpoint('time_limit')
        except KeyboardInterrupt:
            checkpoint('interrupted')
        except Exception as error:
            state['error'] = str(error)
            checkpoint('execution_failed')
            raise
        finally:
            print(json.dumps({'status': state.get('status'), 'state': str(state_file)}, ensure_ascii=False))


def control_fingerprint(root):
    h = hashlib.sha256()
    paths = [root / 'AGENTS.md', root / 'tools/development_loop.py']
    for directory in ('schemas', 'projects', 'contracts'):
        paths += sorted((root / directory).rglob('*'))
    for path in paths:
        if path.is_file():
            h.update(str(path.relative_to(root)).encode() + path.read_bytes())
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['status', 'run'])
    p.add_argument('--project', required=True, help='Target project configuration')
    p.add_argument('--contract', help='Contract path relative to controller repository')
    p.add_argument('--state-dir', help='State directory under controller .local/')
    p.add_argument('--codex', default='codex')
    p.add_argument('--max-cycles', type=int, default=3)
    p.add_argument('--total-seconds', type=int, default=1800)
    args = p.parse_args()
    if args.max_cycles < 1 or args.total_seconds < 1:
        p.error('Limits must be positive')
    project = json.loads((ROOT / args.project).resolve().read_text())
    root = (ROOT / project['root']).resolve()
    contract_path = (ROOT / (args.contract or project['contract'])).resolve()
    if not contract_path.is_relative_to(ROOT / 'contracts'):
        p.error('contract must be under controller contracts/')
    project_id = project['id']
    if not project_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in project_id):
        p.error('Invalid project id')
    state_dir = (ROOT / (args.state_dir or ('.local/runs/' + project_id + '/' + contract_path.stem))).resolve()
    if not state_dir.is_relative_to(ROOT / '.local/runs'):
        p.error('state-dir must be under controller .local/runs/')
    if args.action == 'status':
        file = state_dir / 'state.json'
        print(file.read_text() if file.exists() else 'Not started')
        return
    # One lock per target prevents different milestones writing it concurrently.
    lock_dir = ROOT / '.local/locks'
    lock_dir.mkdir(parents=True, exist_ok=True)
    target_key = hashlib.sha256(str(root).encode()).hexdigest()
    with lock(lock_dir / target_key):
        run(root, contract_path, state_dir, args.codex, args.max_cycles, args.total_seconds, project_context=project)


if __name__ == '__main__':
    main()
