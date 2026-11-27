"""Bounded quality improvement protocol. Trusted operator policy, untrusted incident data.

Commands are argv arrays from the controller policy, never from incident notes.
They write step.json in a fresh {output} directory. No merge/deploy/publication API.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import subprocess
from development_loop import execute, lock, save, digest
from delivery_evidence import git

ROOT=Path(__file__).resolve().parents[1]
TERMINAL={'awaiting_human_retest','decision_required','budget_exhausted','interrupted'}
CRITERIA={'root_cause','source_grounding','regression','documentation_sync','scope'}


def read(path):
    path=Path(path)
    if path.is_symlink():raise ValueError('Symlink evidence/policy refused')
    value=json.loads(path.read_text())
    if not isinstance(value,dict):raise ValueError('JSON object required')
    return value


def sha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def fingerprint(paths):
    result={}
    for name in paths:
        p=Path(name).resolve(strict=True)
        if not p.is_file():raise ValueError('Protected file required')
        result[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def evidence_manifest(folder):
    result={}
    for item in sorted(Path(folder).rglob('*')):
        if item.is_symlink():raise ValueError('Symlink evidence refused')
        if item.is_file():result[str(item.relative_to(folder))]=hashlib.sha256(item.read_bytes()).hexdigest()
    return result


def policy(path):
    path=Path(path).resolve(strict=True);cfg=read(path)
    if not path.is_relative_to(ROOT):raise ValueError('Policy must be controller-owned')
    if cfg.get('schema_version')!=1 or cfg.get('enabled') is not True or not cfg.get('authorization_reference'):
        raise ValueError('Enabled trusted policy and owner scope reference required')
    episode=cfg.get('episode_id','')
    if not episode or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in episode):raise ValueError('Stable episode ID required')
    target=Path(cfg['target']).resolve(strict=True)
    if target==ROOT or ROOT in target.parents or target in ROOT.parents:raise ValueError('Controller/target must be disjoint')
    if cfg.get('branch') in {None,'','main','master'}:raise ValueError('Dedicated candidate branch required')
    for key,maximum in [('total_seconds',3600),('max_cycles',5)]:
        if type(cfg.get(key)) is not int or not 1<=cfg[key]<=maximum:raise ValueError('Explicit bounded limits required')
    if type(cfg.get('step_seconds',600)) is not int or not 1<=cfg.get('step_seconds',600)<=600:raise ValueError('Invalid per-step timeout')
    allowed=cfg['allowed_paths']
    if not isinstance(allowed,list) or not allowed:raise ValueError('Explicit allowed files required')
    for name in allowed:
        if not isinstance(name,str):raise ValueError('Literal file paths required')
        p=Path(name)
        if not isinstance(name,str) or p.is_absolute() or '..' in p.parts or name.startswith('.git') or any(c in name for c in '*?['):raise ValueError('Only literal target paths allowed')
        if not (target/p).resolve().is_relative_to(target) or (target/p).is_symlink():raise ValueError('Allowed paths must stay inside target')
    cases=read(cfg['cases'])
    if not isinstance(cases.get('cases'),dict) or not cases['cases'] or any(not isinstance(k,str) or not k or not isinstance(v,str) or len(v)!=64 for k,v in cases['cases'].items()):raise ValueError('Frozen case IDs and expectation digests required')
    commands=cfg['commands']
    for stage in ['evaluate','diagnose','repair','review']:
        argv=commands.get(stage)
        if not isinstance(argv,list) or not argv or any(not isinstance(a,str) or not a for a in argv) or not any('{output}' in a for a in argv):raise ValueError('Trusted argv with {output} required for '+stage)
    command_files=[Path(a) for argv in commands.values() for a in argv[1:] if '{' not in a and Path(a).is_absolute() and Path(a).is_file()]
    stage_files=[Path(__file__).with_name('quality_agent_stage.py'),*(Path(__file__).resolve().parents[1]/'schemas').glob('quality-*.schema.json')]
    protected=[*stage_files,path,Path(__file__),Path(__file__).with_name('development_loop.py'),Path(__file__).with_name('delivery_evidence.py'),Path(cfg['cases']),*map(Path,cfg['protected_files']),*command_files]
    if not cfg['protected_files']:raise ValueError('Protected evaluator/data inputs required')
    for item in protected:
        resolved=item.resolve(strict=True)
        if resolved.is_relative_to(target) and str(resolved.relative_to(target)) in allowed:raise ValueError('Allowed files overlap protected inputs')
    return cfg,target,cases['cases'],fingerprint(protected)


def model_binding(value):
    rows=value.get('model_identity')
    if not isinstance(rows,list) or not rows or any(not isinstance(r,dict) or not r.get('provider') or not r.get('model') for r in rows):raise ValueError('Observed provider/model identity missing')
    return rows


def observation(value,cases,source):
    if value.get('schema_version')!=1 or value.get('source_digest')!=source or value.get('dataset_digest')!=sha(cases):raise ValueError('Evaluation version/dataset binding mismatch')
    rows=value.get('cases')
    if not isinstance(rows,list) or len(rows)!=len(cases):raise ValueError('Missing evaluation cases')
    found={}
    for row in rows:
        if not isinstance(row,dict) or row.get('id') in found or row.get('id') not in cases or row.get('expected_digest')!=cases[row['id']] or row.get('status') not in {'pass','fail','deferred'}:raise ValueError('Invalid/changed evaluation case')
        found[row['id']]=row['status']
    if set(found)!=set(cases):raise ValueError('Evaluation coverage changed')
    return found


class Protocol:
    def __init__(self,path):
        self.path=Path(path).resolve();self.cfg,self.target,self.cases,self.authority=policy(path)
        self.folder=ROOT/'.local/quality-improvement'/self.cfg['episode_id']
        (ROOT/'.local/locks').mkdir(parents=True,exist_ok=True)
        self.folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        self.file=self.folder/'state.json'

    def check(self,allow_target_change=False):
        if policy(self.path)[3]!=self.state['authority']:raise ValueError('Authority/protected inputs changed')
        for item in self.state['history']:
            if evidence_manifest(Path(item['directory']))!=item['files']:raise ValueError('Prior stage evidence changed')
        if git(self.target,'branch','--show-current')!=self.cfg['branch']:raise ValueError('Candidate branch changed')
        if git(self.target,'rev-parse','HEAD')!=self.state['head']:raise ValueError('Candidate HEAD moved outside protocol')
        for name in self.cfg['allowed_paths']:
            if not (self.target/name).resolve().is_relative_to(self.target) or (self.target/name).is_symlink():raise ValueError('Allowed path escaped target')
        if not allow_target_change and digest(self.target)!=self.state['expected_digest']:raise ValueError('Target changed outside the recorded stage')
        names=set(filter(None,git(self.target,'diff','--name-only',self.state['head']).splitlines()))
        names.update(filter(None,git(self.target,'ls-files','--others','--exclude-standard').splitlines()))
        if not names<=set(self.cfg['allowed_paths']):raise ValueError('Target changed outside allowed files')

    def checkpoint(self,status,**extra):
        self.state.update(status=status,updated_at=time.time(),**extra);save(self.file,self.state)

    def remaining(self):
        left=self.state['deadline']-time.time()
        if left<=0:raise TimeoutError('Cumulative deadline exhausted')
        return left

    def step(self,stage,number,packet):
        self.check();self.remaining()
        output=self.folder/(str(number)+'-'+stage)
        output.mkdir(exist_ok=False,mode=0o700)
        packet_file=output/'input.json';save(packet_file,packet)
        before=digest(self.target)
        argv=[a.replace('{output}',str(output)).replace('{input}',str(packet_file)).replace('{target}',str(self.target)).replace('{remaining_seconds}',str(max(1,int(self.remaining())))) for a in self.cfg['commands'][stage]]
        self.state['active_step']={'stage':stage,'directory':str(output),'source_digest':before}
        self.checkpoint(stage)
        code=execute(argv,self.target,output/'process.log',min(self.remaining(),self.cfg.get('step_seconds',600)))
        self.check(allow_target_change=stage=='repair')
        if stage!='repair' and digest(self.target)!=before:raise ValueError('Read-only stage changed target')
        if code:raise ValueError(stage+' command failed; inspect preserved process.log')
        result=read(output/'step.json')
        if result.get('decision_requests'):
            raise ValueError('Human decision required: '+str(result['decision_requests']))
        if stage in {'evaluate','diagnose','review'} and result.get('source_digest')!=digest(self.target):raise ValueError('Stale step result')
        self.state['history'].append({'stage':stage,'directory':str(output),'result_sha256':sha(result),'source_digest':digest(self.target),'files':evidence_manifest(output)})
        self.checkpoint(stage,active_step=None,expected_digest=digest(self.target))
        return result

    def run(self):
        # Target lock is shared with existing W1/W2 runners; episode lock prevents duplicate consumption.
        with lock(ROOT/'.local/locks'/hashlib.sha256(str(self.target).encode()).hexdigest()),lock(self.folder/'lock'):
            if self.file.exists():
                self.state=read(self.file)
                if self.state['authority']!=self.authority:raise ValueError('Cannot renew/change an existing episode')
                if self.state['status'] in TERMINAL:
                    if self.state['status']=='awaiting_human_retest':
                        try:self.check()
                        except Exception as error:self.checkpoint('decision_required',reason='Candidate became stale: '+str(error))
                    return self.state
                # A process killed between checkpoints must never silently rerun a mutating step.
                self.checkpoint('interrupted',reason='Interrupted episode requires operator recovery; original budget/evidence preserved')
                return self.state
            if git(self.target,'status','--porcelain'):raise ValueError('Clean candidate baseline required')
            self.state={'schema_version':1,'episode_id':self.cfg['episode_id'],'authority':self.authority,'head':git(self.target,'rev-parse','HEAD'),'expected_digest':digest(self.target),'deadline':time.time()+self.cfg['total_seconds'],'cycles':0,'history':[],'merge_authorized':False,'publication_authorized':False}
            self.checkpoint('preflight')
            try:
                initial=self.step('evaluate',0,{'phase':'baseline','cases':self.cases})
                if self.cfg.get('require_model_identity'):model_binding(initial)
                baseline=observation(initial,self.cases,digest(self.target));previous=baseline
                self.state['baseline']=initial
                if not any(s=='fail' for s in baseline.values()):raise ValueError('No reproduced failure; do not manufacture a repair')
                stalled=0
                for cycle in range(1,self.cfg['max_cycles']+1):
                    self.remaining();self.state['cycles']=cycle
                    diagnosis=self.step('diagnose',cycle,{'observation':initial,'previous_statuses':previous,'baseline':baseline,'history':self.state['history'],'review_feedback':self.state.get('review_feedback')})
                    if diagnosis.get('reproduced') is not True or not diagnosis.get('root_cause') or not diagnosis.get('evidence') or diagnosis.get('change_class') not in {'implementation','prompt_format'}:
                        raise ValueError('Unproven cause or semantic/model/scope change requires owner decision')
                    before=digest(self.target)
                    self.step('repair',cycle,{'diagnosis':diagnosis,'baseline':initial,'failed_cases':[k for k,v in previous.items() if v=='fail'],'allowed_paths':self.cfg['allowed_paths'],'protected_expectations':self.cases,'deadline':self.state['deadline'],'cycles_remaining':self.cfg['max_cycles']-cycle})
                    if before==digest(self.target):raise ValueError('Repair produced no candidate change')
                    candidate=self.step('evaluate',cycle,{'phase':'candidate','baseline':initial,'diagnosis':diagnosis})
                    if self.cfg.get('require_model_identity') and model_binding(candidate)!=model_binding(self.state['baseline']):raise ValueError('Observed provider/model changed; owner decision required')
                    current=observation(candidate,self.cases,digest(self.target))
                    regressions=[k for k in current if previous[k]=='pass' and current[k]!='pass']
                    hidden=[k for k in current if previous[k]=='fail' and current[k]=='deferred']
                    improvement=any(previous[k]=='fail' and current[k]=='pass' for k in current)
                    review=self.step('review',cycle,{'diagnosis':diagnosis,'baseline':self.state['baseline'],'candidate':candidate,'history':self.state['history'],'required_criteria':sorted(CRITERIA),'regressions':regressions,'hidden_failures':hidden})
                    criteria=review.get('criteria',{})
                    accepted=review.get('verdict')=='pass' and review.get('blocking_findings')==[] and review.get('decision_requests')==[] and isinstance(criteria,dict) and set(criteria)==CRITERIA and all(v is True for v in criteria.values()) and review.get('evidence')
                    if review.get('verdict') not in {'pass','changes_requested'}:raise ValueError('Missing/invalid review verdict')
                    initial=candidate
                    self.state['review_feedback']={'review':review,'regressions':regressions,'hidden_failures':hidden,'measured_improvement':improvement}
                    if not accepted or regressions or hidden or not improvement:
                        stalled+=1
                        self.checkpoint('revision_required')
                        if stalled>=2:raise ValueError('Two non-accepted attempts; strategy/quality decision required')
                        continue
                    stalled=0;previous=current
                    if not any(v=='fail' for v in current.values()):
                        self.checkpoint('awaiting_human_retest',candidate_digest=digest(self.target),evaluation=candidate,review=review)
                        return self.state
                self.checkpoint('budget_exhausted',reason='Cumulative repair-cycle limit reached; residual failures preserved')
            except subprocess.TimeoutExpired as e:self.checkpoint('budget_exhausted' if time.time()>=self.state['deadline'] else 'decision_required',reason='Command timeout: '+str(e))
            except TimeoutError as e:self.checkpoint('budget_exhausted',reason=str(e))
            except (Exception,KeyboardInterrupt) as e:self.checkpoint('decision_required',reason=str(e))
            return self.state


def analyze_topics(report,output):
    """Captured CoRA traces -> private failure inventory, NOT a semantic gold set."""
    report=Path(report).resolve();data=read(report);output=Path(output).resolve()
    if output.exists():raise ValueError('Analysis output is immutable')
    groups={};failed_sources=set()
    for run in data['runs']:
        failures=[o for o in run.get('outcomes',[]) if o.get('status') in {'schema_error','unsupported_quote','model_error','resolver_error'}]
        if run.get('status') in {'schema_error','model_error','resolver_error'}:failures.append({'status':run['status'],'reason':run.get('error','')})
        for item in failures:
            reason=item.get('reason','');key='source_grounding' if 'source' in reason.lower() or 'cited' in reason.lower() else item['status']
            groups.setdefault(key,[]).append({'sourceId':run['sourceId'],'runId':run.get('id'),'status':item['status'],'reason':reason,'stageNames':[s.get('stage') for s in run.get('stages',[])],'promptDigest':run.get('promptDigest'),'sourceDigest':run.get('sourceDigest')})
            failed_sources.add(run['sourceId'])
    result={'schema_version':1,'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest(),'source_count':len(data['runs']),'sources_with_errors':len(failed_sources),'groups':groups,'root_cause_proven':False,'semantic_quality_accepted':False,'next_action':'Reproduce on pinned sources; independently establish expected behavior before repair. Captured traces are diagnostic evidence, not gold labels.'}
    output.parent.mkdir(parents=True,exist_ok=True);save(output,result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('run');a.add_argument('--policy',required=True)
    a=sub.add_parser('analyze-topics');a.add_argument('--report',required=True);a.add_argument('--output',required=True)
    args=p.parse_args()
    result=Protocol(args.policy).run() if args.action=='run' else analyze_topics(args.report,args.output)
    print(json.dumps(result if args.action=='analyze-topics' else {k:result.get(k) for k in ['status','cycles','reason','candidate_digest','merge_authorized']},ensure_ascii=False))

if __name__=='__main__':main()
