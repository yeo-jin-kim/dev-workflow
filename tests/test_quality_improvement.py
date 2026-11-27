import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import quality_improvement as q

SCRIPT=r'''
import sys,json
from pathlib import Path
sys.path.insert(0,TOOLS)
from development_loop import digest
stage,target,out,packet=sys.argv[1:]
target,out=Path(target),Path(out);packet=json.loads(Path(packet).read_text())
mode=MODE
cases=CASES
result={'source_digest':digest(target),'decision_requests':[],'model_identity':[{'provider':'local','model':'different' if stage=='evaluate' and mode=='model_swap' and (target/'code').read_text()=='fixed' else 'pinned'}]}
if stage=='evaluate':
    after=(target/'code').read_text()=='fixed'
    statuses={'broken':'pass' if after else 'fail','neighbor':'pass'}
    if after and mode=='regression':statuses['neighbor']='fail'
    if after and mode=='hide':statuses['broken']='deferred'
    result.update(schema_version=1,dataset_digest=DATASET,cases=[{'id':k,'expected_digest':v,'status':statuses[k]} for k,v in cases.items()])
    if after and mode=='coverage':result['cases'].pop()
elif stage=='diagnose':
    result.update(reproduced=True,root_cause='Synthetic fixture returns the wrong literal',evidence=['code and baseline'],change_class='semantic_policy' if mode=='semantic' else 'implementation')
elif stage=='repair':
    (target/'code').write_text('fixed')
    if mode=='scope':(target/'outside').write_text('forbidden')
    if mode=='gold':Path(GOLD).write_text('{}')
    result['source_digest']=digest(target)
    if mode=='timeout':__import__('time').sleep(5)
elif stage=='review':
    result.update(verdict='changes_requested' if mode=='review_reject' else 'pass',blocking_findings=['Needs more evidence'] if mode=='review_reject' else [],criteria={k:True for k in CRITERIA},evidence=['Synthetic evaluator and diff'])
    if mode=='decision':result['decision_requests']=['Choose model']
    if mode=='review_write':(target/'code').write_text('reviewer mutation');result['source_digest']=digest(target)
(out/'step.json').write_text(json.dumps(result))
'''

class QualityProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name).resolve();self.ctrl=root/'controller';self.ctrl.mkdir();self.target=root/'target'
        subprocess.run(['git','init','-b','workflow/test',str(self.target)],check=True,capture_output=True)
        for key,value in [('user.email','test@example.invalid'),('user.name','Test')]:q.git(self.target,'config',key,value)
        (self.target/'code').write_text('broken');q.git(self.target,'add','.');q.git(self.target,'commit','-m','baseline')
        self.patcher=patch.object(q,'ROOT',self.ctrl);self.patcher.start();self.addCleanup(self.patcher.stop)
        self.cases={'broken':q.sha('expected-correct-value'),'neighbor':q.sha('preserved-neighbor')}
        self.gold=self.ctrl/'gold.json';q.save(self.gold,{'cases':self.cases})
        self.script=self.ctrl/'fixture.py';self.cfg=self.ctrl/'policy.json'
        self.configure()

    def configure(self,mode='normal',cycles=3):
        code=SCRIPT.replace('TOOLS',repr(str(Path(q.__file__).parent))).replace('MODE',repr(mode)).replace('CASES',repr(self.cases)).replace('DATASET',repr(q.sha(self.cases))).replace('CRITERIA',repr(sorted(q.CRITERIA))).replace('GOLD',repr(str(self.gold)))
        self.script.write_text(code)
        q.save(self.cfg,{'schema_version':1,'enabled':True,'episode_id':'one-incident','authorization_reference':'Synthetic test authorization, not a real owner decision','target':str(self.target),'branch':'workflow/test','total_seconds':30,'max_cycles':cycles,'step_seconds':1 if mode=='timeout' else 10,'allowed_paths':['code'],'cases':str(self.gold),'protected_files':[str(self.script)],'commands':{k:[sys.executable,str(self.script),k,'{target}','{output}','{input}'] for k in ['evaluate','diagnose','repair','review']}})

    def run_protocol(self):return q.Protocol(self.cfg).run()

    def test_long_step_limit_remains_under_cumulative_deadline(self):
        cfg=q.read(self.cfg);cfg['step_seconds']=3600;q.save(self.cfg,cfg)
        result=self.run_protocol()
        self.assertEqual(result['status'],'awaiting_human_retest')
        self.assertEqual(result['cycles'],1)
        cfg['step_seconds']=3601;q.save(self.cfg,cfg)
        with self.assertRaisesRegex(ValueError,'per-step'):q.Protocol(self.cfg)

    def test_full_loop_stops_at_human_retest_and_repeated_run_does_not_renew(self):
        result=self.run_protocol()
        self.assertEqual(result['status'],'awaiting_human_retest');self.assertEqual(result['cycles'],1)
        self.assertFalse(result['merge_authorized']);self.assertFalse(result['publication_authorized'])
        self.assertEqual(self.run_protocol()['deadline'],result['deadline'])
        self.assertEqual(len(result['history']),5)

    def test_feedback_is_automatically_repaired_with_cumulative_cycles(self):
        self.configure('review_reject');r=self.run_protocol()
        self.assertEqual(r['status'],'decision_required')
        # First review rejection gets a second diagnosis/repair attempt without a human prompt.
        self.assertEqual(r['cycles'],2)
        second=q.read(self.ctrl/'.local/quality-improvement/one-incident/2-diagnose/input.json')
        self.assertEqual(second['review_feedback']['review']['verdict'],'changes_requested')

    def test_coverage_and_gold_changes_fail_closed(self):
        for mode in ['coverage','gold','scope','semantic','decision','review_write']:
            with self.subTest(mode=mode):
                # Every subcase gets a separate temporary fixture and episode, never reset a live run.
                t=QualityProtocolTests('test_full_loop_stops_at_human_retest_and_repeated_run_does_not_renew');t.setUp()
                try:
                    t.configure(mode);r=t.run_protocol();self.assertEqual(r['status'],'decision_required');self.assertNotEqual(r.get('status'),'awaiting_human_retest')
                finally:t.doCleanups()

    def test_regression_and_deferral_do_not_pass(self):
        self.configure('regression');r=self.run_protocol();self.assertEqual(r['status'],'decision_required')
        self.assertTrue(r['review_feedback']['regressions'])

    def test_budget_is_not_replaced_by_an_updated_policy(self):
        r=self.run_protocol();cfg=q.read(self.cfg);cfg['total_seconds']=31;q.save(self.cfg,cfg)
        with self.assertRaisesRegex(ValueError,'renew/change'):self.run_protocol()
        self.assertEqual(q.read(self.ctrl/'.local/quality-improvement/one-incident/state.json')['deadline'],r['deadline'])

    def test_cycle_limit_and_timeout_are_persisted(self):
        self.configure('review_reject',cycles=1);r=self.run_protocol();self.assertEqual(r['status'],'budget_exhausted')

    def test_interrupted_step_cannot_silently_repeat(self):
        p=q.Protocol(self.cfg);state={'status':'repair','authority':p.authority,'deadline':123,'cycles':1};q.save(p.file,state)
        self.assertEqual(p.run()['status'],'interrupted')
        self.assertEqual(q.read(p.file)['cycles'],1)

    def test_source_binding_and_case_labels_cannot_be_forged(self):
        row={'schema_version':1,'dataset_digest':q.sha(self.cases),'source_digest':'source','cases':[{'id':k,'expected_digest':v,'status':'pass'} for k,v in self.cases.items()]}
        for key,value in [('source_digest','other'),('dataset_digest','other')]:
            changed=dict(row,**{key:value})
            with self.assertRaises(ValueError):q.observation(changed,self.cases,'source')
        row['cases'][0]['expected_digest']='different'
        with self.assertRaises(ValueError):q.observation(row,self.cases,'source')

    def test_captured_topic_analysis_is_diagnostic_not_gold(self):
        report=self.ctrl/'captured.json';q.save(report,{'runs':[{'sourceId':'a','status':'schema_error','error':'Activity name absent from cited segments','stages':[]},{'sourceId':'b','status':'completed','outcomes':[{'status':'needs_scope'}]}]})
        out=self.ctrl/'analysis.json';r=q.analyze_topics(report,out)
        self.assertEqual(r['sources_with_errors'],1);self.assertFalse(r['root_cause_proven']);self.assertFalse(r['semantic_quality_accepted'])
        with self.assertRaises(ValueError):q.analyze_topics(report,out)


