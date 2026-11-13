"""Real temporary Git/queue boundaries; synthetic workers and remote CI."""
import os
import sys
import json
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import test_delivery_loop as fixture
from delivery_evidence import environment_identity


class EnvironmentTests(unittest.TestCase):
    def test_transport_changes_do_not_invalidate_but_runtime_settings_do(self):
        first=environment_identity()
        with patch.dict(os.environ,{'CODEX_TOOL_CALL_ID':'new-call','_':'different','SHLVL':'999'}):
            self.assertEqual(first,environment_identity())
        for key in ['PATH','PYTHONPATH','CORA_PROVIDER','CODEX_PERMISSION_PROFILE','UNKNOWN_DEPENDENCY','SECURITYSESSIONID','XPC_FLAGS','CODEX_APP_TOOLS_PIPE_PATH']:
            with self.subTest(key=key),patch.dict(os.environ,{key:'different-runtime-value'}):
                self.assertNotEqual(first,environment_identity())

    def setup_fixture(self):
        f=fixture.DeliveryTests();f.setUp();self.addCleanup(f.doCleanups);return f

    def test_ci_exists_before_semantic_review_and_owner_merge_stays_pending(self):
        f=self.setup_fixture();os.environ['FIXTURE_FAULT']='ci_before_review'
        state=f.delivery().run()
        self.assertEqual(state['status'],'ready_for_merge_approval')
        self.assertEqual(state['last_ci']['status'],'success')
        self.assertEqual(f.cmd('git','rev-parse','main').strip(),state['baseline_head'])

    def test_runtime_change_revalidates_without_worker_or_budget_refill(self):
        f=self.setup_fixture();old=f.delivery().run();deadline=old['budget']['deadline'];cycles=old['budget']['cycles']
        with patch.dict(os.environ,{'CORA_PROVIDER':'new-provider'}):new=f.delivery().run()
        self.assertEqual(new['status'],'ready_for_merge_approval')
        self.assertEqual(new['budget']['deadline'],deadline)
        self.assertEqual(new['budget']['cycles'],cycles)
        self.assertEqual((f.fixture_state/'workers').read_text(),'1')
        self.assertTrue(new['environment_invalidations'])
        self.assertTrue(list((f.base/'run').glob('revalidation-*')))

    def test_transport_restart_reuses_current_verified_revision(self):
        f=self.setup_fixture();old=f.delivery().run()
        with patch.dict(os.environ,{'CODEX_TOOL_CALL_ID':'restart'}):new=f.delivery().run()
        self.assertEqual(new['status'],'ready_for_merge_approval')
        self.assertEqual(new['budget']['deadline'],old['budget']['deadline'])
        self.assertEqual(new['budget']['cycles'],old['budget']['cycles'])
        self.assertEqual((f.fixture_state/'workers').read_text(),'1')
