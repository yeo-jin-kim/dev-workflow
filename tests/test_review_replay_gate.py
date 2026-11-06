"""Replay observation binding tests; no private source or actual model calls."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import review_replay_gate as gate


class ReplayGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name);self.target=self.base/'target';self.target.mkdir()
        subprocess.run(['git','init','-q',str(self.target)],check=True)
        (self.target/'task.txt').write_text('baseline')
        self.review=self.base/'selected.json'
        self.record={'context':{'snapshotSha256':'a'*64},'request':{'query':'Who participated?','options':{'llmAnswer':False}},'response':{'retrieval':{'graphSequence':7}}}
        self.review.write_text(json.dumps(self.record))
        self.output=self.base/'evidence';self.output.mkdir()
        self.observation={'schema_version':1,'selected_review_sha256':hashlib.sha256(self.review.read_bytes()).hexdigest(),'target_digest':gate.manifest(self.target)['digest'],'snapshot_sha256':'a'*64,'replayed_request':copy.deepcopy(self.record['request']),
                          'response':{'request':{'query':'Who participated?'},'answer':{'summary':'Synthetic observation'},'trace':{'activationScores':{},'activationPaths':{}},'retrieval':{'graphSequence':7}}}

    def invoke(self, value=None, mutate=False):
        data=json.dumps(self.observation if value is None else value)
        script='import sys; from pathlib import Path; Path(sys.argv[1]).write_text(sys.argv[2])'
        if mutate:script+='; Path("task.txt").write_text("mutated")'
        return gate.replay(self.target,self.review,self.output,[sys.executable,'-c',script,str(self.output/'review-replay.json'),data])

    def test_bound_observation_is_not_a_semantic_pass(self):
        self.assertEqual(self.invoke()['response']['answer']['summary'],'Synthetic observation')

    def test_zero_exit_without_fresh_evidence_is_rejected(self):
        with self.assertRaises(ValueError):gate.replay(self.target,self.review,self.output,[sys.executable,'-c','pass'])

    def test_old_artifact_is_not_adopted(self):
        (self.output/'review-replay.json').write_text(json.dumps(self.observation))
        with patch.object(gate.subprocess,'run') as command:
            with self.assertRaises(ValueError):self.invoke()
            command.assert_not_called()

    def test_wrong_source_review_or_data_binding_is_rejected(self):
        for field in ('selected_review_sha256','target_digest','snapshot_sha256'):
            with self.subTest(field=field):
                obs=copy.deepcopy(self.observation);obs[field]='0'*64
                with self.assertRaises(ValueError):self.invoke(obs)
                (self.output/'review-replay.json').unlink()

    def test_changed_graph_or_question_or_settings_is_rejected(self):
        for field in ('graph','question','settings'):
            with self.subTest(field=field):
                obs=copy.deepcopy(self.observation)
                if field=='graph':obs['response']['retrieval']['graphSequence']=8
                elif field=='question':obs['response']['request']['query']='Unrelated question'
                else:obs['replayed_request']['options']['llmAnswer']=True
                with self.assertRaises(ValueError):self.invoke(obs)
                (self.output/'review-replay.json').unlink()

    def test_replay_cannot_mutate_tested_source(self):
        with self.assertRaises(ValueError):self.invoke(mutate=True)

    def test_missing_activation_trace_is_rejected(self):
        obs=copy.deepcopy(self.observation);obs['response']['trace']={'unrelated':True}
        with self.assertRaises(ValueError):self.invoke(obs)


if __name__=='__main__':unittest.main()