class AdditionalProtocolTests(unittest.TestCase):
    setUp=QualityProtocolTests.setUp
    configure=QualityProtocolTests.configure
    run_protocol=QualityProtocolTests.run_protocol
    # Inherited base cases are tested once; add targeted protections here.
    __unittest_skip__=False
    def test_retest_candidate_is_invalidated_by_later_target_changes(self):
        r=self.run_protocol();self.assertEqual(r['status'],'awaiting_human_retest')
        (self.target/'code').write_text('changed after review')
        again=self.run_protocol();self.assertEqual(again['status'],'decision_required')
        self.assertIn('stale',again['reason'])
    def test_observed_model_change_requires_owner_decision(self):
        self.configure('model_swap');cfg=q.read(self.cfg);cfg['require_model_identity']=True;q.save(self.cfg,cfg)
        r=self.run_protocol();self.assertEqual(r['status'],'decision_required')
        self.assertIn('provider/model changed',r['reason'])
    def test_prior_evidence_tampering_invalidates_ready_candidate(self):
        r=self.run_protocol();self.assertEqual(r['status'],'awaiting_human_retest')
        (Path(r['history'][0]['directory'])/'process.log').write_text('rewritten baseline evidence')
        after=self.run_protocol();self.assertEqual(after['status'],'decision_required')
        self.assertIn('Prior stage evidence changed',after['reason'])
    def test_failure_cannot_be_hidden_as_deferral(self):
        self.configure('hide');r=self.run_protocol()
        self.assertNotEqual(r['status'],'awaiting_human_retest')
        self.assertTrue(r['review_feedback']['hidden_failures'])
    def test_cumulative_wall_clock_timeout_kills_step_and_cannot_restart(self):
        self.configure('timeout');cfg=q.read(self.cfg);cfg['total_seconds']=1;q.save(self.cfg,cfg)
        r=self.run_protocol();self.assertEqual(r['status'],'budget_exhausted')
        self.assertEqual(self.run_protocol()['cycles'],r['cycles'])
    def test_review_integers_are_not_boolean_passes(self):
        code=self.script.read_text().replace("criteria={k:True for k in", "criteria={k:1 for k in")
        self.script.write_text(code)
        self.assertNotEqual(self.run_protocol()['status'],'awaiting_human_retest')

class TopicAdapterTests(unittest.TestCase):
    def test_conversion_preserves_coverage_and_does_not_make_runtime_semantic_gold(self):
        import quality_topic_evaluate as e
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);gold=root/'gold.json';manifest=root/'manifest.json'
            q.save(gold,{'cases':[{'id':'positive','text':'Project','expected':[['project','Project']]}]})
            q.save(manifest,{'sources':[{'id':'real','digest':'frozen-source'}]})
            cfg={'gold':str(gold),'manifest':str(manifest)}
            gr={'runs':[{'sourceId':'positive','status':'completed','outcomes':[]}],'goldEvaluation':[{'id':'positive','exactMatch':False,'forbiddenCategoryPresent':False}]}
            rr={'runs':[{'sourceId':'real','status':'completed','outcomes':[{'status':'no_subject'}]}]}
            out=e.convert(cfg,gr,rr,'candidate')
            self.assertEqual([r['status'] for r in out['cases']],['fail','pass'])
            self.assertFalse(out['semantic_quality_accepted'])
            rr['runs']=[]
            with self.assertRaises(ValueError):e.convert(cfg,gr,rr,'candidate')
    def test_agent_roles_are_separate_readonly_and_workspace_write(self):
        import quality_agent_stage as a
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve();controller=root/'controller';target=root/'target';target.mkdir();(target/'code').write_text('example')
            subprocess.run(['git','init',str(target)],check=True,capture_output=True)
            q.git(target,'add','code')
            contract=root/'contract.json';contract.write_text('{}')
            calls=[]
            def simulated(argv,**kw):
                calls.append(argv);Path(argv[argv.index('-o')+1]).write_text(json.dumps({'decision_requests':[]}))
                return type('Result',(),{'returncode':0})()
            with patch.object(a,'ROOT',controller),patch.object(a,'subprocess',SimpleNamespace(run=simulated,STDOUT=subprocess.STDOUT)):
                for stage in ['diagnose','repair','review']:
                    a.invoke(stage,target,{},controller/'.local'/stage,contract)
            self.assertEqual([c[c.index('-s')+1] for c in calls],['read-only','workspace-write','read-only'])
            self.assertTrue(all('--model' not in c for c in calls))

if __name__=='__main__':unittest.main()
