"""W1 opt-in branch/report delivery. Legacy development_loop.py is unchanged."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

from development_loop import effective_contract, lock, save, valid_review
from delivery_evidence import Budget, Halt, Recorder, browser_run, fingerprint, git, manifest, environment_identity
from delivery_publish import Publisher

ROOT = Path(__file__).resolve().parents[1]


def expanded(argv, target, evidence):
    return [a.replace('{target}', str(target)).replace('{evidence}', str(evidence)) for a in argv]


def worker_output(data):
    return (isinstance(data, dict) and isinstance(data.get('summary'), str)
            and isinstance(data.get('decision_requests'), list)
            and all(isinstance(x, str) for x in data['decision_requests']))


def decision_packet(reason, status):
    return {'reason': reason, 'outcome': status,
            'options': ['Resolve the stated capability/conflict using the recorded evidence.',
                        'Explicitly authorize a revised contract/budget in a new linked run.'],
            'impact': 'Current candidate is not accepted for merging. Historical attempts and any safe branch publication are preserved.',
            'recommendation': 'Keep acceptance criteria fixed; repair the concrete environment/implementation before resuming.'}


class Delivery:
    def __init__(self, project_path, state_dir, seconds=3600, cycles=3, codex='codex'):
        self.project_path, self.dir = project_path.resolve(), state_dir.resolve()
        self.project = json.loads(self.project_path.read_text())
        self.root = (ROOT / self.project['root']).resolve()
        self.contract_path = (ROOT / self.project['contract']).resolve()
        self.contract = effective_contract(json.loads(self.contract_path.read_text()))
        self.codex, self.seconds, self.cycles = codex, seconds, cycles
        if (ROOT == self.root or ROOT in self.root.parents or self.root in ROOT.parents
                or self.dir == self.root or self.root in self.dir.parents):
            raise ValueError('Controller/target/evidence must be disjoint; controller cannot target itself.')
        if self.project.get('schema_version') != 2:
            raise ValueError('Explicit delivery project schema_version=2 is required.')
        if not self.contract.get('allowed_paths') or not self.contract.get('checks'):
            raise ValueError('Frozen allowed_paths and trusted checks are required.')
        if not self.contract_path.is_relative_to(ROOT / 'contracts'):
            raise ValueError('Execution contract must be in controller contracts/.')
        for path in self.contract['allowed_paths']:
            if Path(path).is_absolute() or '..' in Path(path).parts:
                raise ValueError('Task publication paths must be target-relative.')
        self.dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.dir / 'state.json'
        self.state = json.loads(self.state_file.read_text()) if self.state_file.exists() else {}
        if self.state and self.state.get('schema_version') != 2:
            raise ValueError('Legacy states are preserved; create a new W1 run instead of migrating complete.')
        if not self.state:
            self.state = {'schema_version': 2, 'run_id': uuid.uuid4().hex, 'state_dir': str(self.dir),
                          'target': str(self.root), 'baseline_head': git(self.root, 'rev-parse', 'HEAD'),
                          'initial_manifest': manifest(self.root), 'attempts': [], 'status': 'preflight'}
            if git(self.root, 'status', '--porcelain'):
                raise ValueError('Use an isolated clean baseline; original dirty checkout must be preserved.')
            link = self.project.get('parent_budget')
            if link:
                parent_path = Path(link['state_file']).resolve()
                parent = json.loads(parent_path.read_text())
                if parent.get('schema_version') != 2 or not link.get('reason'):
                    raise ValueError('Linked revalidation needs explicit reason and version-2 parent budget.')
                if parent.get('status') != 'ready_for_merge_approval':
                    prior = parent.get('last_review', {})
                    resolution_path = Path(link.get('format_resolution', '/missing')).resolve()
                    resolution = json.loads(resolution_path.read_text()) if resolution_path.is_file() else {}
                    normalized = dict(prior)
                    normalized['decision_requests'] = []
                    try:
                        contradictory = prior.get('decision_requests') and valid_review(normalized, self.contract['criteria'])
                    except (AttributeError, TypeError):
                        contradictory = False
                    if not contradictory or not valid_review(resolution, self.contract['criteria']):
                        raise ValueError('Unresolved genuine parent decisions cannot be bypassed by linking a new run.')
                    binding_path = Path(link.get('format_resolution_binding', '/missing')).resolve()
                    binding = json.loads(binding_path.read_text()) if binding_path.is_file() else {}
                    prior_review_input = Path(parent['attempts'][-1]['folder']) / 'review.input.json'
                    expected = json.loads(prior_review_input.read_text())['digest']
                    if (binding.get('target_digest') != expected or manifest(Path(parent['target']))['digest'] != expected
                            or binding.get('resolution_sha256') != hashlib.sha256(resolution_path.read_bytes()).hexdigest()):
                        raise ValueError('Format clarification must bind unchanged original reviewed source and exact resolution.')
                    self.state['format_resolution'] = str(resolution_path)
                old_contract_hash = parent.get('controls', {}).get('protected', {}).get(str(self.contract_path))
                if old_contract_hash != hashlib.sha256(self.contract_path.read_bytes()).hexdigest():
                    raise ValueError('Linked pilot must preserve the exact task contract.')
                self.state['budget'] = copy.deepcopy(parent['budget'])
                self.state['attempts'] = copy.deepcopy(parent.get('attempts', []))
                self.state['parent_budget'] = {'state_file': str(parent_path), 'reason': link['reason'],
                                               'status_at_link': parent['status'],
                                               'sha256': hashlib.sha256(parent_path.read_bytes()).hexdigest()}
                allocation = parent_path.with_name(parent_path.name + '.child.json')
                bindings = self.journal_bindings(parent_path, link)
                if allocation.exists():
                    prior = json.loads(allocation.read_text())
                    if (prior.get('child_state') != str(self.state_file) or prior.get('phase') != 'allocated'
                            or prior.get('bindings') != bindings or self.state_file.exists()):
                        raise ValueError('Parent budget already allocated; resume its recorded child or obtain explicit new authorization.')
                    # No execution can start until state persistence and activation.
                    # Recover the original run ID/deadline/counters, never regenerate.
                    self.state = copy.deepcopy(prior['initial_state'])
                else:
                    receipt = {'child_state': str(self.state_file), 'phase': 'allocated',
                               'bindings': bindings, 'initial_state': copy.deepcopy(self.state)}
                    temporary = allocation.with_name(allocation.name + '.' + uuid.uuid4().hex + '.pending')
                    with temporary.open('x') as stream:
                        json.dump(receipt, stream, sort_keys=True)
                        stream.flush()
                        os.fsync(stream.fileno())
                    try:
                        # Hard-link is exclusive and exposes only a complete journal.
                        os.link(temporary, allocation)
                    except FileExistsError:
                        raise ValueError('Parent budget concurrently allocated; retry recorded child only.')
                    finally:
                        temporary.unlink()
            self.persist()
        pending_allocation = None
        if self.project.get('parent_budget'):
            parent_path = Path(self.project['parent_budget']['state_file']).resolve()
            allocation = parent_path.with_name(parent_path.name + '.child.json')
            receipt = json.loads(allocation.read_text())
            if receipt.get('phase') == 'allocated':
                if receipt['child_state'] != str(self.state_file) or receipt['initial_state']['run_id'] != self.state['run_id']:
                    raise ValueError('Allocation/state identity mismatch; no allowance regenerated.')
                if receipt['bindings'] != self.journal_bindings(parent_path, self.project['parent_budget']):
                    raise ValueError('Journal inputs changed after child persistence; original bindings cannot be replaced.')
                pending_allocation = (allocation, receipt, parent_path)
        if self.state['target'] != str(self.root):
            raise ValueError('Run is bound to a different target root.')
        protected = [self.project_path, self.contract_path]
        protected += [Path(p).resolve() for p in self.project.get('protected_files', [])]
        if self.project.get('parent_budget'):
            protected.append(Path(self.project['parent_budget']['state_file']).resolve())
            if self.project['parent_budget'].get('format_resolution'):
                protected.append(Path(self.project['parent_budget']['format_resolution']).resolve())
                protected.append(Path(self.project['parent_budget']['format_resolution_binding']).resolve())
        self.protected_paths = protected
        current = {'controller': manifest(ROOT)['digest'], 'protected': fingerprint(protected)}
        if len(current['protected']) != len(set(str(p.resolve()) for p in protected)):
            raise ValueError('A required protected input is missing.')
        if 'controls' not in self.state:
            self.state['controls'] = current
            self.persist()
        try:
            self.guard()
        except Halt as error:
            self.state['handoff'] = decision_packet(error.message, error.status)
            self.checkpoint(error.status)
            raise
        if pending_allocation:
            allocation, receipt, parent_path = pending_allocation
            if receipt['bindings'] != self.journal_bindings(parent_path, self.project['parent_budget']):
                raise ValueError('Journal inputs changed before activation; no fresh controls accepted.')
            # Controls are durable and verified before activation. A crash on
            # either side resumes against original policy, never fresh inputs.
            receipt['phase'] = 'active'
            save(allocation, receipt)
        self.budget = Budget(self.state, self.persist, seconds, cycles)
        self.folder = self.dir / ('preflight-%03d' % len(list(self.dir.glob('preflight-*'))))
        self.recorder = Recorder(self.root, self.state, self.persist, self.budget, self.folder, self.guard)
        self.publisher = Publisher(self.recorder, self.project['delivery'], self.contract, self.state, self.persist)

    def journal_bindings(self, parent_path, link):
        external = [Path(p).resolve() for p in self.project.get('protected_files', [])]
        external += [Path(link[p]).resolve() for p in ['format_resolution', 'format_resolution_binding'] if p in link]
        return {'protected': fingerprint(external),
                'project': hashlib.sha256(self.project_path.read_bytes()).hexdigest(),
                'contract': hashlib.sha256(self.contract_path.read_bytes()).hexdigest(),
                'controller': manifest(ROOT)['digest'], 'target': manifest(self.root)['digest'],
                'parent': hashlib.sha256(parent_path.read_bytes()).hexdigest()}

    def persist(self):
        save(self.state_file, self.state)

    def checkpoint(self, status):
        self.state['status'] = status
        self.persist()

    def guard(self):
        current = {'controller': manifest(ROOT)['digest'], 'protected': fingerprint(self.protected_paths)}
        if current != self.state['controls']:
            raise Halt('decision_required', 'Protected contract/evaluator/controller inputs changed; old evidence invalid. Owner decision required.')

    def recorder_at(self, folder):
        self.recorder = Recorder(self.root, self.state, self.persist, self.budget, folder, self.guard)
        self.publisher.r = self.recorder

    def preflight(self):
        self.guard()
        self.budget.remaining(reserve=120)
        self.publisher.preflight()
        browser = self.project.get('browser')
        if not browser:
            raise Halt('capability_blocked', 'A real browser adapter configuration is required before worker execution.')
        probe = self.recorder.folder / 'probe'
        probe.mkdir(exist_ok=True)
        (probe / 'index.html').write_text('<!doctype html><pre id="results">RUNNING</pre><script>document.getElementById("results").textContent=JSON.stringify({status:"PASS",userAgent:navigator.userAgent});</script>')
        result = browser_run(self.recorder, browser['executable'], probe, 'probe')
        if result.get('status') != 'PASS' or 'HeadlessChrome' not in result.get('userAgent', ''):
            raise Halt('capability_blocked', 'Actual Chrome preflight did not execute JavaScript.')
        self.environment_probes()
        if self.recorder.command([self.codex, '--version'], 'worker-capability', cap=20):
            raise Halt('capability_blocked', 'Codex CLI unavailable.')
        self.publisher.scope()

    def environment_probes(self):
        probes = []
        for i, argv in enumerate(self.project.get('environment_commands', [])):
            label = 'environment-%d-%d' % (i, len(list(self.recorder.folder.glob('environment-*.log'))))
            if self.recorder.command(argv, label, cap=30):
                raise Halt('capability_blocked', 'Configured test dependency/environment probe failed.')
            probes.append({'argv': argv, 'sha256': hashlib.sha256((self.recorder.folder / (label + '.log')).read_bytes()).hexdigest()})
        binding = {'inherited': environment_identity(), 'dependency_probes': probes}
        previous = self.state.get('environment_binding')
        self.state['environment_binding'] = binding
        self.persist()
        if previous is not None and previous != binding:
            self.state.pop('accepted_digest', None)
            self.persist()
            raise Halt('changes_requested', 'Environment/dependency identity changed; prior review is stale.')
        return binding

    def phase_context(self):
        return json.dumps({'contract': self.contract, 'project_context': self.project,
                           'run_evidence': {'state_file': str(self.state_file),
                                            'attempt_directory': str(self.recorder.folder),
                                            'reports_directory': str(self.dir / 'reports')},
                           'baseline_head': self.state['baseline_head'], 'source_digest': manifest(self.root)['digest']}, ensure_ascii=False)

    def implement(self, feedback):
        for key in ['accepted_digest', 'accepted_parent', 'accepted_environment', 'accepted_dependency_binding']:
            self.state.pop(key, None)
        self.checkpoint('implementing')
        before_head = git(self.root, 'rev-parse', 'HEAD')
        result = self.recorder.folder / 'implementation.json'
        prompt = ('Read target AGENTS.md and supplied documentation policy. Implement only allowed_paths and fixed criteria. '
                  'Do not edit controller, contracts, protected tests/evaluator, original private data or evidence. '
                  'Do not commit/push/merge/create PR. Record genuine owner decisions; do not decide them yourself. '
                  'Update implementation record and related design status, with precise scope and limitations. '
                  'Documentation is written before controller verification: describe current behavior and limits, '
                  'label earlier check results as historical observations of their exact earlier candidate, and link '
                  'the stable run evidence location for current verification and final report. Never claim an earlier '
                  'digest certifies this candidate. Do not embed a claimed final digest of documents that contain it: '
                  'editing such a digest changes the digest again. The external report binds final source and results. '
                  'If previous failures exist, first inspect their exact logs and project observations. '
                  'Fix the failing condition, not only documentation. Inspect callers before renaming public test/helper names used by fixed evaluators. '
                  'The controller will run verification and record final results externally; do not invent test outcomes.\n'
                  + self.phase_context() + '\nPrevious actual failures/review: ' + json.dumps(feedback, ensure_ascii=False))
        code = self.recorder.command([self.codex, 'exec', '-C', str(self.root), '-s', 'workspace-write',
                                      '--output-schema', str(ROOT / 'schemas/implementation.schema.json'),
                                      '-o', str(result), '-'], 'implementation', prompt=prompt, cap=900, reserve=180)
        if code or not result.is_file():
            raise Halt('capability_blocked', 'Worker did not produce a valid result.')
        data = json.loads(result.read_text())
        if not worker_output(data):
            raise Halt('changes_requested', 'Worker result violates required schema.')
        if git(self.root, 'rev-parse', 'HEAD') != before_head:
            raise Halt('decision_required', 'Worker changed Git history; publication is reserved for controller.')
        if data['decision_requests']:
            self.state['decision_requests'] = data['decision_requests']
            raise Halt('decision_required', '; '.join(data['decision_requests']))
        self.publisher.scope()
        self.state.setdefault('implementation_summaries', []).append({'folder': str(self.recorder.folder), 'summary': data['summary']})
        self.persist()
        return data

    def failure_feedback(self, kind, message):
        folder = self.recorder.folder
        return {kind: message, 'log_directory': str(folder),
                'raw_outputs': [str(p) for p in sorted(folder.glob('*.log'))],
                'execution_records': [str(p) for p in sorted(folder.glob('*-execution.json'))],
                'project_observations': [str(p) for p in sorted((folder / 'browser').glob('*.json'))]}

    def checks_and_browser(self):
        self.checkpoint('checking')
        before = manifest(self.root)
        results = []
        for i, argv in enumerate(self.contract['checks']):
            code = self.recorder.command(expanded(argv, self.root, self.recorder.folder), 'check-%d' % i, cap=300, reserve=120)
            results.append({'argv': argv, 'exit_code': code, 'evidence': str(self.recorder.folder / ('check-%d-execution.json' % i))})
        if before != manifest(self.root):
            raise Halt('changes_requested', 'Target changed during verification; observations are stale.')
        if any(r['exit_code'] for r in results):
            return {'failed_checks': results}
        self.checkpoint('browser_verifying')
        cfg = self.project['browser']
        directory = self.recorder.folder / 'browser'
        directory.mkdir(exist_ok=True)
        if self.recorder.command(expanded(cfg['prepare'], self.root, self.recorder.folder), 'browser-prepare', cap=90, reserve=120):
            return self.failure_feedback('browser_failed', 'Project harness preparation failed.')
        result = browser_run(self.recorder, cfg['executable'], directory)
        if result.get('status') != 'PASS':
            return self.failure_feedback('browser_failed', result)
        # Project validator consumes exact raw actual-browser result, never a copied pass flag.
        save(directory / cfg.get('result_file', 'browser-result.json'), result)
        if self.recorder.command(expanded(cfg['validate'], self.root, self.recorder.folder), 'browser-validate', cap=90, reserve=120):
            return self.failure_feedback('browser_failed', 'Project-specific browser/evidence validator failed.')
        if before != manifest(self.root):
            raise Halt('changes_requested', 'Source/docs changed during browser execution; repeat all required verification.')
        return {}

    def review(self):
        for key in ['accepted_digest', 'accepted_parent', 'accepted_environment', 'accepted_dependency_binding']:
            self.state.pop(key, None)
        self.checkpoint('reviewing')
        before = manifest(self.root)
        result = self.recorder.folder / 'review.json'
        prompt = ('Independent read-only audit. Read original fixed requirements, actual source/tests/docs diff and verification evidence. '
                  'Do not modify files or run other agents. Missing/ambiguous evidence must fail. Check meaningful negative cases, '
                  'scope, conceptual drift and weakening of protected expectations. Passing tests never override semantic findings. '
                  'Review documentation changes and actual evidence, not worker claims. Return all criterion IDs once with evidence; '
                  'Documentation is authored before these checks. Require accurate behavior/progress/limits and clear '
                  'provenance, not a self-referential final source digest or current check outcome inside the checked '
                  'documents. Clearly labeled historical checks may remain historical; they never establish current '
                  'acceptance. Verify this exact candidate using this attempt input manifests, checks and browser bindings; '
                  'the external final report binds current outcomes after review. Reject misleading claims that historical '
                  'results certify current source, missing documentation, or actual contradictions. Do not demand edits '
                  'solely to replace a clearly historical attempt number with the latest attempt number. '
                  'report actual owner decisions separately. Inspect only task-related files and concise logs; do not read the whole repository. '
                  'Evidence directory: ' + str(self.recorder.folder) + '\n' + self.phase_context())
        prompt += '\nFormatting: decision_requests must be [] when no actual human choice is necessary. Never put sentences such as no decisions into that array. A pass verdict must have zero blockers and zero decision requests.'
        for formatting_attempt in range(2):
            label = 'review' if formatting_attempt == 0 else 'review-format'
            result = self.recorder.folder / (label + '.json')
            code = self.recorder.command([self.codex, 'exec', '-C', str(self.root), '-s', 'read-only',
                                          '--output-schema', str(ROOT / 'schemas/review.schema.json'),
                                          '-o', str(result), '-'], label, prompt=prompt,
                                         cap=240 if formatting_attempt == 0 else 60, reserve=60)
            if code or not result.is_file():
                return {'invalid_review': 'Independent review unavailable; no acceptance.'}
            data = json.loads(result.read_text())
            if not isinstance(data, dict) or not isinstance(data.get('decision_requests'), list):
                return {'invalid_review': data}
            contradictory = data.get('verdict') == 'pass' and (data.get('decision_requests') or data.get('blocking_findings'))
            if not contradictory:
                break
            # Do not discard decisions or retry a valid negative semantic judgment.
            # Ask the independent reviewer to resolve its internally inconsistent
            # pass/decision result once; both original and clarification survive.
            prompt += '\nYour previous internally inconsistent result was: ' + json.dumps(data) + '\nClarify format only: preserve semantic findings. If an actual human choice is needed, return changes_requested with its concrete question. Otherwise return decision_requests=[]; never claim an owner authorized a choice.'
        if data.get('verdict') == 'pass' and (data.get('decision_requests') or data.get('blocking_findings')):
            return {'invalid_review': data, 'reason': 'Contradictory pass result after bounded clarification.'}
        self.state['last_review'] = data
        self.persist()
        if before != manifest(self.root):
            return {'stale_review': 'Source/docs changed during independent review.'}
        if data.get('decision_requests'):
            self.state['decision_requests'] = data['decision_requests']
            raise Halt('decision_required', '; '.join(data['decision_requests']))
        try:
            passed = valid_review(data, self.contract['criteria'])
        except (AttributeError, TypeError):
            return {'invalid_review': data}
        if not passed:
            return {'review': data}
        self.state.update(accepted_digest=before['digest'], accepted_parent=git(self.root, 'rev-parse', 'HEAD'),
                          accepted_environment=environment_identity(), accepted_dependency_binding=self.state.get('environment_binding'))
        self.persist()
        return {}

    def publish_and_check(self):
        self.environment_probes()
        self.checkpoint('publishing')
        head = self.publisher.publish()
        self.checkpoint('remote_checking')
        ci = self.publisher.ci(head, cap=self.project.get('ci_timeout_seconds', 300))
        self.state['last_ci'] = ci
        self.persist()
        if ci['status'] != 'success':
            return {'remote_failure': ci, 'log_directory': str(self.recorder.folder)}
        self.guard()
        if manifest(self.root)['digest'] != self.state['accepted_digest']:
            return {'stale_after_ci': 'Current source differs from accepted revision.'}
        if self.publisher.remote_head(self.project['delivery']['head']) != head or self.publisher.remote_head(self.project['delivery']['base']) != self.state['base_sha']:
            return {'remote_moved': 'Remote changed before owner handoff; revalidation required.'}
        self.checkpoint('reporting')
        self.publisher.report('ready_for_merge_approval', 'All current checks and independent review passed; owner merge authorization pending.', ci)
        self.checkpoint('ready_for_merge_approval')
        return None

    def incomplete(self, error):
        origin = error.status
        self.state['handoff'] = decision_packet(error.message, origin)
        self.state['origin_status'] = origin
        self.checkpoint(origin)
        # A failed implementation can still be saved, but only after an independent
        # publication-safety review within the original time allowance, never by
        # promoting a failed semantic review to accepted.
        try:
            if not self.publisher.scope() or not git(self.root, 'status', '--porcelain'):
                self.publisher.report(origin, error.message, self.state.get('last_ci'))
                return
            if origin == 'decision_required' and 'inputs changed' in error.message:
                raise Halt('publication_blocked', 'Protected inputs changed; no trusted safety review can be started.')
            self.budget.remaining(reserve=15)
            result = self.recorder.folder / 'publication-safety.json'
            current = manifest(self.root)['digest']
            prompt = ('Read-only publication-safety review ONLY: task is incomplete. Do not claim semantic acceptance. '
                      'Inspect actual task diff and allowed_paths. Is it safe to save precisely these changes on the configured '
                      'incomplete dedicated branch without unrelated files/private original data? No edits or agents. '
                      'Return safe, exact files, blockers, decisions and concrete evidence.\n' + self.phase_context())
            code = self.recorder.command([self.codex, 'exec', '-C', str(self.root), '-s', 'read-only',
                                          '--output-schema', str(ROOT / 'schemas/publication.schema.json'),
                                          '-o', str(result), '-'], 'publication-safety', prompt=prompt, cap=90, reserve=10)
            data = json.loads(result.read_text()) if result.exists() else {}
            if (code or data.get('safe') is not True or data.get('blocking_findings') != []
                    or data.get('decision_requests') != [] or not data.get('evidence')
                    or set(data.get('files', [])) != set(self.publisher.scope())
                    or manifest(self.root)['digest'] != current):
                raise Halt('publication_blocked', 'Incomplete publication safety was not established by independent review.')
            self.state.update(publication_safety_digest=current, publication_parent=git(self.root, 'rev-parse', 'HEAD'),
                              publication_safety_environment=environment_identity())
            self.persist()
            self.publisher.publish(incomplete=True)
            self.checkpoint('incomplete_published')
            self.publisher.report('incomplete_published', error.message, self.state.get('last_ci'))
        except (Halt, OSError, ValueError, subprocess.SubprocessError) as blocked:
            self.state['publication_blocked_reason'] = str(blocked)
            self.persist()
            try:
                self.publisher.report(origin, error.message + ' Publication blocked: ' + str(blocked), self.state.get('last_ci'))
            except Exception as report_error:
                self.state['report_error'] = str(report_error)
                self.persist()

    def run(self):
        if self.state['status'] in {'decision_required', 'budget_exhausted', 'incomplete_published'}:
            raise ValueError('Stopped run requires recorded explicit resolution/new linked authorization; restart is not approval.')
        try:
            self.preflight()
            feedback = self.state.get('feedback', {})
            if self.state.get('accepted_digest') == manifest(self.root)['digest']:
                feedback = self.publish_and_check()
                if feedback is None:
                    return self.state
            while True:
                cycle = self.budget.cycle()
                folder = self.dir / ('attempt-%03d' % cycle)
                self.recorder_at(folder)
                attempt = {'cycle': cycle, 'folder': str(folder), 'started_at': time.time()}
                self.state['attempts'].append(attempt)
                self.persist()
                try:
                    self.implement(feedback)
                    feedback = self.checks_and_browser()
                    if not feedback:
                        feedback = self.review()
                    if not feedback:
                        feedback = self.publish_and_check()
                        if feedback is None:
                            attempt['outcome'] = 'ready_for_merge_approval'
                            self.persist()
                            return self.state
                except Halt as error:
                    if error.status != 'changes_requested':
                        raise
                    feedback = {'invalidation': error.message}
                attempt['outcome'] = 'changes_requested'
                attempt['feedback'] = feedback
                self.state['feedback'] = feedback
                self.checkpoint('changes_requested')
        except Halt as error:
            self.incomplete(error)
        except (OSError, ValueError, subprocess.SubprocessError, KeyError) as error:
            self.incomplete(Halt('capability_blocked', str(error)))
        return self.state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['run', 'status'])
    p.add_argument('--project', required=True)
    p.add_argument('--state-dir', required=True)
    p.add_argument('--max-cycles', type=int, default=3)
    p.add_argument('--total-seconds', type=int, default=3600)
    p.add_argument('--codex', default='codex')
    args = p.parse_args()
    if min(args.max_cycles, args.total_seconds) < 1:
        p.error('Limits must be positive.')
    project = (ROOT / args.project).resolve()
    folder = Path(args.state_dir).resolve()
    if args.action == 'status':
        data = json.loads((folder / 'state.json').read_text())
        print(json.dumps({'status_as_recorded': data['status'], 'report': data.get('report'),
                          'note': 'Historical snapshot; run performs live input/remote revalidation.'}))
        return
    cfg = json.loads(project.read_text())
    target = (ROOT / cfg['root']).resolve()
    locks = ROOT / '.local/locks'
    locks.mkdir(parents=True, exist_ok=True)
    with lock(locks / hashlib.sha256(str(target).encode()).hexdigest()):
        delivery = None
        try:
            delivery = Delivery(project, folder, args.total_seconds, args.max_cycles, args.codex)
            state = delivery.run()
        except Halt as error:
            if delivery is not None:
                delivery.incomplete(error)
                state = delivery.state
            else:
                state_file = folder / 'state.json'
                state = json.loads(state_file.read_text()) if state_file.exists() else {}
                state.update(status=error.status, handoff=decision_packet(error.message, error.status))
                if state_file.exists():
                    save(state_file, state)
        except ValueError as error:
            print(json.dumps({'status': 'configuration_blocked', 'reason': str(error)}))
            sys.exit(2)
        print(json.dumps({'status': state['status'], 'state': str(folder / 'state.json'), 'report': state.get('report')}, ensure_ascii=False))
        if state['status'] != 'ready_for_merge_approval':
            sys.exit(2)


if __name__ == '__main__':
    main()
