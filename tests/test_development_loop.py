import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('development_loop', Path(__file__).resolve().parents[1] / 'tools/development_loop.py')
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class DevelopmentLoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'target'
        self.root.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        (self.root / '.gitignore').write_text('.local/\n')
        (self.root / 'workflow').mkdir()
        (self.root / 'tools').mkdir()
        (self.root / 'AGENTS.md').write_text('policy')
        self.contract = Path(self.tmp.name) / 'task.json'
        self.contract.write_text(json.dumps({'criteria': [{'id': 'a'}], 'checks': [['check']]}))
        self.state_dir = Path(self.tmp.name) / 'run'
        self.review = {'verdict': 'pass', 'blocking_findings': [], 'decision_requests': [],
                       'criteria': [{'id': 'a', 'passed': True, 'evidence': 'checked source and logs'},
                                    {'id': 'documentation_sync', 'passed': True, 'evidence': 'fixture-only task; no runtime or design change'}]}

    def fake(self, argv, root, log, timeout, prompt=None):
        log.write_text('executed')
        if argv[0] == 'check':
            return self.check_exit
        self.assertEqual(root, self.root.resolve())
        schema = Path(argv[argv.index('--output-schema') + 1])
        self.assertEqual(schema.parent, loop.ROOT / 'schemas')
        self.assertFalse(schema.is_relative_to(root))
        target = Path(argv[argv.index('-o') + 1])
        if target.name == 'review.json':
            if self.mutate_review:
                (root / 'late.py').write_text('changed')
            target.write_text(json.dumps(self.review))
        else:
            target.write_text(json.dumps({'summary': 'done', 'decision_requests': self.decisions}))
        return 0

    def go(self):
        self.check_exit = getattr(self, 'check_exit', 0)
        self.decisions = getattr(self, 'decisions', [])
        self.mutate_review = getattr(self, 'mutate_review', False)
        with patch.object(loop, 'execute', side_effect=self.fake):
            loop.run(self.root, self.contract, self.state_dir, 'codex', 1, 30)
        return json.loads((self.state_dir / 'state.json').read_text())['status']

    def test_documentation_criterion_is_always_added(self):
        original = {'criteria': [{'id': 'a'}]}
        result = loop.effective_contract(original)
        self.assertEqual([x['id'] for x in result['criteria']], ['a', 'documentation_sync'])
        self.assertEqual(original['criteria'], [{'id': 'a'}])
        with self.assertRaises(ValueError):
            loop.effective_contract({'criteria': [{'id': 'documentation_sync'}]})

    def test_missing_documentation_review_blocks_completion(self):
        self.review['criteria'] = self.review['criteria'][:1]
        self.assertEqual(self.go(), 'cycle_limit')

    def test_failed_documentation_review_blocks_completion(self):
        self.review['criteria'][1]['passed'] = False
        self.assertEqual(self.go(), 'cycle_limit')

    def test_logs_and_schemas_are_external_to_target(self):
        self.assertEqual(self.go(), 'complete')
        self.assertFalse((self.root / '.local/run').exists())
        self.assertTrue((self.state_dir / 'attempt-001/implementation.log').exists())

    def test_state_inside_target_is_rejected(self):
        self.state_dir = self.root / '.local/run'
        with self.assertRaises(ValueError):
            self.go()

    def test_controller_cannot_be_target(self):
        with self.assertRaises(ValueError):
            loop.run(loop.ROOT, self.contract, self.state_dir, 'codex', 1, 30)

    def test_complete(self):
        self.assertEqual(self.go(), 'complete')

    def test_failed_check_blocks_completion(self):
        self.check_exit = 1
        self.assertEqual(self.go(), 'cycle_limit')

    def test_missing_criterion_blocks_completion(self):
        self.review['criteria'] = []
        self.assertEqual(self.go(), 'cycle_limit')

    def test_decision_blocks_restart(self):
        self.decisions = ['Choose authority']
        self.assertEqual(self.go(), 'decision_required')
        with self.assertRaises(ValueError):
            self.go()

    def test_source_change_invalidates_review(self):
        self.mutate_review = True
        self.assertEqual(self.go(), 'tree_changed_during_review')

    def test_blocking_finding_blocks_completion(self):
        self.review['blocking_findings'] = ['scope drift']
        self.assertEqual(self.go(), 'cycle_limit')

    def test_policy_change_blocks_restart(self):
        self.go()
        self.contract.write_text(self.contract.read_text() + '\n')
        with self.assertRaises(ValueError):
            self.go()

    def test_exclusive_lock(self):
        self.state_dir.mkdir(parents=True)
        with loop.lock(self.state_dir / 'lock'):
            with self.assertRaises(BlockingIOError):
                with loop.lock(self.state_dir / 'lock'):
                    pass

    def test_deleted_and_untracked_source_change_digest(self):
        path = self.root / 'sample.py'
        path.write_text('first')
        first = loop.digest(self.root)
        path.write_text('second')
        self.assertNotEqual(first, loop.digest(self.root))
        subprocess.run(['git', 'add', 'sample.py'], cwd=self.root, check=True)
        before = loop.digest(self.root)
        path.unlink()
        self.assertNotEqual(before, loop.digest(self.root))


if __name__ == '__main__':
    unittest.main()
