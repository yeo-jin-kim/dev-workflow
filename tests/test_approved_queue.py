"""W2 fault tests: real W1/Git integration with explicitly synthetic AI/CI fixtures."""
import copy
import contextlib
import io
import html
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import approved_queue as queue
from development_loop import save
import test_delivery_loop as fixtures


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.DeliveryTests()
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        project = json.loads(f.project.read_text()); project['delivery']['mode'] = 'branch_report'; save(f.project, project)
        def browser(recorder, executable, directory, label='browser', **kwargs):
            directory.mkdir(exist_ok=True)
            entry = directory / 'index.html'; entry.write_text('Synthetic protocol fixture, not a real browser.')
            result = {'status': 'PASS', 'userAgent': 'HeadlessChrome synthetic fixture; not real browser execution'}
            save(recorder.folder / (label + '-result.json'), result)
            (recorder.folder / (label + '-version.log')).write_text('Chrome synthetic fixture')
            (recorder.folder / (label + '-dom.log')).write_text('<pre id="results">' + html.escape(json.dumps(result)) + '</pre>')
            digest = queue.manifest(recorder.root)['digest']
            for suffix in ['version', 'dom']:
                save(recorder.folder / (label + '-' + suffix + '-execution.json'),
                     {'argv': [executable], 'input_digest': digest, 'exit_code': 0, 'synthetic': True})
            save(recorder.folder / (label + '-binding.json'), {
                'target_digest': digest, 'engine': 'actual Chrome headless', 'browser_version': 'Chrome synthetic fixture',
                'harness': {'index.html': queue.hashlib.sha256(entry.read_bytes()).hexdigest()},
                'result_sha256': queue.hashlib.sha256((recorder.folder / (label + '-result.json')).read_bytes()).hexdigest(),
                'synthetic_protocol_fixture': True})
            return result
        f.browser_mock.side_effect = browser
        self.base, self.control = f.base, f.control
        (self.control / '.gitignore').write_text('.local/\n')
        p = patch.object(queue, 'ROOT', self.control); p.start(); self.addCleanup(p.stop)
        self.path = self.base / 'queue.json'; self.approval = self.base / 'approval.json'; self.state = self.base / 'queue-state'
        self.config = {'schema_version': 1, 'id': 'test-approved-queue',
                       'limits': {'window_seconds': 600, 'max_tasks': 3, 'max_reserved_seconds': 1200, 'max_reserved_cycles': 9},
                       'project_limits': {f.env['FIXTURE_REPO']: {'max_tasks': 3, 'max_reserved_seconds': 1200, 'max_reserved_cycles': 9}},
                       'tasks': [{'id': 'first', 'project': str(f.project), 'total_seconds': 300, 'max_cycles': 3}]}
        save(self.path, self.config); self.approve()
        self.executed = []

    def approve(self):
        if self.approval.exists(): self.approval.unlink()
        queue.approve(self.path, self.approval, 'Synthetic owner authorization in test only')

    def fake_engine(self, task, folder, grant):
        self.executed.append(task['id']); folder.mkdir(parents=True)
        save(folder / 'synthetic.json', {'id': task['id'], 'deadline': grant['deadline']})

    def fake_verify(self, task, folder, grant):
        if not (folder / 'synthetic.json').exists(): raise ValueError('No verified receipt')
        return {'head': task['id'], 'report': str(folder / 'synthetic.json')}

    def runner(self):
        return queue.Queue(self.path, self.approval, self.state, self.fake_engine, self.fake_verify)

    def second(self, depends=True):
        f = self.fixture
        root = self.base / 'second-target'; f.cmd('git', 'clone', '-q', str(f.remote), str(root), cwd=self.base)
        f.cmd('git', 'checkout', '-qb', 'second', 'origin/main', cwd=root)
        cfg = json.loads(f.project.read_text()); cfg['root'] = str(root); cfg['delivery']['head'] = 'second'
        project = self.base / 'second-project.json'; save(project, cfg)
        self.config['tasks'].append({'id': 'second', 'project': str(project), 'depends_on': ['first'] if depends else [], 'total_seconds': 300, 'max_cycles': 3})
        save(self.path, self.config); self.approve()

    def test_w2_real_w1_gate_chain_and_idempotent_queue_restart(self):
        runner = queue.Queue(self.path, self.approval, self.state)
        result = runner.run(); self.assertEqual(result['status'], 'delivered_awaiting_merge')
        self.assertEqual(result['jobs']['first']['phase'], 'delivered')
        first = json.loads((self.fixture.fixture_state / 'workers').read_text())
        again = queue.Queue(self.path, self.approval, self.state).run()
        self.assertEqual(again['status'], 'delivered_awaiting_merge')
        self.assertEqual(int((self.fixture.fixture_state / 'workers').read_text()), first)
        self.assertFalse(result['handoff']['merge_authorized'])

    def test_w2_missing_approval_does_not_dispatch_and_can_be_approved_later(self):
        self.approval.unlink(); result = self.runner().run()
        self.assertEqual(self.executed, []); self.assertEqual(result['status'], 'approval_or_budget_required')
        self.approve(); self.assertEqual(self.runner().run()['status'], 'delivered_awaiting_merge')

    def test_w2_approval_is_exclusive_and_drift_blocks(self):
        with self.assertRaises(ValueError): queue.approve(self.path, self.approval, 'overwrite')
        self.fixture.contract.write_text(self.fixture.contract.read_text() + '\n')
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required'); self.assertFalse(self.executed)

    def test_w2_queue_edit_and_authority_policy_edit_require_new_approval(self):
        self.config['tasks'][0]['max_cycles'] = 4; save(self.path, self.config)
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required')
        self.approve(); (self.fixture.repo / 'AGENTS.md').write_text('Changed policy')
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required')

    def test_w2_dependency_order_and_separate_worktrees(self):
        self.second(); self.config['tasks'].reverse(); save(self.path, self.config); self.approve()
        self.assertEqual(self.runner().run()['status'], 'delivered_awaiting_merge')
        self.assertEqual(self.executed, ['first', 'second'])

    def test_w2_invalid_dag_duplicate_root_and_nonpositive_limits_reject(self):
        cases = []
        c = copy.deepcopy(self.config); c['tasks'][0]['depends_on'] = ['first']; cases.append(c)
        c = copy.deepcopy(self.config); c['tasks'][0]['depends_on'] = ['unknown']; cases.append(c)
        c = copy.deepcopy(self.config); c['tasks'].append(dict(c['tasks'][0], id='other')); cases.append(c)
        c = copy.deepcopy(self.config); c['limits']['window_seconds'] = True; cases.append(c)
        for config in cases:
            save(self.path, config)
            with self.assertRaises(ValueError): queue.model(self.path)

    def test_w2_pr_or_linked_budget_projects_reject(self):
        cfg = json.loads(self.fixture.project.read_text()); cfg['parent_budget'] = {'state_file': 'old'}; save(self.fixture.project, cfg)
        with self.assertRaises(ValueError): queue.model(self.path)
        cfg.pop('parent_budget'); cfg['delivery']['mode'] = 'pr'; save(self.fixture.project, cfg)
        with self.assertRaises(ValueError): queue.model(self.path)

    def test_w2_reservations_are_cumulative_and_not_refunded_on_early_success(self):
        self.second(); self.config['limits']['max_reserved_seconds'] = 500; save(self.path, self.config); self.approve()
        result = self.runner().run(); self.assertEqual(self.executed, ['first'])
        self.assertEqual(result['status'], 'approval_or_budget_required')
        restart = self.runner().run(); self.assertEqual(restart['deadline'], result['deadline']); self.assertEqual(self.executed, ['first'])

    def test_w2_project_cap_applies_across_tasks(self):
        self.second(); self.config['project_limits'][self.fixture.env['FIXTURE_REPO']]['max_tasks'] = 1
        save(self.path, self.config); self.approve()
        self.runner().run(); self.assertEqual(self.executed, ['first'])

    def test_w2_cycle_and_task_caps_stop_dispatch(self):
        self.second(); self.config['limits']['max_reserved_cycles'] = 3; save(self.path, self.config); self.approve()
        self.runner().run(); self.assertEqual(self.executed, ['first'])

    def test_w2_reserved_checkpoint_keeps_original_deadline_after_restart(self):
        runner = self.runner(); binding = runner.guard(); now = time.time()
        runner.initialize(binding); runner.state['deadline'] = now + 100
        job = runner.reserve(runner.tasks['first']); saved = dict(job['grant'])
        self.assertEqual(self.runner().run()['status'], 'delivered_awaiting_merge')
        self.assertEqual(self.runner().state['jobs']['first']['grant'], saved)

    def test_w2_crash_after_dispatch_never_reexecutes_missing_or_ambiguous_child(self):
        def crash(task, folder, grant): raise KeyboardInterrupt()
        runner = queue.Queue(self.path, self.approval, self.state, crash, self.fake_verify)
        with self.assertRaises(KeyboardInterrupt): runner.run()
        result = self.runner().run(); self.assertEqual(result['status'], 'decision_required'); self.assertFalse(self.executed)

    def test_w2_crash_after_child_success_reconciles_without_replay(self):
        def crash(task, folder, grant): self.fake_engine(task, folder, grant); raise KeyboardInterrupt()
        runner = queue.Queue(self.path, self.approval, self.state, crash, self.fake_verify)
        with self.assertRaises(KeyboardInterrupt): runner.run()
        result = self.runner().run(); self.assertEqual(result['status'], 'delivered_awaiting_merge'); self.assertEqual(self.executed, ['first'])

    def test_w2_failure_blocks_dependents_and_is_not_retried(self):
        self.second()
        def fail(*args): self.executed.append('first'); return {'status': 'ready_for_merge_approval'}
        result = queue.Queue(self.path, self.approval, self.state, fail, self.fake_verify).run()
        self.assertEqual(result['status'], 'decision_required'); self.runner().run(); self.assertEqual(self.executed, ['first'])

    def test_w2_clock_rollback_and_expired_window_cannot_renew(self):
        runner = self.runner(); runner.initialize(runner.guard()); runner.state['deadline'] = time.time()-1; runner.persist()
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required'); self.assertFalse(self.executed)
        runner.state['deadline'] = time.time()+100; runner.state['last_seen'] = time.time()+1000; runner.persist()
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required'); self.assertFalse(self.executed)

    def test_w2_mutated_delivered_receipt_blocks_restart(self):
        self.runner().run(); (self.state / 'tasks/first/synthetic.json').unlink()
        self.assertEqual(self.runner().run()['status'], 'decision_required'); self.assertEqual(self.executed, ['first'])

    def test_w2_real_receipt_rejects_forged_ready_status_and_remote_movement(self):
        result = queue.Queue(self.path, self.approval, self.state).run(); job = result['jobs']['first']; task = queue.model(self.path)[1]['first']
        folder = Path(job['folder']); state = json.loads((folder / 'state.json').read_text())
        original = copy.deepcopy(state)
        state['last_ci']['status'] = 'pending'; save(folder / 'state.json', state)
        with self.assertRaises(ValueError): queue.verify_delivery(task, folder, job['grant'])
        save(folder / 'state.json', original)
        self.fixture.cmd('git', '--git-dir', str(self.fixture.remote), 'update-ref', 'refs/heads/main', original['published_sha'])
        with self.assertRaises(ValueError): queue.verify_delivery(task, folder, job['grant'])

    def invoke(self, state):
        argv = ['approved_queue', 'run', '--queue', str(self.path), '--approval', str(self.approval), '--state-dir', str(state)]
        with patch.object(sys, 'argv', argv), patch.object(queue, 'w1_engine', self.fake_engine), patch.object(queue, 'verify_delivery', self.fake_verify), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            queue.main()

    def test_w2_cli_allocation_rejects_fanout_and_deleted_state(self):
        self.invoke(self.state)
        with self.assertRaises(SystemExit): self.invoke(self.base / 'other-state')
        (self.state / 'state.json').unlink()
        with self.assertRaises(SystemExit): self.invoke(self.state)
        self.assertEqual(self.executed, ['first'])

    def test_w2_cli_lock_rejects_concurrent_queue_dispatch(self):
        key = queue.hashlib.sha256(str(self.path.resolve()).encode()).hexdigest()
        folder = self.control / '.local/queue-locks'; folder.mkdir(parents=True)
        with queue.lock(folder / key):
            with self.assertRaises(SystemExit): self.invoke(self.state)
        self.assertFalse(self.executed)

    def test_w2_mutable_state_cannot_contain_approval_or_configuration(self):
        with self.assertRaises(ValueError): queue.Queue(self.path, self.approval, self.base)
        with self.assertRaises(ValueError): queue.approve(self.path, self.fixture.repo / 'approval.json', 'Synthetic test')

    def test_w2_existing_child_cannot_be_adopted_by_fresh_dispatch(self):
        runner = self.runner(); task = runner.tasks['first']; folder = self.state / 'tasks/first'; folder.mkdir(parents=True)
        with self.assertRaises(ValueError): queue.w1_engine(task, folder, {'seconds': 300, 'cycles': 3, 'deadline': time.time()+300})

    def test_w2_changed_reapproved_queue_cannot_execute_stale_loaded_tasks(self):
        runner = self.runner()
        self.config['tasks'][0]['id'] = 'replacement'; save(self.path, self.config); self.approve()
        self.assertEqual(runner.run()['status'], 'approval_or_budget_required')
        self.assertFalse(self.executed)

    def test_w2_started_state_without_binding_cannot_reset_allowance(self):
        self.state.mkdir(); save(self.state / 'state.json', {'status': 'running', 'jobs': {}, 'deadline': 1})
        with self.assertRaises(ValueError): self.runner()

    def test_w2_remote_probe_failure_during_reconciliation_is_actionable(self):
        self.runner().run()
        def unavailable(*args): raise queue.subprocess.TimeoutExpired('git', 30)
        result = queue.Queue(self.path, self.approval, self.state, self.fake_engine, unavailable).run()
        self.assertEqual(result['status'], 'decision_required')
        self.assertEqual(self.executed, ['first'])

    def test_w2_invalid_state_location_does_not_create_target_directories(self):
        path = self.fixture.repo / 'must-not-exist' / 'queue'
        with self.assertRaises(ValueError): queue.Queue(self.path, self.approval, path)
        self.assertFalse((self.fixture.repo / 'must-not-exist').exists())

    def test_w2_cli_empty_partial_or_replaced_state_never_renews_grant(self):
        self.invoke(self.state); original = json.loads((self.state / 'state.json').read_text())
        for bad in [[], {}, {'status': 'attention', 'handoff': {}}, dict(original, schema_version=99), dict(original, run_id='new-run'), dict(original, deadline=original['deadline']+1000)]:
            save(self.state / 'state.json', bad)
            with self.assertRaises(SystemExit): self.invoke(self.state)
        self.assertEqual(self.executed, ['first'])

    def test_w2_missing_allocation_receipt_cannot_reset_existing_state(self):
        self.invoke(self.state)
        key = queue.hashlib.sha256(str(self.path.resolve()).encode()).hexdigest()
        (self.control / '.local/queue-locks' / (key + '.json')).unlink()
        with self.assertRaises(SystemExit): self.invoke(self.state)
        self.assertEqual(self.executed, ['first'])

    def test_w2_clean_source_movement_after_approval_blocks_dispatch(self):
        self.fixture.cmd('git', 'commit', '--allow-empty', '-qm', 'Unapproved new baseline')
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required')
        self.assertFalse(self.executed)

    def test_w2_remote_base_movement_after_approval_blocks_dispatch(self):
        old = self.fixture.cmd('git', 'rev-parse', 'HEAD')
        self.fixture.cmd('git', 'commit', '--allow-empty', '-qm', 'other base')
        new = self.fixture.cmd('git', 'rev-parse', 'HEAD')
        self.fixture.cmd('git', 'push', '-q', 'origin', 'HEAD:main')
        self.fixture.cmd('git', 'reset', '--hard', old)
        self.assertNotEqual(old, new)
        self.assertEqual(self.runner().run()['status'], 'approval_or_budget_required')
        self.assertFalse(self.executed)

    def test_w2_locks_cover_engine_validation_dependencies_and_persistence(self):
        self.second()
        def assert_locked(task):
            with self.assertRaises(BlockingIOError):
                with queue.target_locks([task]): pass
        def engine(task, folder, grant):
            assert_locked(task); self.fake_engine(task, folder, grant)
        def verify(task, folder, grant):
            assert_locked(task); return self.fake_verify(task, folder, grant)
        result = queue.Queue(self.path, self.approval, self.state, engine, verify).run()
        self.assertEqual(result['status'], 'delivered_awaiting_merge')
        self.assertIn('Point-in-time', result['handoff']['freshness'])

    def test_w2_browser_result_harness_raw_dom_and_report_are_bound(self):
        result = queue.Queue(self.path, self.approval, self.state).run()
        self.assertEqual(result['status'], 'delivered_awaiting_merge')
        job = result['jobs']['first']; task = queue.model(self.path)[1]['first']; folder = Path(job['folder'])
        child = json.loads((folder / 'state.json').read_text()); attempt = Path(child['attempts'][-1]['folder'])
        cases = [('browser-binding.json', '{"target_digest":"' + child['accepted_digest'] + '"}'),
                 ('browser-result.json', '{"status":"PASS","forged":true}'),
                 ('browser-dom.log', '<pre id="results">{"status":"PASS"}</pre>'),
                 ('browser/index.html', 'Modified harness')]
        for filename, bad in cases:
            path = attempt / filename; original = path.read_text(); path.write_text(bad)
            with self.assertRaises((ValueError, KeyError)): queue.verify_delivery(task, folder, job['grant'])
            path.write_text(original)
        (attempt / 'browser-dom-execution.json').unlink()
        with self.assertRaises(OSError): queue.verify_delivery(task, folder, job['grant'])


if __name__ == '__main__': unittest.main()
