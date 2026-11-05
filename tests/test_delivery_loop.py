"""W1 fault rehearsals. Fake model/GitHub outputs are explicitly synthetic.

Real Git commits/pushes use temporary bare remotes. Real Chrome is exercised
separately when installed. The real CoRA pilot is not replaced by these tests.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
from delivery_loop import Delivery, decision_packet, recoverable_review_timeout
from delivery_evidence import Budget, Halt, Recorder, browser_run, git, manifest, fingerprint
from development_loop import save

FAKE = r'''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
a=sys.argv[1:];root=Path(os.environ['FIXTURE_TARGET']);fault=os.environ.get('FIXTURE_FAULT','');state=Path(os.environ['FIXTURE_STATE']);state.mkdir(exist_ok=True)
if Path(sys.argv[0]).name=='codex':
 if '--version' in a: print('synthetic-codex');sys.exit(0)
 prompt=sys.stdin.read();out=Path(a[a.index('-o')+1]);schema=Path(a[a.index('--output-schema')+1]).name
 if schema=='implementation.schema.json':
  count=int((state/'workers').read_text())+1 if (state/'workers').exists() else 1;(state/'workers').write_text(str(count))
  value='good-'+str(count)
  if count==1 and fault=='check_repair':value='bad'
  if count==1 and fault=='review_repair':value='plausible'
  if count>1 and fault=='browser_repair' and 'project_observations' not in prompt:value='bad'
  (root/'task.txt').write_text(value);(root/'impl.md').write_text('Behavior, checks and limits documented.')
  result={'summary':'synthetic worker','decision_requests':['Choose core semantics'] if fault=='decision' else []}
 elif schema=='publication.schema.json':
  result={'safe':True,'files':['impl.md','task.txt'],'blocking_findings':[],'decision_requests':[],'evidence':'Synthetic publication-safety review of exact allowed task files.'}
 else:
  passed=(root/'task.txt').read_text().startswith('good') and not (state/'reject_review').exists()
  result={'verdict':'pass' if passed else 'changes_requested','blocking_findings':[] if passed else ['Plausible text violates independent quality criterion.'],'decision_requests':[],'criteria':[{'id':i,'passed':passed,'evidence':'Synthetic independent judgment for '+i} for i in ['quality','documentation_sync']]}
  if fault=='mutate_review':(root/'impl.md').write_text('Changed after tests during review')
  if fault=='invalid_review':result={}
  if fault=='format_review' and 'review-format' not in str(out):result['decision_requests']=['No new owner decision is recorded.']
 out.write_text(json.dumps(result));sys.exit(0)
if a[:2]==['repo','view']: print(json.dumps({'nameWithOwner':os.environ['FIXTURE_REPO'],'viewerPermission':'ADMIN'}));sys.exit(0)
if a[:2]==['workflow','list']:print(json.dumps([{'name':'Test','state':'active','path':'.github/workflows/test.yml'}]));sys.exit(0)
if a[:2]==['run','list']:
 head=a[a.index('--commit')+1];branch=a[a.index('--branch')+1]
 if not (state/'firsthead').exists():(state/'firsthead').write_text(head)
 failed=fault=='ci_repair' and (state/'firsthead').read_text()==head
 (state/'cihead').write_text(head);(state/'cifailed').write_text(str(failed))
 print(json.dumps([{'databaseId':1,'name':'Test','status':'completed','conclusion':'failure' if failed else 'success','headSha':head,'event':'push','headBranch':branch}]));sys.exit(0)
if a[:2]==['run','view']:
 if '--log-failed' in a:print('synthetic remote missing dependency');sys.exit(0)
 failed=(state/'cifailed').read_text()=='True'
 print(json.dumps({'headSha':(state/'cihead').read_text(),'event':'push','jobs':[{'name':'test','conclusion':'failure' if failed else 'success'}]}));sys.exit(0)
raise SystemExit('Unexpected synthetic command '+repr(a))
'''


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.repo = self.base/'target';self.repo.mkdir()
        self.remote = self.base/'remote.git'
        self.cmd('git','init','-q','-b','main',str(self.repo),cwd=self.base)
        for key,value in [('user.name','Fixture'),('user.email','fixture@example.invalid')]:
            self.cmd('git','config',key,value)
        (self.repo/'.gitignore').write_text('.local/\n')
        (self.repo/'AGENTS.md').write_text('Synthetic task policy.')
        (self.repo/'task.txt').write_text('baseline')
        (self.repo/'impl.md').write_text('pending')
        self.cmd('git','add','.');self.cmd('git','commit','-qm','baseline')
        self.cmd('git','init','--bare','-q',str(self.remote),cwd=self.base)
        self.cmd('git','remote','add','origin',str(self.remote))
        self.cmd('git','push','-q','origin','main')
        self.cmd('git','checkout','-qb','work')
        self.bindir=self.base/'bin';self.bindir.mkdir()
        for name in ['gh','codex']:
            p=self.bindir/name;p.write_text(FAKE);p.chmod(0o755)
        self.fixture_state=self.base/'fake-state';self.fixture_state.mkdir()
        self.project=self.base/'project.json'
        # Execution contract is external to target, inside a temporary controller
        # fixture ROOT. Existing controller source is not copied/imported into target.
        self.control=self.base/'controller';self.control.mkdir()
        self.cmd('git','init','-q',str(self.control),cwd=self.base)
        (self.control/'contracts').mkdir();(self.control/'schemas').mkdir()
        for name in ['implementation.schema.json','review.schema.json','publication.schema.json']:
            shutil.copyfile(TOOLS.parent/'schemas'/name,self.control/'schemas'/name)
        self.contract=self.control/'contracts/task.json'
        self.contract.write_text(json.dumps({'id':'fixture','criteria':[{'id':'quality','requirement':'Must start with good; plausible is insufficient.'}],
                                            'allowed_paths':['task.txt','impl.md'],'checks':[[sys.executable,'-c','from pathlib import Path; s=Path("task.txt").read_text(); raise SystemExit(0 if s.startswith(("good","plausible")) else 1)']]}))
        cfg={'schema_version':2,'id':'fixture','root':str(self.repo),'contract':str(self.contract),
             'delivery':{'repository':str(self.remote).removesuffix('.git'),'remote':'origin','base':'main','head':'work','required_gates':[{'workflow':'Test','job':'test','event':'push'}]},
             'browser':{'executable':'synthetic-browser','prepare':[sys.executable,'-c','print("synthetic harness")'],
                        'validate':[sys.executable,'-c','print("synthetic validator")']}}
        self.project.write_text(json.dumps(cfg))
        self.env={'PATH':str(self.bindir)+os.pathsep+os.environ['PATH'],'FIXTURE_TARGET':str(self.repo),
                  'FIXTURE_REPO':str(self.remote).removesuffix('.git'),'FIXTURE_STATE':str(self.fixture_state)}
        self.environment=patch.dict(os.environ,self.env);self.environment.start();self.addCleanup(self.environment.stop)
        self.root_patch=patch('delivery_loop.ROOT',self.control);self.root_patch.start();self.addCleanup(self.root_patch.stop)
        self.browser=patch('delivery_loop.browser_run',side_effect=lambda *a,**k:{'status':'PASS','userAgent':'HeadlessChrome synthetic test adapter'})
        self.browser_mock=self.browser.start();self.addCleanup(self.browser.stop)

    def cmd(self,*a,cwd=None):
        return subprocess.check_output(list(a),cwd=cwd or self.repo,stderr=subprocess.STDOUT,text=True).strip()

    def delivery(self,folder='run',cycles=3):
        return Delivery(self.project,self.base/folder,300,cycles,str(self.bindir/'codex'))

    def test_w01_w11_w18_branch_report_and_idempotent_resume(self):
        d=self.delivery();s=d.run();self.assertEqual(s['status'],'ready_for_merge_approval')
        head=git(self.repo,'rev-parse','HEAD');self.assertEqual(git(self.remote,'rev-parse','refs/heads/work'),head)
        self.assertEqual(git(self.remote,'rev-parse','refs/heads/main'),s['baseline_head'])
        report=json.loads(Path(s['report']).read_text());self.assertEqual(report['source_sha'],head)
        self.assertTrue(report['review']['verdict']=='pass');self.assertEqual(report['ci']['status'],'success')
        resumed=self.delivery().run();self.assertEqual(resumed['status'],'ready_for_merge_approval')
        self.assertEqual(git(self.repo,'rev-parse','HEAD'),head)
        self.assertEqual(int((self.fixture_state/'workers').read_text()),1)
        commands=[json.loads(p.read_text())['argv'] for p in (self.base/'run').rglob('*.json') if p.name.endswith('.json') and 'argv' in json.loads(p.read_text())]
        self.assertFalse(any('pr' in argv for argv in commands))

    def test_w02_failed_check_drives_repair(self):
        os.environ['FIXTURE_FAULT']='check_repair'
        s=self.delivery().run();self.assertEqual(s['status'],'ready_for_merge_approval')
        self.assertEqual(len(s['attempts']),2)
        self.assertIn('failed_checks',s['attempts'][0]['feedback'])
        self.assertTrue((self.base/'run/attempt-001/check-0.log').exists())

    def test_w03_independent_negative_review_drives_repair(self):
        os.environ['FIXTURE_FAULT']='review_repair'
        s=self.delivery().run();self.assertEqual(s['status'],'ready_for_merge_approval')
        self.assertEqual(len(s['attempts']),2)
        self.assertIn('review',s['attempts'][0]['feedback'])

    def test_contradictory_pass_requests_independent_format_clarification(self):
        os.environ['FIXTURE_FAULT']='format_review'
        s=self.delivery().run();self.assertEqual(s['status'],'ready_for_merge_approval')
        self.assertEqual(len(s['attempts']),1)
        original=json.loads((self.base/'run/attempt-001/review.json').read_text())
        final=json.loads((self.base/'run/attempt-001/review-format.json').read_text())
        self.assertTrue(original['decision_requests']);self.assertEqual(final['decision_requests'],[])

    def test_linked_revalidation_carries_cumulative_budget(self):
        first=self.delivery().run();old_budget=dict(first['budget'])
        cfg=json.loads(self.project.read_text());cfg['parent_budget']={'state_file':str(self.base/'run/state.json'),'reason':'Explicit controller implementation revalidation; fixed task unchanged.'}
        p=self.base/'linked-project.json';p.write_text(json.dumps(cfg))
        d=Delivery(p,self.base/'linked-run',99999,999,str(self.bindir/'codex'))
        self.assertEqual(d.state['budget']['deadline'],old_budget['deadline'])
        self.assertEqual(d.state['budget']['cycles'],1)
        s=d.run();self.assertEqual(s['status'],'ready_for_merge_approval');self.assertEqual(s['budget']['cycles'],2)

    def timeout_parent(self):
        folder=self.base/'timed-out-review';folder.mkdir()
        inputs=manifest(self.repo)
        save(folder/'review.input.json',inputs)
        save(folder/'review-execution.json',{'exit_code':'timeout','input_digest':inputs['digest']})
        parent={'status':'budget_exhausted','handoff':{'reason':'Phase timeout: review'},
                'attempts':[{'folder':str(folder)}],
                'budget':{'started_at':time.time()-30,'deadline':time.time()+120,'cycles':1,'max_cycles':5}}
        return parent,[str(folder/'review.input.json'),str(folder/'review-execution.json')]

    def test_review_timeout_link_carries_limits_and_cannot_fan_out(self):
        d=self.delivery();parent,protected=self.timeout_parent()
        d.state.update(parent);d.persist();old=dict(d.state['budget'])
        cfg=json.loads(self.project.read_text());cfg['protected_files']=protected
        cfg['parent_budget']={'state_file':str(d.state_file),'reason':'Repair phase timeout classification; original allowance only.','review_timeout_recovery':True,'parent_state_sha256':__import__('hashlib').sha256(d.state_file.read_bytes()).hexdigest(),'timeout_evidence_sha256':fingerprint([Path(x) for x in protected])}
        project=self.base/'recovery.json';save(project,cfg)
        child=Delivery(project,self.base/'recovered',9999,99,str(self.bindir/'codex'))
        self.assertEqual(child.state['budget']['deadline'],old['deadline'])
        self.assertEqual(child.state['budget']['cycles'],1)
        self.assertEqual(child.state['budget']['max_cycles'],5)
        with self.assertRaises(ValueError):Delivery(project,self.base/'fanout',9999,99,str(self.bindir/'codex'))

    def test_review_timeout_recovery_rejects_decision_or_finished_review(self):
        parent,protected=self.timeout_parent();self.assertTrue(recoverable_review_timeout(parent,self.repo,protected,fingerprint([Path(x) for x in protected])))
        parent['decision_requests']=['Choose semantics'];self.assertFalse(recoverable_review_timeout(parent,self.repo,protected,fingerprint([Path(x) for x in protected])))
        parent.pop('decision_requests');save(Path(parent['attempts'][0]['folder'])/'review.json',{'verdict':'changes_requested'})
        self.assertFalse(recoverable_review_timeout(parent,self.repo,protected,fingerprint([Path(x) for x in protected])))

    def test_review_timeout_recovery_rejects_mutation_expiry_and_unprotected_records(self):
        parent,protected=self.timeout_parent()
        self.assertFalse(recoverable_review_timeout(parent,self.repo,[]))
        (self.repo/'task.txt').write_text('mutated');self.assertFalse(recoverable_review_timeout(parent,self.repo,protected,fingerprint([Path(x) for x in protected])))
        (self.repo/'task.txt').write_text('baseline');parent['budget']['deadline']=time.time()-1
        self.assertFalse(recoverable_review_timeout(parent,self.repo,protected,fingerprint([Path(x) for x in protected])))

    def test_review_timeout_recovery_rejects_rewritten_or_unpinned_evidence(self):
        parent,protected=self.timeout_parent();expected=fingerprint([Path(x) for x in protected])
        self.assertFalse(recoverable_review_timeout(parent,self.repo,protected))
        self.assertTrue(recoverable_review_timeout(parent,self.repo,protected,expected))
        p=Path(protected[1]);record=json.loads(p.read_text());record['fabricated']=True;save(p,record)
        self.assertFalse(recoverable_review_timeout(parent,self.repo,protected,expected))

    def test_review_phase_timeout_retries_only_with_remaining_total_budget(self):
        d=self.delivery();before=dict(d.state['budget'])
        with patch.object(d.recorder,'command',side_effect=Halt('budget_exhausted','Phase timeout: review')):
            self.assertIn('invalid_review',d.review())
            self.assertNotIn('accepted_digest',d.state)
            self.assertEqual(d.state['budget']['deadline'],before['deadline'])
            d.state['budget']['deadline']=time.time()-1
            with self.assertRaises(Halt) as caught:d.review()
            self.assertEqual(caught.exception.status,'budget_exhausted')

    def test_link_allocation_crash_recovers_original_state_without_new_allowance(self):
        first=self.delivery().run();budget=dict(first['budget'])
        cfg=json.loads(self.project.read_text());cfg['parent_budget']={'state_file':str(self.base/'run/state.json'),'reason':'Explicit linked revalidation'}
        project=self.base/'crash-link-project.json';project.write_text(json.dumps(cfg));folder=self.base/'crash-linked'
        with patch.object(Delivery,'persist',side_effect=RuntimeError('crash after allocation journal')):
            with self.assertRaises(RuntimeError):Delivery(project,folder,9999,999,str(self.bindir/'codex'))
        ledger=json.loads((self.base/'run/state.json.child.json').read_text())
        self.assertEqual(ledger['phase'],'allocated');self.assertFalse((folder/'state.json').exists())
        recovered=Delivery(project,folder,9999,999,str(self.bindir/'codex'))
        self.assertEqual(recovered.state['run_id'],ledger['initial_state']['run_id'])
        self.assertEqual(recovered.state['budget']['deadline'],budget['deadline'])
        self.assertEqual(recovered.state['budget']['cycles'],budget['cycles'])
        self.assertEqual(json.loads((self.base/'run/state.json.child.json').read_text())['phase'],'active')

    def test_allocation_crash_cannot_rebaseline_changed_external_policy(self):
        self.delivery().run();policy=self.base/'owning-policy.json';policy.write_text('fixed criterion')
        cfg=json.loads(self.project.read_text());cfg['protected_files']=[str(policy)];cfg['parent_budget']={'state_file':str(self.base/'run/state.json'),'reason':'Explicit linked validation'}
        project=self.base/'policy-link.json';project.write_text(json.dumps(cfg));folder=self.base/'policy-child'
        with patch.object(Delivery,'persist',side_effect=RuntimeError('crash after allocation journal')):
            with self.assertRaises(RuntimeError):Delivery(project,folder,300,3,str(self.bindir/'codex'))
        policy.write_text('changed criterion after crash')
        with self.assertRaises(ValueError):Delivery(project,folder,9999,999,str(self.bindir/'codex'))
        self.assertFalse((folder/'state.json').exists())

    def pending_activation_fixture(self):
        import delivery_loop
        self.delivery().run();policy=self.base/'activation-policy.json';policy.write_text('fixed policy')
        cfg=json.loads(self.project.read_text());cfg['protected_files']=[str(policy)];cfg['parent_budget']={'state_file':str(self.base/'run/state.json'),'reason':'Explicit linked revalidation'}
        project=self.base/'activation-project.json';project.write_text(json.dumps(cfg));folder=self.base/'activation-child'
        original=delivery_loop.save
        def crash_on_activation(path,value):
            if path.name.endswith('.child.json') and value.get('phase')=='active':
                raise RuntimeError('crash after child/control persistence before activation')
            return original(path,value)
        with patch('delivery_loop.save',side_effect=crash_on_activation):
            with self.assertRaises(RuntimeError):Delivery(project,folder,300,3,str(self.bindir/'codex'))
        state=json.loads((folder/'state.json').read_text());self.assertIn('controls',state)
        self.assertEqual(json.loads((self.base/'run/state.json.child.json').read_text())['phase'],'allocated')
        return project,folder,policy,state

    def test_post_persistence_pre_activation_crash_recovers_same_controls(self):
        project,folder,policy,state=self.pending_activation_fixture()
        recovered=Delivery(project,folder,9999,999,str(self.bindir/'codex'))
        self.assertEqual(recovered.state['controls'],state['controls'])
        self.assertEqual(recovered.state['budget']['deadline'],state['budget']['deadline'])
        self.assertEqual(recovered.state['budget']['cycles'],state['budget']['cycles'])
        self.assertEqual(json.loads((self.base/'run/state.json.child.json').read_text())['phase'],'active')

    def test_post_persistence_pre_activation_changed_policy_is_rejected(self):
        project,folder,policy,state=self.pending_activation_fixture();policy.write_text('new policy after crash')
        with self.assertRaises(ValueError):Delivery(project,folder,9999,999,str(self.bindir/'codex'))
        self.assertEqual(json.loads((folder/'state.json').read_text())['controls'],state['controls'])
        self.assertEqual(json.loads((self.base/'run/state.json.child.json').read_text())['phase'],'allocated')

    def test_parent_budget_cannot_fan_out_with_new_state_directory(self):
        self.delivery().run()
        cfg=json.loads(self.project.read_text());cfg['parent_budget']={'state_file':str(self.base/'run/state.json'),'reason':'Explicit linked validation'}
        p=self.base/'linked-project.json';p.write_text(json.dumps(cfg))
        Delivery(p,self.base/'child-one',300,3,str(self.bindir/'codex'))
        with self.assertRaises(ValueError):Delivery(p,self.base/'child-two',9999,999,str(self.bindir/'codex'))

    def test_genuine_parent_decision_cannot_be_bypassed_by_link(self):
        first=self.delivery().run();first['status']='decision_required';first['last_review']['verdict']='changes_requested';first['last_review']['decision_requests']=['Choose actual new semantics'];save(self.base/'run/state.json',first)
        cfg=json.loads(self.project.read_text());cfg['parent_budget']={'state_file':str(self.base/'run/state.json'),'reason':'Attempted bypass'};self.project.write_text(json.dumps(cfg))
        with self.assertRaises(ValueError):Delivery(self.project,self.base/'bad-linked',300,3,str(self.bindir/'codex'))

    def test_w04_w05_document_change_invalidates_approval(self):
        d=self.delivery();d.preflight();d.recorder_at(self.base/'run/probe-attempt');d.implement({})
        self.assertFalse(d.checks_and_browser());self.assertFalse(d.review())
        (self.repo/'impl.md').write_text('Unreviewed late documentation')
        with self.assertRaises(Halt) as caught:d.publisher.publish()
        self.assertEqual(caught.exception.status,'changes_requested')
        self.assertFalse(d.publisher.remote_head('work'))

    def test_negative_review_invalidates_prior_acceptance_for_same_contents(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        old_digest=d.state['accepted_digest']
        (self.fixture_state/'reject_review').write_text('new independent blocking judgment')
        self.assertIn('review',d.review());self.assertNotIn('accepted_digest',d.state)
        # Even a legacy leftover digest cannot override the current rejection.
        d.state['accepted_digest']=old_digest
        with self.assertRaises(Halt):d.publisher.publish()
        self.assertFalse(d.publisher.remote_head('work'))

    def test_w05_mutation_during_review_is_not_accepted(self):
        os.environ['FIXTURE_FAULT']='mutate_review';d=self.delivery();d.preflight();d.implement({});d.checks_and_browser()
        self.assertIn('stale_review',d.review());self.assertNotIn('accepted_digest',d.state)

    def test_w07_browser_missing_blocks_before_worker(self):
        self.browser_mock.side_effect=Halt('capability_blocked','No actual browser')
        s=self.delivery().run();self.assertEqual(s['status'],'capability_blocked')
        self.assertFalse((self.fixture_state/'workers').exists())

    def test_w08_protected_input_change_is_not_a_new_baseline(self):
        d=self.delivery();self.contract.write_text(self.contract.read_text()+'\n')
        with self.assertRaises(Halt) as caught:d.guard()
        self.assertEqual(caught.exception.status,'decision_required')
        with self.assertRaises(Halt):self.delivery()

    def test_w09_decision_cannot_be_approved_by_restart(self):
        os.environ['FIXTURE_FAULT']='decision';s=self.delivery().run()
        self.assertEqual(s['origin_status'],'decision_required')
        self.assertEqual(s['status'],'incomplete_published')
        with self.assertRaises(ValueError):self.delivery().run()
        self.assertEqual(s['handoff']['outcome'],'decision_required')

    def test_w10_budget_survives_restart(self):
        state={};budget=Budget(state,lambda:None,10,1);budget.cycle()
        resumed=Budget(state,lambda:None,99999,999)
        self.assertEqual(state['budget']['max_cycles'],1)
        with self.assertRaises(Halt):resumed.cycle()
        state['budget']['deadline']=time.time()-1
        with self.assertRaises(Halt):resumed.remaining()

    def test_w10_backwards_clock_does_not_extend_allowance(self):
        state={};Budget(state,lambda:None,10,1)
        state['budget']['last_seen']=time.time()+100
        with self.assertRaises(Halt):Budget(state,lambda:None,999,999)

    def test_w11_ambiguous_commit_resume_does_not_duplicate(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        with patch.object(d.publisher,'remote_head',side_effect=Halt('publication_blocked','simulated crash after commit')):
            with self.assertRaises(Halt):d.publisher.publish()
        head=git(self.repo,'rev-parse','HEAD');s=self.delivery().run()
        self.assertEqual(s['status'],'ready_for_merge_approval');self.assertEqual(head,git(self.repo,'rev-parse','HEAD'))

    def test_w12_unrelated_change_is_not_published(self):
        d=self.delivery();(self.repo/'private.txt').write_text('Unrelated original data')
        with self.assertRaises(Halt):d.publisher.scope()
        self.assertFalse(d.publisher.remote_head('work'))

    def test_w12_hidden_staged_contents_cannot_publish(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        # Revert impl.md in working tree while staging a different blob: a
        # working-file-only manifest must never certify this index content.
        baseline=self.cmd('git','show',d.state['baseline_head']+':impl.md')
        (self.repo/'impl.md').write_text(baseline)
        blob=subprocess.check_output(['git','hash-object','-w','--stdin'],input='unreviewed private blob',cwd=self.repo,text=True).strip()
        self.cmd('git','update-index','--cacheinfo','100644,'+blob+',impl.md')
        with self.assertRaises(Halt):d.publisher.scope()
        self.assertFalse(d.publisher.remote_head('work'))

    def test_w13_remote_failure_feeds_repair(self):
        os.environ['FIXTURE_FAULT']='ci_repair';s=self.delivery().run()
        self.assertEqual(s['status'],'ready_for_merge_approval');self.assertEqual(len(s['attempts']),2)
        self.assertIn('remote_failure',s['attempts'][0]['feedback'])
        self.assertTrue((self.base/'run/attempt-001/ci-failed-1.log').is_file())

    def test_readonly_infrastructure_retry_is_bounded_and_persisted(self):
        d=self.delivery();calls=[]
        def fail(argv,label,**kwargs):calls.append(label);return 1
        with patch.object(d.recorder,'command',side_effect=fail):
            with self.assertRaises(Halt):d.publisher.capture(['gh','run','list'],'transient-read')
            self.assertEqual(len(calls),2)
            with self.assertRaises(Halt):d.publisher.capture(['gh','run','list'],'transient-read-again')
            self.assertEqual(len(calls),3)
        self.assertTrue(d.state['infrastructure_retries'])

    def test_w02_browser_failure_transmits_exact_diagnostics(self):
        cfg=json.loads(self.project.read_text())
        cfg['browser']['prepare']=[sys.executable,'-c','from pathlib import Path; import sys; p=Path(sys.argv[1]);p.mkdir(exist_ok=True);(p/"python-result.json").write_text("missing public test function referenced by fixed evaluator")','{evidence}/browser']
        cfg['browser']['validate']=[sys.executable,'-c','from pathlib import Path;raise SystemExit(0 if Path("task.txt").read_text().startswith("good-2") else 1)']
        self.project.write_text(json.dumps(cfg));os.environ['FIXTURE_FAULT']='browser_repair'
        s=self.delivery().run();self.assertEqual(s['status'],'ready_for_merge_approval')
        feedback=s['attempts'][0]['feedback']
        self.assertTrue(feedback['project_observations']);self.assertTrue(feedback['raw_outputs'])
        observed=next(Path(p) for p in feedback['project_observations'] if Path(p).name=='python-result.json')
        self.assertEqual(observed.read_text(),'missing public test function referenced by fixed evaluator')
        self.assertEqual(len(s['attempts']),2)

    def test_environment_change_invalidates_review(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        with patch.dict(os.environ,{'NEW_RUNTIME_DEPENDENCY':'changed'}):
            with self.assertRaises(Halt) as caught:d.publisher.publish()
        self.assertEqual(caught.exception.status,'changes_requested')
        self.assertFalse(d.publisher.remote_head('work'))

    def test_command_environment_and_executable_are_bound_without_secrets(self):
        d=self.delivery()
        with patch.dict(os.environ,{'TEST_SECRET':'private-fixture-value'}):
            self.assertEqual(d.recorder.command([sys.executable,'-c','print("probe")'],'identity'),0)
        record=json.loads((d.recorder.folder/'identity-execution.json').read_text())
        self.assertTrue(record['environment']['inherited_sha256']);self.assertTrue(record['executable']['sha256'])
        self.assertNotIn('private-fixture-value',json.dumps(record))

    def test_ci_timeout_retains_last_pending_gate_state(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review();head=d.publisher.publish()
        capture=d.publisher.capture
        def pending(argv,label):
            return '[]' if argv[:3]==['gh','run','list'] else capture(argv,label)
        with patch.object(d.publisher,'capture',side_effect=pending):
            with self.assertRaises(Halt):d.publisher.ci(head,cap=.2)
        self.assertEqual(d.state['last_ci']['status'],'pending')
        self.assertEqual(d.state['last_ci']['head'],head)

    def test_report_is_idempotent_after_orphan_write(self):
        d=self.delivery();s=d.run();self.assertEqual(s['status'],'ready_for_merge_approval')
        before=len(list((self.base/'run/reports').glob('*.json')))
        with patch.object(d,'persist',side_effect=RuntimeError('crash after report write')):
            # Publisher retains original bound callback; patch it explicitly.
            with patch.object(d.publisher,'persist',side_effect=RuntimeError('crash after report write')):
                with self.assertRaises(RuntimeError):d.publisher.report('ready_for_merge_approval','orphan receipt',s['last_ci'])
        count=len(list((self.base/'run/reports').glob('*.json')));self.assertEqual(count,before+1)
        recovered=d.publisher.report('ready_for_merge_approval','orphan receipt',s['last_ci'])
        self.assertEqual(len(list((self.base/'run/reports').glob('*.json'))),count)
        again=d.publisher.report('ready_for_merge_approval','orphan receipt',s['last_ci'])
        self.assertEqual(again['report_id'],recovered['report_id'])
        self.assertEqual(again['created_at'],recovered['created_at'])

    def test_report_failure_never_persists_ready_state(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        with patch.object(d.publisher,'report',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):d.publish_and_check()
        self.assertEqual(d.state['status'],'reporting')

    def test_w13_pr_only_gate_requests_decision(self):
        p=json.loads(self.project.read_text());p['delivery']['required_gates'][0]['event']='pull_request';self.project.write_text(json.dumps(p))
        s=self.delivery().run();self.assertEqual(s['origin_status'],'decision_required')
        self.assertFalse((self.fixture_state/'workers').exists())

    def test_w14_external_head_movement_blocks_stale_push(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        with patch.object(d.publisher,'remote_head',side_effect=lambda branch:'f'*40 if branch=='work' else d.state['base_sha']):
            with self.assertRaises(Halt) as caught:d.publisher.publish()
        self.assertEqual(caught.exception.status,'decision_required')

    def test_w14_target_advance_integrates_then_revalidates(self):
        d=self.delivery();d.preflight();d.implement({});d.checks_and_browser();d.review()
        other=self.base/'other';self.cmd('git','clone','-q','--branch','main',str(self.remote),str(other),cwd=self.base)
        self.cmd('git','config','user.name','Fixture',cwd=other);self.cmd('git','config','user.email','fixture@example.invalid',cwd=other)
        (other/'base-note.txt').write_text('New unrelated base work')
        self.cmd('git','add','.',cwd=other);self.cmd('git','commit','-qm','advance base',cwd=other)
        self.cmd('git','push','-q','origin','main',cwd=other)
        with self.assertRaises(Halt) as caught:d.publisher.publish()
        self.assertEqual(caught.exception.status,'changes_requested')
        self.assertNotIn('accepted_digest',d.state)
        s=self.delivery().run();self.assertEqual(s['status'],'ready_for_merge_approval')
        self.assertEqual((self.repo/'base-note.txt').read_text(),'New unrelated base work')
        self.assertEqual(s['base_sha'],git(other,'rev-parse','HEAD'))

    def test_w12_dirty_baseline_is_preserved_and_rejected(self):
        (self.repo/'unrelated.txt').write_text('Owner uncommitted work')
        with self.assertRaises(ValueError):self.delivery()
        self.assertEqual((self.repo/'unrelated.txt').read_text(),'Owner uncommitted work')

    def test_publication_receipts_are_not_overwritten(self):
        d=self.delivery();d.preflight();d.publisher.remote_head('main');d.publisher.remote_head('main')
        records=list(d.recorder.folder.glob('remote-main*-execution.json'))
        self.assertGreaterEqual(len(records),3)

    def test_w15_failed_review_can_publish_only_as_incomplete(self):
        os.environ['FIXTURE_FAULT']='review_repair';s=self.delivery(cycles=1).run()
        self.assertEqual(s['status'],'incomplete_published');self.assertEqual(s['origin_status'],'budget_exhausted')
        self.assertNotIn('accepted_digest',s)
        self.assertEqual(json.loads(Path(s['report']).read_text())['status'],'incomplete_published')

    def test_w16_self_target_and_target_state_are_rejected(self):
        p=json.loads(self.project.read_text());p['root']=str(self.control);self.project.write_text(json.dumps(p))
        with self.assertRaises(ValueError):self.delivery()
        p['root']=str(self.repo);self.project.write_text(json.dumps(p))
        with self.assertRaises(ValueError):Delivery(self.project,self.repo/'.local/run')

    def test_legacy_state_not_silently_certified(self):
        folder=self.base/'run';folder.mkdir();save(folder/'state.json',{'status':'complete'})
        with self.assertRaises(ValueError):self.delivery()

    def test_invalid_review_never_accepts(self):
        os.environ['FIXTURE_FAULT']='invalid_review';s=self.delivery(cycles=1).run()
        self.assertNotEqual(s['status'],'ready_for_merge_approval');self.assertNotIn('accepted_digest',s)

    def test_manifest_stable_across_commit_and_tracks_deletions(self):
        before=manifest(self.repo);(self.repo/'task.txt').unlink();deleted=manifest(self.repo)
        self.assertNotEqual(before,deleted)
        self.cmd('git','add','-u');self.cmd('git','commit','-qm','delete')
        self.assertEqual(deleted,manifest(self.repo))

    def test_budget_timeout_terminates_child_group(self):
        from development_loop import execute
        log=self.base/'timeout.log';pidfile=self.base/'child.pid'
        script='import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"]);open(sys.argv[1],"w").write(str(p.pid));time.sleep(60)'
        with self.assertRaises(subprocess.TimeoutExpired):
            execute([sys.executable,'-c',script,str(pidfile)],self.repo,log,0.3)
        child=int(pidfile.read_text())
        for _ in range(20):
            result=subprocess.run(['ps','-p',str(child),'-o','stat='],capture_output=True,text=True)
            if result.returncode or result.stdout.strip().startswith('Z'):
                break
            time.sleep(.02)
        else:
            self.fail('Timed-out child process still running')

    def test_w04_generated_browser_runtime_mutation_invalidates_result(self):
        folder=self.base/'mutated-browser';folder.mkdir();harness=folder/'harness';harness.mkdir()
        entry=harness/'index.html';entry.write_text('original runtime')
        b=Budget({},lambda:None,120,1);r=Recorder(self.repo,{},lambda:None,b,folder,lambda:None)
        def command(argv,label,**kwargs):
            if label.endswith('-version'):(folder/(label+'.log')).write_text('Chrome synthetic mutation fixture')
            else:
                entry.write_text('different runtime')
                (folder/(label+'.log')).write_text('<pre id="results">{"status":"PASS"}</pre>')
            return 0
        with patch.object(r,'command',side_effect=command):
            with self.assertRaises(Halt) as caught:browser_run(r,'synthetic',harness)
        self.assertEqual(caught.exception.status,'changes_requested')

    def test_w06_real_chrome_executes_javascript(self):
        executable='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        executable=executable if Path(executable).exists() else shutil.which('google-chrome')
        if not executable:self.skipTest('Actual Chrome not installed; W06 remains a live-environment prerequisite.')
        folder=self.base/'actual-browser';folder.mkdir();harness=folder/'harness';harness.mkdir()
        (harness/'index.html').write_text('<pre id="results">WAIT</pre><script>document.getElementById("results").textContent=JSON.stringify({status:"PASS",computed:6*7});</script>')
        state={};b=Budget(state,lambda:None,120,1)
        r=Recorder(self.repo,state,lambda:None,b,folder,lambda:None)
        result=browser_run(r,executable,harness)
        self.assertEqual(result,{'status':'PASS','computed':42})
        binding=json.loads((folder/'browser-binding.json').read_text());self.assertIn('Chrome',binding['browser_version'])
        self.assertTrue(binding['harness'])
