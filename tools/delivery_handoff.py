"""Private revision-bound comparisons, human retest, merge and regression cases."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from development_loop import effective_contract, lock, save
from delivery_publish import repository_identity

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True, stderr=subprocess.STDOUT, timeout=60).strip()


def private(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT / '.local'):
        raise ValueError('Handoff evidence must remain in controller .local/.')
    return path


def ready(report):
    review, ci = report.get('review') or {}, report.get('ci') or {}
    criteria = review.get('criteria') or []
    identity=report.get('identity') or {}
    report_id=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    coherent=(bool(identity) and report.get('report_id')==report_id
              and all(identity.get(k)==report.get(v) for k,v in [('status','status'),('head','source_sha'),('base','target_sha'),('contents','reviewed_digest'),('review','review'),('ci','ci')]))
    return (coherent and bool(ci.get('gates')) and all(g.get('passed') is True for g in ci['gates'])
            and report.get('status') == 'ready_for_merge_approval'
            and review.get('verdict') == 'pass' and not review.get('blocking_findings')
            and not review.get('decision_requests') and bool(criteria)
            and all(x.get('passed') is True for x in criteria)
            and ci.get('status') == 'success' and ci.get('head') == report.get('source_sha')
            and ci.get('base') == report.get('target_sha'))


def validate_report(path, report):
    """Require matching controller state and raw execution/review receipts."""
    path=private(path);state_path=private(path.parent.parent/'state.json');state=read(state_path)
    if (private(state.get('report','')) != path or state.get('status')!='ready_for_merge_approval'
            or state.get('run_id')!=report.get('identity',{}).get('run_id')
            or state.get('published_sha')!=report.get('source_sha')
            or state.get('base_sha')!=report.get('target_sha')
            or state.get('accepted_digest')!=report.get('reviewed_digest')
            or state.get('last_review')!=report.get('review') or state.get('last_ci')!=report.get('ci')):
        raise ValueError('Report does not match controller delivery state.')
    proof=[state_path]
    verification=report.get('verification') or []
    if not verification:raise ValueError('Raw verification receipts required.')
    last=verification[-1];attempt=private(last['evidence_directory'])
    if attempt.parent!=state_path.parent:raise ValueError('Verification is outside the recorded run.')
    review_path=attempt/'review.json'
    if read(review_path)!=report['review']:raise ValueError('Independent review receipt differs.')
    checks=last.get('checks') or []
    raw=sorted(attempt.glob('check-*-execution.json'))
    if not checks or [read(p) for p in raw]!=checks or any(c.get('exit_code')!=0 or c.get('input_digest')!=report['reviewed_digest'] for c in checks):
        raise ValueError('Passing source-bound check receipts required.')
    proof.extend([review_path,*raw])
    protected=state.get('controls',{}).get('protected',{})
    projects=[]
    for name, expected_hash in protected.items():
        candidate=Path(name).resolve()
        if candidate.suffix!='.json' or not candidate.is_relative_to(ROOT):continue
        cfg=read(candidate)
        if isinstance(cfg,dict) and cfg.get('schema_version')==2 and cfg.get('root')==state.get('target') and cfg.get('delivery',{}).get('head')==report['source_branch']:
            task_contract=effective_contract(read((ROOT/cfg['contract']).resolve()))
            if {c['id'] for c in task_contract.get('criteria',[])}=={c['id'] for c in report['review']['criteria']}:projects.append((candidate,cfg,expected_hash))
    if len(projects)!=1:raise ValueError('Pinned trusted task project required.')
    project,cfg,expected_hash=projects[0];contract_path=(ROOT/cfg['contract']).resolve();contract=effective_contract(read(contract_path))
    for p,expected_hash in [(project,expected_hash),(contract_path,protected.get(str(contract_path)))]:
        if not expected_hash or hashlib.sha256(p.read_bytes()).hexdigest()!=expected_hash:raise ValueError('Task authority changed after verification.')
    delivery=cfg['delivery']
    if delivery.get('base')!=report['target_branch'] or delivery.get('repository')!=report['repository'] or len(contract.get('checks',[]))!=len(raw):
        raise ValueError('Report task policy/check count differs.')
    required=delivery.get('required_gates') or []
    if not required or len(report['ci'].get('gates',[]))!=len(required) or any(not any(g.get('gate')==gate and g.get('passed') is True for g in report['ci']['gates']) for gate in required):raise ValueError('Configured CI gates are missing.')
    actual_criteria={c['id'] for c in report['review']['criteria'] if c.get('passed') is True}
    if any(c['id'] not in actual_criteria for c in contract.get('criteria',[])):raise ValueError('Configured review criteria are missing.')
    if cfg.get('browser'):
        from approved_queue import verify_browser
        verify_browser(attempt,cfg['browser'],report['reviewed_digest'],last.get('browser'))
        proof.extend(p for p in attempt.glob('browser*') if p.is_file())
    proof.extend([project,contract_path])
    return proof


def register(report_path, review_path, observation_path, folder, *, historical_only=False):
    """Called by the controller after verified publication; never by review notes."""
    report_path, review_path, observation_path = map(private, (report_path, review_path, observation_path))
    report, record, observation = map(read, (report_path, review_path, observation_path))
    if 'records' in record:raise ValueError('An exact selected-record file, not an export envelope, is required.')
    from review_replay_gate import validate_observation
    validate_observation(observation,record,review_path.read_bytes(),report.get('reviewed_digest'))
    proof=[];proof_issue=None
    try:proof=validate_report(report_path,report)
    except (ValueError,OSError,KeyError) as error:
        if not historical_only:raise
        proof_issue=str(error)
    if not ready(report):
        raise ValueError('Passing exact-revision review and CI required.')
    if observation.get('target_digest') != report.get('reviewed_digest'):
        raise ValueError('Candidate replay differs from independently reviewed contents.')
    if observation.get('replayed_request') != record['request']:
        raise ValueError('Candidate replay used a different request.')
    if observation.get('snapshot_sha256') != record['context']['snapshotSha256']:
        raise ValueError('Candidate replay used a different snapshot.')
    graph = record['context'].get('graphContentSha256')
    if graph and observation.get('graph_content_sha256') != graph:
        raise ValueError('Candidate replay used a different graph.')
    regressions=check_registry(observation,folder)
    body = {'schema_version': 2, 'historical_only':historical_only,'proof_issue':proof_issue,'report_path':str(report_path),'review_path':str(review_path),'observation_path':str(observation_path),'report': report, 'review': record, 'regressions':regressions,
            'candidate': observation, 'artifacts': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                                   for p in (report_path, review_path, observation_path,*proof)}}
    body['id'] = digest(body)
    folder = private(folder);folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = folder / (body['id'] + '.json')
    if path.exists():
        if read(path) != body:raise ValueError('Immutable handoff differs.')
    else:
        save(path, body);path.chmod(0o600)
    return path


def verify(path):
    path = private(path);packet = read(path)
    if packet.get('schema_version')!=2:raise ValueError('Legacy handoff requires registration with raw proof files.')
    if digest({k:v for k,v in packet.items() if k != 'id'}) != packet['id']:
        raise ValueError('Handoff contents changed.')
    for name, expected in packet['artifacts'].items():
        artifact=Path(name).resolve()
        if not any(artifact.is_relative_to(ROOT/d) for d in ('.local','projects','contracts')):raise ValueError('Evidence is outside trusted controller locations.')
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != expected:
            raise ValueError('Bound evidence changed; revalidation required.')
    if not ready(packet['report']):raise ValueError('Handoff gates do not pass.')
    if not packet.get('historical_only'):validate_report(packet['report_path'],packet['report'])
    from review_replay_gate import validate_observation
    validate_observation(packet['candidate'],packet['review'],private(packet['review_path']).read_bytes(),packet['report']['reviewed_digest'])
    return packet


def retest(path, decision, reason):
    if decision not in {'pass', 'changes_requested', 'hold'} or not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 8000:
        raise ValueError('Choose a decision and enter a reason (1–8000 characters).')
    path = private(path);packet = verify(path)
    if packet.get('historical_only'):raise ValueError('Historical comparison cannot authorize retest acceptance or merge.')
    with lock(path.with_suffix('.lock')):
        entry = {'handoff_id':packet['id'], 'source_sha':packet['report']['source_sha'],
                 'decision':decision, 'reason':reason, 'time':time.time(),
                 'authority':'Local human retest notes; separate operator merge authorization required.'}
        history = path.parent / (packet['id'] + '-retests');history.mkdir(exist_ok=True, mode=0o700)
        save(history / (str(time.time_ns()) + '.json'), entry)
        save(path.with_suffix('.retest.json'), entry)
    return entry


def remote(root, branch):
    git(root, 'check-ref-format', 'refs/heads/' + branch)
    lines = git(root, 'ls-remote', 'origin', 'refs/heads/' + branch).splitlines()
    if len(lines) != 1:raise ValueError('Remote branch unavailable.')
    return lines[0].split()[0]


def authorize(path, root, reference, checks, output=None):
    """Operator attestation of an actual owner decision; not human authentication."""
    path=private(path);packet=verify(path);root=Path(root).resolve()
    if packet.get('historical_only'):raise ValueError('Historical comparison cannot authorize merge.')
    if not isinstance(reference,str) or not reference.strip():raise ValueError('Actual owner decision reference required.')
    if not isinstance(checks,list) or not checks or len(checks)>16 or any(not isinstance(c,list) or not c or any(not isinstance(a,str) for a in c) for c in checks):
        raise ValueError('Trusted check argv arrays required.')
    report=packet['report']
    approval={'schema_version':1,'enabled':True,'decision':'approve_exact_merge','handoff_id':packet['id'],
              'source_sha':report['source_sha'],'target_sha':report['target_sha'],'repository':report['repository'],
              'target_branch':report['target_branch'],'target_root':str(root),'checks':checks,'authorization_reference':reference}
    output=Path(output or ROOT/'projects/.local/merge-approvals'/(packet['id']+'.json')).resolve()
    if not output.is_relative_to(ROOT/'projects'):raise ValueError('Operator approval must be under trusted projects/.')
    output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with lock(path.with_suffix('.lock')):
        if output.exists():
            if read(output)!=approval:raise ValueError('Owner approval is immutable; select a new record.')
        else:
            with output.open('x') as stream:json.dump(approval,stream,ensure_ascii=False,indent=2)
            output.chmod(0o600)
    return output


def merge(path, root, approval_path, push=True):
    """Explicit operator-only action. No web request can call this function."""
    path = private(path);root = Path(root).resolve();packet = verify(path);report = packet['report']
    if packet.get('historical_only'):raise ValueError('Historical comparison cannot authorize merge.')
    approval_path=Path(approval_path).resolve()
    if not approval_path.is_relative_to(ROOT/'projects'):raise ValueError('Trusted revision-bound owner approval required.')
    approval=read(approval_path);approval_hash=hashlib.sha256(approval_path.read_bytes()).hexdigest()
    expected={'schema_version':1,'enabled':True,'decision':'approve_exact_merge','handoff_id':packet['id'],
              'source_sha':report['source_sha'],'target_sha':report['target_sha'],'repository':report['repository'],
              'target_branch':report['target_branch'],'target_root':str(root)}
    if any(approval.get(k)!=v for k,v in expected.items()) or not approval.get('authorization_reference'):
        raise ValueError('Owner approval belongs to a different revision or target.')
    checks=approval.get('checks')
    if not isinstance(checks,list) or not checks or len(checks)>16 or any(not isinstance(c,list) or not c or any(not isinstance(a,str) for a in c) for c in checks):
        raise ValueError('Trusted check argv arrays required.')
    for field in ('source_sha','target_sha'):
        if not re.fullmatch('[a-f0-9]{40}',report[field]):raise ValueError('Full commit identities required.')
    with lock(path.with_suffix('.lock')):
        receipt_path = path.with_suffix('.merge.json')
        if receipt_path.exists():raise ValueError('Merge already attempted; inspect its receipt, never silently retry.')
        from delivery_evidence import manifest, fingerprint
        state=read(private(packet['report_path']).parent.parent/'state.json')
        controls=state.get('controls',{})
        if controls.get('controller')!=manifest(ROOT)['digest'] or fingerprint([Path(p) for p in controls.get('protected',{})])!=controls.get('protected'):
            raise ValueError('Controller/task authority changed; revalidation required.')
        check_registry(packet['candidate'],path.parent)
        human = read(path.with_suffix('.retest.json'))
        if human.get('decision') != 'pass' or human.get('handoff_id') != packet['id'] or human.get('source_sha') != report['source_sha']:
            raise ValueError('Passing human retest for this exact candidate required.')
        if git(root, 'status', '--porcelain') or git(root, 'branch', '--show-current') != report['target_branch']:
            raise ValueError('Clean checkout of recorded target branch required.')
        if repository_identity(git(root, 'remote', 'get-url', 'origin')) != report['repository']:
            raise ValueError('Repository identity differs.')
        if git(root, 'rev-parse', 'HEAD') != report['target_sha'] or remote(root, report['target_branch']) != report['target_sha'] or remote(root, report['source_branch']) != report['source_sha']:
            raise ValueError('Candidate or target moved; revalidation required.')
        git(root, 'fetch', 'origin', report['source_branch'])
        if git(root, 'merge-base', report['target_sha'], report['source_sha']) != report['target_sha']:
            raise ValueError('Candidate does not descend from the reviewed target.')
        receipt = {'handoff_id':packet['id'], 'approval':str(approval_path), 'approval_sha256':approval_hash, 'status':'merging',
                   'source_sha':report['source_sha'], 'target_sha':report['target_sha'], 'checks':[]}
        save(receipt_path, receipt)
        deadline=time.monotonic()+3600
        try:
            git(root, 'merge', '--no-ff', report['source_sha'], '-m', 'Merge owner-reviewed candidate ' + report['source_sha'])
            receipt['merged_sha'] = git(root, 'rev-parse', 'HEAD')
            if git(root, 'rev-parse', 'HEAD^{tree}') != git(root, 'rev-parse', report['source_sha'] + '^{tree}'):
                raise ValueError('Merged contents differ from reviewed candidate.')
            for command in checks:
                if time.monotonic()>=deadline:raise ValueError('Post-merge check allowance exhausted; no push.')
                result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=max(.01,min(600,deadline-time.monotonic())))
                receipt['checks'].append({'argv':command, 'returncode':result.returncode,
                                          'stdout':result.stdout, 'stderr':result.stderr})
                save(receipt_path, receipt)
                if result.returncode:raise ValueError('Post-merge check failed; local merge preserved, no push.')
            if git(root, 'status', '--porcelain') or git(root, 'rev-parse', 'HEAD') != receipt['merged_sha']:
                raise ValueError('Checks changed the target; no push.')
            if remote(root, report['source_branch']) != report['source_sha'] or remote(root, report['target_branch']) != report['target_sha']:
                raise ValueError('Remote moved during validation; no push.')
            if hashlib.sha256(approval_path.read_bytes()).hexdigest()!=approval_hash:
                raise ValueError('Owner approval changed during validation; no push.')
            verify(path)
            receipt['status'] = 'verified_local_merge'
            if push:
                git(root, 'push', 'origin', 'HEAD:refs/heads/' + report['target_branch'])
                if remote(root,report['target_branch']) != receipt['merged_sha']:raise ValueError('Remote verification failed.')
                receipt['status'] = 'merged_and_pushed'
        except Exception as exc:
            receipt.update(status='decision_required', reason=str(exc));save(receipt_path,receipt);raise
        save(receipt_path,receipt)
        return receipt


def inspect_integration(path, root):
    """Read-only reconciliation for candidates merged outside this helper."""
    path = private(path);packet = verify(path);report = packet['report'];root = Path(root).resolve()
    if repository_identity(git(root,'remote','get-url','origin')) != report['repository']:
        raise ValueError('Repository identity differs.')
    target = remote(root,report['target_branch'])
    git(root,'fetch','origin',report['target_branch'])
    result = subprocess.run(['git','merge-base','--is-ancestor',report['source_sha'],target],cwd=root,capture_output=True)
    if result.returncode not in (0,1):raise ValueError('Cannot inspect candidate ancestry.')
    status = 'already_integrated' if result.returncode == 0 else ('awaiting_human_retest' if target == report['target_sha'] else 'stale_target_requires_revalidation')
    receipt = {'status':status,'source_sha':report['source_sha'],'observed_target_sha':target,
               'time':time.time(),'authority':'Read-only Git ancestry observation; not a new merge or semantic review.'}
    with lock(path.with_suffix('.lock')):save(path.with_suffix('.integration.json'),receipt)
    return receipt


def preserve_case(path, required_claims, forbidden_claims):
    """Human-selected assertions, not an automatic gold answer copied from a model."""
    path = private(path);packet = verify(path)
    if packet.get('historical_only'):raise ValueError('Historical comparison cannot create accepted regression cases.')
    human = read(path.with_suffix('.retest.json'))
    if human.get('decision') != 'pass' or human.get('handoff_id') != packet['id']:
        raise ValueError('Passing human retest required before preserving a case.')
    if not required_claims and not forbidden_claims:raise ValueError('Explicit claim assertions required.')
    if set(required_claims) & set(forbidden_claims):raise ValueError('Contradictory assertions.')
    case = {'schema_version':1, 'handoff_id':packet['id'], 'request':packet['review']['request'],
            'context':packet['review']['context'], 'selected_review':packet['review'],
            'origin_source_sha':packet['report']['source_sha'], 'origin_source_digest':packet['report']['reviewed_digest'], 'required_claims':required_claims,
            'forbidden_claims':forbidden_claims, 'human_retest':human,
            'authority':'Owner-selected regression assertions; not general semantic correctness.'}
    check_case(case, packet['candidate'])
    dest = path.parent / (packet['id'] + '.case.json')
    with lock(path.with_suffix('.lock')):
        if dest.exists() and read(dest) != case:raise ValueError('Existing regression case differs; preserve it and create a revised handoff.')
        save(dest,case);dest.chmod(0o600)
    return dest


def check_case(case, observed):
    if observed.get('replayed_request') != case['request'] or observed.get('snapshot_sha256') != case['context']['snapshotSha256']:
        raise ValueError('Regression input binding differs.')
    graph = case['context'].get('graphContentSha256')
    if graph and observed.get('graph_content_sha256') != graph:raise ValueError('Regression graph differs.')
    claims = observed['response']['answer'].get('claims', [])
    ids = {c.get('claimId') for c in claims}
    if not set(case['required_claims']) <= ids or set(case['forbidden_claims']) & ids:
        raise ValueError('Regression participant assertions failed.')
    return {'status':'passed', 'required_claims':case['required_claims'], 'forbidden_claims':case['forbidden_claims']}


def check_registry(observed, folder):
    results = []
    folder = private(folder)
    for path in sorted(folder.glob('*.case.json')):
        case = read(path)
        # Different inputs are not silently treated as equivalent regressions.
        if case['request'] != observed.get('replayed_request') or case['context']['snapshotSha256'] != observed.get('snapshot_sha256'):
            results.append({'case':path.name,'status':'not_applicable'});continue
        result = check_case(case, observed)
        results.append({'case':path.name,**result})
    return results


def run_case(case_path, root, command, output, *, expected_head):
    """Execute an operator-selected trusted replay; require fresh source-bound evidence."""
    from delivery_evidence import manifest
    case_path=private(case_path);case_bytes=case_path.read_bytes();case = json.loads(case_bytes);output = private(output)
    if output.exists():raise ValueError('Regression output must be fresh.')
    output.mkdir(parents=True, mode=0o700);root = Path(root).resolve()
    head=git(root,'rev-parse','HEAD')
    if head!=expected_head or git(root,'status','--porcelain'):raise ValueError('Expected clean regression source revision required.')
    before = manifest(root)['digest']
    selected=output/'selected.json';save(selected,case['selected_review']);selected_bytes=selected.read_bytes()
    if not all(any(token in a for a in command) for token in ('{output}','{review}')):raise ValueError('Trusted replay must bind {output} and {review}.')
    argv = [a.replace('{output}',str(output)).replace('{review}',str(selected)) for a in command]
    result = subprocess.run(argv,cwd=root,capture_output=True,text=True,timeout=600)
    save(output/'execution.json',{'target':str(root),'head':head,'target_digest':before,'case_sha256':hashlib.sha256(case_bytes).hexdigest(),'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode:raise ValueError('Trusted regression replay failed.')
    artifact=output/'review-replay.json'
    if artifact.is_symlink() or not artifact.is_file() or artifact.stat().st_size>32*1024*1024:
        raise ValueError('Regression must produce a fresh regular observation file (up to 32 MiB).')
    observed = read(artifact)
    if git(root,'rev-parse','HEAD')!=head or git(root,'status','--porcelain') or manifest(root)['digest']!=before or case_path.read_bytes()!=case_bytes or selected.read_bytes()!=selected_bytes:raise ValueError('Regression source/input binding differs.')
    from review_replay_gate import validate_observation
    validate_observation(observed,case['selected_review'],selected_bytes,before)
    verdict = check_case(case,observed);save(output/'verdict.json',verdict);return verdict


def main():
    p = argparse.ArgumentParser(description=__doc__);s = p.add_subparsers(dest='action',required=True)
    r=s.add_parser('register');r.add_argument('--report',required=True);r.add_argument('--review',required=True);r.add_argument('--observation',required=True);r.add_argument('--folder',default=str(ROOT/'.local/handoffs'));r.add_argument('--historical-only',action='store_true')
    r=s.add_parser('retest');r.add_argument('--packet',required=True);r.add_argument('--decision',choices=['pass','changes_requested','hold'],required=True);r.add_argument('--reason',required=True)
    r=s.add_parser('merge');r.add_argument('--packet',required=True);r.add_argument('--target',required=True);r.add_argument('--approval',required=True);r.add_argument('--no-push',action='store_true')
    r=s.add_parser('authorize');r.add_argument('--packet',required=True);r.add_argument('--target',required=True);r.add_argument('--reference',required=True);r.add_argument('--checks',required=True);r.add_argument('--output')
    r=s.add_parser('inspect');r.add_argument('--packet',required=True);r.add_argument('--target',required=True)
    r=s.add_parser('preserve');r.add_argument('--packet',required=True);r.add_argument('--required',nargs='*',default=[]);r.add_argument('--forbidden',nargs='*',default=[])
    r=s.add_parser('regression');r.add_argument('--case',required=True);r.add_argument('--target',required=True);r.add_argument('--command',required=True,help='Trusted JSON argv with {output} and {review}');r.add_argument('--expected-head',required=True);r.add_argument('--output',required=True)
    a=p.parse_args()
    if a.action=='register':print(register(a.report,a.review,a.observation,a.folder,historical_only=a.historical_only))
    elif a.action=='retest':print(json.dumps(retest(a.packet,a.decision,a.reason),ensure_ascii=False))
    elif a.action=='merge':print(json.dumps(merge(a.packet,a.target,a.approval,not a.no_push),ensure_ascii=False))
    elif a.action=='authorize':print(authorize(a.packet,a.target,a.reference,read(a.checks),a.output))
    elif a.action=='inspect':print(json.dumps(inspect_integration(a.packet,a.target)))
    elif a.action=='preserve':print(preserve_case(a.packet,a.required,a.forbidden))
    elif a.action=='regression':print(json.dumps(run_case(a.case,a.target,read(a.command),a.output,expected_head=a.expected_head)))


if __name__ == '__main__':main()
