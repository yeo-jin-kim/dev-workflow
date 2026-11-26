"""Real local Git merges, HTTP boundaries and revision-bound regression behavior."""
import copy
import http.client
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import delivery_handoff as h
import handoff_server as web


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve();self.local=self.root/'.local';self.local.mkdir()
        subprocess.run(['git','init',str(self.root)],check=True,capture_output=True)
        (self.root/'.gitignore').write_text('.local/\ntarget/\nremote.git/\n')
        p=patch.object(h,'ROOT',self.root);p.start();self.addCleanup(p.stop)
        self.remote=self.root/'remote.git';self.repo=self.root/'target'
        subprocess.run(['git','init','--bare',str(self.remote)],check=True,capture_output=True)
        subprocess.run(['git','init','-b','base',str(self.repo)],check=True,capture_output=True)
        h.git(self.repo,'config','user.email','test@example.invalid');h.git(self.repo,'config','user.name','Test')
        (self.repo/'code').write_text('before');h.git(self.repo,'add','.');h.git(self.repo,'commit','-m','base')
        base=h.git(self.repo,'rev-parse','HEAD');h.git(self.repo,'remote','add','origin',str(self.remote));h.git(self.repo,'push','origin','base')
        h.git(self.repo,'switch','-c','candidate');(self.repo/'code').write_text('after');h.git(self.repo,'commit','-am','candidate');head=h.git(self.repo,'rev-parse','HEAD');h.git(self.repo,'push','origin','candidate');h.git(self.repo,'switch','base')
        self.report={'status':'ready_for_merge_approval','source_sha':head,'target_sha':base,'source_branch':'candidate','target_branch':'base','repository':h.repository_identity(str(self.remote)),'reviewed_digest':'contents','review':{'verdict':'pass','blocking_findings':[],'decision_requests':[],'criteria':[{'id':'test','passed':True},{'id':'documentation_sync','passed':True}]},'ci':{'status':'success','head':head,'base':base}}
        self.report['ci']['gates']=[{'gate':{'workflow':'synthetic-test'},'passed':True}]
        identity={'status':self.report['status'],'head':head,'base':base,'contents':'contents','review':self.report['review'],'ci':self.report['ci']}
        self.report.update(identity=identity,report_id=__import__('hashlib').sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest())
        self.report['identity']['run_id']='synthetic-run'
        self.record={'request':{'query':'who','options':{}},'context':{'snapshotSha256':'snapshot','graphContentSha256':'graph'},'response':{'answer':{'summary':'before','claims':[]},'retrieval':{'graphSequence':1}},'review':{'reason':'missing owner'}}
        self.observed={'replayed_request':self.record['request'],'snapshot_sha256':'snapshot','graph_content_sha256':'graph','target_digest':'contents','schema_version':1,'response':{'request':{'query':'who'},'retrieval':{'graphSequence':1},'trace':{'activationScores':{},'activationPaths':{},'synthetic':True},'answer':{'summary':'after','claims':[{'claimId':'claim:owner','text':'Owner'}]},'graph':{'states':[],'relations':[]}}}
        run=self.local/'delivery';attempt=run/'attempt-001';attempt.mkdir(parents=True);(run/'reports').mkdir()
        self.report_path=run/'reports/report.json';self.review_path=self.local/'review.json';self.observation_path=self.local/'observation.json';self.folder=self.local/'handoffs'
        check={'exit_code':0,'input_digest':'contents'}
        h.save(attempt/'check-0-execution.json',check);h.save(attempt/'review.json',self.report['review'])
        self.report['report_id']=__import__('hashlib').sha256(json.dumps(self.report['identity'],sort_keys=True).encode()).hexdigest()
        self.report['verification']=[{'evidence_directory':str(attempt),'checks':[check]}]
        (self.root/'projects').mkdir();(self.root/'contracts').mkdir()
        project=self.root/'projects/task.json';contract=self.root/'contracts/task.json'
        h.save(project,{'schema_version':2,'root':str(self.repo),'contract':str(contract),'delivery':{'head':'candidate','base':'base','repository':self.report['repository'],'required_gates':[{'workflow':'synthetic-test'}]}})
        h.save(contract,{'checks':[['synthetic-check']],'criteria':[{'id':'test'}]})
        from delivery_evidence import manifest,fingerprint
        controls={'controller':manifest(self.root)['digest'],'protected':fingerprint([project,contract])}
        h.save(run/'state.json',{'controls':controls,'target':str(self.repo),'report':str(self.report_path),'status':'ready_for_merge_approval','run_id':'synthetic-run','published_sha':head,'base_sha':base,'accepted_digest':'contents','last_review':self.report['review'],'last_ci':self.report['ci']})
        for p,d in [(self.report_path,self.report),(self.review_path,self.record),(self.observation_path,self.observed)]:h.save(p,d)
        self.observed['selected_review_sha256']=__import__('hashlib').sha256(self.review_path.read_bytes()).hexdigest();h.save(self.observation_path,self.observed)
        self.packet=h.register(self.report_path,self.review_path,self.observation_path,self.folder)
    def merge(self,checks):
        approval=h.authorize(self.packet,self.repo,'Explicit synthetic fixture owner approval',checks)
        return h.merge(self.packet,self.repo,approval)
    def accept(self):h.retest(self.packet,'pass','Verified original question and owner evidence.')
    def test_registration_is_immutable_and_rejects_stale_evidence(self):
        self.assertEqual(self.packet,h.register(self.report_path,self.review_path,self.observation_path,self.folder))
        self.observed['response']['answer']['summary']='changed';h.save(self.observation_path,self.observed)
        with self.assertRaisesRegex(ValueError,'evidence changed'):h.retest(self.packet,'pass','test')
    def test_failed_ci_and_mismatched_replay_cannot_register(self):
        for mutate in [lambda:self.report['ci'].update(head='wrong'),lambda:self.report['review'].update(blocking_findings=['block']),lambda:self.observed.update(graph_content_sha256='other')]:
            mutate();h.save(self.report_path,self.report);h.save(self.observation_path,self.observed)
            with self.assertRaises(ValueError):h.register(self.report_path,self.review_path,self.observation_path,self.folder)
    def test_missing_trace_or_wrong_selected_record_cannot_register(self):
        for field in ['trace','request']:
            damaged=copy.deepcopy(self.observed);damaged['response'].pop(field);h.save(self.observation_path,damaged)
            with self.assertRaises(ValueError):h.register(self.report_path,self.review_path,self.observation_path,self.folder)
        damaged=copy.deepcopy(self.observed);damaged['selected_review_sha256']='wrong';h.save(self.observation_path,damaged)
        with self.assertRaises(ValueError):h.register(self.report_path,self.review_path,self.observation_path,self.folder)
    def test_historical_import_cannot_gain_acceptance_or_merge_authority(self):
        state=self.report_path.parent.parent/'state.json';data=h.read(state);data['status']='old';h.save(state,data)
        with self.assertRaises(ValueError):h.register(self.report_path,self.review_path,self.observation_path,self.folder)
        history=h.register(self.report_path,self.review_path,self.observation_path,self.local/'history',historical_only=True)
        with self.assertRaisesRegex(ValueError,'Historical'):h.retest(history,'pass','not allowed')
        with self.assertRaisesRegex(ValueError,'Historical'):h.authorize(history,self.repo,'not allowed',[[sys.executable,'-c','pass']])
    def test_owner_approval_is_bound_to_exact_revision(self):
        self.accept();approval=h.authorize(self.packet,self.repo,'Explicit fixture owner decision',[[sys.executable,'-c','pass']])
        value=h.read(approval);value['source_sha']='0'*40;h.save(approval,value)
        with self.assertRaisesRegex(ValueError,'different revision'):h.merge(self.packet,self.repo,approval)

    def test_actual_merge_checks_and_push_are_exact_revision_bound(self):
        self.accept();result=self.merge([[sys.executable,'-c',"from pathlib import Path; assert Path('code').read_text()=='after'"]])
        self.assertEqual(result['status'],'merged_and_pushed');self.assertEqual(h.remote(self.repo,'base'),result['merged_sha'])
        self.assertEqual(h.git(self.repo,'rev-parse','HEAD^{tree}'),h.git(self.repo,'rev-parse','candidate^{tree}'))
        with self.assertRaisesRegex(ValueError,'already attempted'):h.merge(self.packet,self.repo,self.root/'projects/.local/merge-approvals'/(self.packet.stem+'.json'))
    def test_failed_postmerge_checks_never_push(self):
        self.accept();before=h.remote(self.repo,'base')
        with self.assertRaisesRegex(ValueError,'check failed'):self.merge([[sys.executable,'-c','raise SystemExit(1)']])
        self.assertEqual(h.remote(self.repo,'base'),before);self.assertEqual(h.read(self.packet.with_suffix('.merge.json'))['status'],'decision_required')
    def test_moved_source_and_nonpassing_human_test_block_merge(self):
        with self.assertRaises(OSError):self.merge([[sys.executable,'-c','pass']])
        h.retest(self.packet,'changes_requested','Still wrong')
        with self.assertRaisesRegex(ValueError,'Passing human'):self.merge([[sys.executable,'-c','pass']])
        self.accept();h.git(self.repo,'switch','candidate');(self.repo/'code').write_text('moved');h.git(self.repo,'commit','-am','moved');h.git(self.repo,'push','origin','candidate');h.git(self.repo,'switch','base')
        with self.assertRaisesRegex(ValueError,'moved'):self.merge([[sys.executable,'-c','pass']])
    def test_private_case_preservation_and_future_failure(self):
        self.accept();case=h.preserve_case(self.packet,['claim:owner'],['claim:platform'])
        self.assertEqual(h.check_registry(self.observed,self.folder)[0]['status'],'passed')
        broken=copy.deepcopy(self.observed);broken['response']['answer']['claims']=[]
        with self.assertRaisesRegex(ValueError,'assertions failed'):h.check_registry(broken,self.folder)
        other=copy.deepcopy(self.observed);other['replayed_request']={'query':'other'}
        self.assertEqual(h.check_registry(other,self.folder)[0]['status'],'not_applicable')
        self.assertEqual(h.read(case)['required_claims'],['claim:owner'])
    def test_fresh_regression_executes_trusted_replay(self):
        from delivery_evidence import manifest
        self.accept();case=h.preserve_case(self.packet,['claim:owner'],[])
        observed={**self.observed,'target_digest':manifest(self.repo)['digest']}
        command=[sys.executable,'-c',"import pathlib,json,sys,hashlib;d=json.loads(sys.argv[3]);d['selected_review_sha256']=hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest();pathlib.Path(sys.argv[2],'review-replay.json').write_text(json.dumps(d))",'{review}','{output}',json.dumps(observed)]
        head=h.git(self.repo,'rev-parse','HEAD')
        result=h.run_case(case,self.repo,command,self.local/'regression',expected_head=head)
        self.assertEqual(result['status'],'passed')
        with self.assertRaisesRegex(ValueError,'fresh'):h.run_case(case,self.repo,command,self.local/'regression',expected_head=head)
        with self.assertRaisesRegex(ValueError,'source revision'):h.run_case(case,self.repo,command,self.local/'wrong-source',expected_head='0'*40)
    def test_regression_rejects_symlinked_reused_observation(self):
        self.accept();case=h.preserve_case(self.packet,['claim:owner'],[])
        command=[sys.executable,'-c',"import pathlib,sys;pathlib.Path(sys.argv[2],'review-replay.json').symlink_to(sys.argv[3])",'{review}','{output}',str(self.observation_path)]
        with self.assertRaisesRegex(ValueError,'fresh regular'):
            h.run_case(case,self.repo,command,self.local/'symlink-run',expected_head=h.git(self.repo,'rev-parse','HEAD'))

    def test_console_reads_live_worker_phase_without_resuming_it(self):
        import review_intake as ri
        queue=self.local/'queue';queue.mkdir();run=self.local/'run';run.mkdir()
        state=self.local/'worker/tasks/repair/state.json';state.parent.mkdir(parents=True)
        journal=self.local/'journal.json';h.save(journal,{'state_dir':str(self.local/'worker')})
        h.save(state,{'status':'reviewing'})
        h.save(run/'receipt.json',{'phase':'prepared','id':'a'*64})
        h.save(queue/('b'*64+'.json'),{'id':'b'*64,'status':'running','run':str(run),'answer_policy':'trusted','notes':{'reviewRecord':self.record}})
        with patch.object(ri,'locations',return_value=(self.local,journal)):
            self.assertEqual(web.queued_items(queue)[0]['status'],'reviewing')
        self.assertEqual(h.read(state)['status'],'reviewing')

    def test_http_notes_require_session_and_cannot_merge(self):
        server=web.make_server(self.folder,queue=self.local/'queue');self.addCleanup(server.server_close)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();self.addCleanup(server.shutdown)
        port=server.server_port
        def request(method,path,data=None,headers=None):
            c=http.client.HTTPConnection('127.0.0.1',port);body=json.dumps(data) if data is not None else None
            hs={'Host':f'127.0.0.1:{port}','Origin':f'http://127.0.0.1:{port}','Content-Type':'application/json',**(headers or {})}
            c.request(method,path,body,hs);r=c.getresponse();content=r.read();c.close();return r.status,content
        status,raw=request('GET','/api/session');self.assertEqual(status,200);token=json.loads(raw)['token'];headers={'X-Review-Token':token}
        self.assertEqual(request('GET','/api/items')[0],403)
        self.assertEqual(request('GET','/api/items',headers=headers)[0],200)
        endpoint='/api/items/'+self.packet.stem
        self.assertEqual(request('POST',endpoint+'/retest',{'decision':'pass','reason':'tested'},headers)[0],200)
        self.assertEqual(request('POST',endpoint+'/merge',{},headers)[0],409)
        self.assertEqual(request('POST',endpoint+'/retest',{'decision':'pass','reason':'test'},{**headers,'Origin':'https://evil.test'})[0],403)
        self.assertEqual(request('GET','/api/session',headers={'Host':'evil.test'})[0],403)
        status,raw=request('GET',endpoint,headers=headers);self.assertEqual(json.loads(raw)['status'],'awaiting_owner_merge_authorization')


if __name__=='__main__':unittest.main()
