"""Real HTTP security boundaries and durable queue transitions; synthetic executor."""
import hashlib
import http.client
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import quality_intake as m
import quality_workflow as q

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve();(self.root/'projects').mkdir();(self.root/'contracts').mkdir()
        self.target=self.root.parent/(self.root.name+'-target');self.target.mkdir();self.addCleanup(lambda:__import__('shutil').rmtree(self.target))
        self.snapshot=self.target/'snapshot';self.snapshot.write_text('source')
        self.folder=self.root/'.local/review';(self.folder/'trial').mkdir(parents=True)
        self.plan={'node_id':'node','snapshot_sha256':hashlib.sha256(b'source').hexdigest(),'binding':{'graph_digest':'graph','graph_sequence':1},'blockers':['missing source']};self.plan['plan_digest']=m.plan_hash(self.plan)
        q.save(self.folder/'trial/plan.json',self.plan);(self.folder/'trial/index.html').write_text('<h1>Review</h1><input id="plan"><select id="decision"></select><textarea id="reason"></textarea>')
        q.save(self.root/'contracts/removal.json',{'repair_mode':'remove_mixed_preserve_unresolved','production_apply_authorized':False})
        self.cfg={'target':str(self.target),'snapshot':str(self.snapshot),'graph':'graph','node_id':'node','enabled':True,'authorization_reference':'owner fixture','total_seconds':60,'commands':{'audit':['audit','{run}'],'trial':['trial','--repair-mode','remove_mixed_preserve_unresolved','--expected-review','{run}/review-binding.json'],'compare':['compare']},'intake':{'enabled':True,'contract':'contracts/removal.json','repair_mode':'remove_mixed_preserve_unresolved'}}
        self.policy=self.root/'projects/p.json';q.save(self.policy,self.cfg)
        self.addCleanup(patch.stopall);patch.object(q,'ROOT',self.root).start();self.manifest=patch.object(m,'manifest',return_value={'digest':'source-code'}).start()
        self.audit_binding=dict(self.plan['binding'])
        def audit(argv,cwd,log,timeout):q.save(Path(argv[1])/'audit.json',{'binding':self.audit_binding});return 0
        patch.object(m,'execute',side_effect=audit).start()
        self.intake=m.Intake(self.folder,self.policy);self.server=m.make_server(self.intake,0)
        self.addCleanup(self.server.server_close);threading.Thread(target=self.server.serve_forever,daemon=True).start();self.addCleanup(self.server.shutdown)
        self.origin='http://127.0.0.1:'+str(self.server.server_port)
        self.notes={'schemaVersion':1,'planDigest':self.plan['plan_digest'],'decision':'changes_requested','reason':'Remove mixed node; preserve all evidence. $(untrusted)'}

    def http(self,method,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        h={'Origin':self.origin,'Content-Type':'application/json','X-Review-Token':self.intake.token};h.update(headers or {})
        c.request(method,path,json.dumps(body).encode() if body is not None else None,h);r=c.getresponse();data=r.read();c.close()
        try:data=json.loads(data)
        except ValueError:pass
        return r.status,data

    def test_http_accepts_once_and_dispatches_only_fixed_policy_with_notes_as_data(self):
        status,r=self.http('POST','/api/requests',{**self.notes,'command':['UNTRUSTED'],'total_seconds':999999});self.assertEqual(status,202)
        again,same=self.http('POST','/api/requests',{**self.notes,'reason':'Different notes cannot refill budget'})
        self.assertEqual(again,200);self.assertEqual(same['id'],r['id'])
        before=self.intake.get(r['id'])
        with patch.object(q,'run',return_value={'status':'awaiting_owner_review'}) as runner:
            result=self.intake.process(r['id']);self.intake.process(r['id'])
        self.assertEqual(runner.call_count,1);args,kwargs=runner.call_args
        self.assertEqual(args[0],self.policy);self.assertEqual(kwargs['deadline_limit'],before['deadline'])
        self.assertEqual(kwargs['expected_binding'],self.plan['binding'])
        self.assertEqual(kwargs['issue_evidence']['reason'],self.notes['reason'])
        self.assertEqual(result['status'],'awaiting_owner_review');self.assertFalse(result['production_apply_authorized'])
        self.assertEqual(self.http('GET','/api/requests/'+r['id'])[0],200)

    def test_csrf_and_rebinding_cannot_enqueue(self):
        for headers in [{'Origin':'https://evil.test'},{'Host':'evil.test'},{'X-Review-Token':'wrong'},{'Sec-Fetch-Site':'cross-site'}]:
            with self.subTest(headers=headers):self.assertEqual(self.http('POST','/api/requests',self.notes,headers)[0],403)
        self.assertFalse(list(self.intake.queue.glob('*.json')))
        self.assertEqual(self.http('GET','/api/session',headers={'Host':'evil.test'})[0],403)

    def test_stale_plan_graph_snapshot_and_policy_are_rejected(self):
        self.assertEqual(self.http('POST','/api/requests',{**self.notes,'planDigest':'wrong'})[0],409)
        self.audit_binding={'graph_digest':'changed','graph_sequence':2}
        self.assertEqual(self.http('POST','/api/requests',self.notes)[0],409)
        self.audit_binding=self.plan['binding'];self.snapshot.write_text('changed')
        self.assertEqual(self.http('POST','/api/requests',self.notes)[0],409)
        self.assertFalse(list(self.intake.queue.glob('*.json')))

    def test_approval_and_oversized_requests_cannot_start_work(self):
        self.assertEqual(self.http('POST','/api/requests',{**self.notes,'decision':'approve_proposal'})[0],409)
        self.assertEqual(self.http('POST','/api/requests',{**self.notes,'reason':'x'*40000})[0],409)
        self.assertEqual(self.http('POST','/api/requests',self.notes,{'Content-Type':'text/plain'})[0],409)

    def test_restart_does_not_resume_running_or_refill_expired_request(self):
        r,_=self.intake.accept(self.notes);path=self.intake.queue/(r['id']+'.json');r.update(status='running');q.save(path,r)
        self.intake.recover();self.assertEqual(self.intake.get(r['id'])['status'],'decision_required')
        r.update(status='queued',deadline=time.time()-1);q.save(path,r)
        with patch.object(q,'run') as runner:result=self.intake.process(r['id'])
        runner.assert_not_called();self.assertEqual(result['status'],'decision_required')

    def test_artifact_allowlist_hides_databases_and_other_requests(self):
        r,_=self.intake.accept(self.notes);out=self.intake.queue/r['id'];(out/'trial').mkdir(parents=True);(out/'trial/candidate.db').write_bytes(b'private')
        for path in ['/candidate.db','/trial/candidate.db','/results/'+r['id']+'/candidate.db','/api/requests/../x']:
            with self.subTest(path=path):self.assertEqual(self.http('GET',path)[0],404)
        self.assertNotIn(b'send-repair',self.http('GET','/')[1])

    def test_queued_restart_preserves_deadline_and_runs_once(self):
        r,_=self.intake.accept(self.notes);restarted=m.Intake(self.folder,self.policy)
        with patch.object(q,'run',return_value={'status':'awaiting_owner_review'}) as runner:
            restarted.process(r['id']);restarted.process(r['id'])
        self.assertEqual(runner.call_count,1)
        self.assertEqual(runner.call_args.kwargs['deadline_limit'],r['deadline'])

    def test_changed_contract_does_not_authorize_old_queued_request(self):
        r,_=self.intake.accept(self.notes)
        path=self.root/'contracts/removal.json';contract=q.read(path);contract['version']=2;q.save(path,contract)
        restarted=m.Intake(self.folder,self.policy)
        with patch.object(q,'run') as runner:result=restarted.process(r['id'])
        runner.assert_not_called();self.assertEqual(result['status'],'decision_required')

    def test_policy_cannot_exceed_fixed_contract_deadline(self):
        path=self.root/'contracts/removal.json';contract=q.read(path);contract['limits']={'total_seconds_max':1};q.save(path,contract)
        with self.assertRaisesRegex(ValueError,'deadline'):m.Intake(self.folder,self.policy)

    def completed_record(self):
        return {'id':'review-1','context':{'snapshotSha256':self.plan['snapshot_sha256'],'graphSequence':1},'request':{'query':'Who worked on the paper?'},'response':{'retrieval':{'graphSequence':1},'answer':{'summary':'Recorded actual response'}},'review':{'decision':'changes_requested','reason':self.notes['reason'],'issues':['unsupported']}}

    def test_answer_feedback_is_recorded_for_scope_decision_without_running_removal(self):
        status,r=self.http('POST','/api/requests',{**self.notes,'repairScope':'recall_answer','reviewRecord':self.completed_record()})
        self.assertEqual(status,202);record=self.intake.get(r['id'])
        self.assertEqual(record['status'],'decision_required')
        _,state=self.http('GET','/api/requests/'+r['id']);status,receipt=self.http('GET',state['resultUrl'])
        self.assertEqual(status,200);self.assertIn(b'Who worked on the paper?',receipt);self.assertIn(b'Recorded actual response',receipt)
        with patch.object(q,'run') as runner:self.intake.process(r['id'])
        runner.assert_not_called();self.assertEqual(record['notes']['reviewRecord']['response']['answer']['summary'],'Recorded actual response')

    def test_stale_recall_response_cannot_start_a_repair(self):
        record=self.completed_record();record['response']['retrieval']['graphSequence']=2
        self.assertEqual(self.http('POST','/api/requests',{**self.notes,'repairScope':'mixed_node','reviewRecord':record})[0],409)
