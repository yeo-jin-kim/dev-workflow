"""Trusted adapter from a web review record to the bounded W2/W1 code runner."""
import argparse
import copy
import time
from pathlib import Path
import review_intake as intake
from development_loop import save


def dispatch(notes,policy,output,deadline=None):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False,mode=0o700)
    document={'schemaVersion':1,'records':[notes['reviewRecord']]}
    review=output/'review.json';intake.durable(review,document,exclusive=True)
    cfg,project,contract,files,authority=intake.policy_inputs(policy)
    record,_=intake.select_record(document)
    revalidate=cfg.get('allow_stale_revalidation') is True
    target=(intake.ROOT/project['root']).resolve() if revalidate else intake.version_guard(record,project,cfg)
    if revalidate and intake.git(target,'status','--porcelain'):raise ValueError('Current replay target is dirty; preserve candidate and request a decision.')
    selected=output/'selected-baseline.json';intake.durable(selected,record,exclusive=True)
    from review_replay_gate import replay
    baseline=output/'baseline';baseline.mkdir(mode=0o700)
    save(output/'receipt.json',{'phase':'revalidating' if revalidate else 'replaying','original_commit':record['context']['frontendCommit'],'merge_authorized':False})
    command=[a.replace('{review}',str(selected)).replace('{evidence}',str(baseline)) for a in cfg['replay_check']]
    if revalidate:
        binding=intake.strict_read(cfg['revalidation_binding'])
        if notes.get('planDigest')!=binding['plan_digest'] or record['context']['snapshotSha256']!=binding['snapshot_sha256'] or record['response']['retrieval']['graphSequence']!=binding['binding']['graph_sequence']:
            raise ValueError('Original review is not bound to the trusted graph/snapshot plan.')
        command+=['--revalidate-current','--expected-graph-content',binding['binding']['graph_digest']]
    observed=replay(target,selected,baseline,command)
    original_review=None
    if revalidate:
        current=observed.get('current_context')
        if not isinstance(current,dict):raise ValueError('Current-version replay context missing.')
        derived=copy.deepcopy(record);derived.update(context=current,response=observed['response'])
        derived['review'].update(currentResponseHumanReviewed=False,provenance='Inherited issue report; current answer is an automated observation, not a new human judgment.')
        derived['revalidatedFrom']={'review_sha256':intake.sha(record),'originalCommit':record['context']['frontendCommit'],'historicalProviderKnown':bool(record['context'].get('answerProviderIdentity'))}
        intake.version_guard(derived,project,cfg)
        original_review=review
        review=output/'current-review.json';intake.durable(review,{'schemaVersion':1,'records':[derived]},exclusive=True)
        record=derived

    if intake.fingerprint(files)!=authority:raise ValueError('Answer authority changed during baseline replay.')
    receipt=intake.prepare(review,policy,baseline_observation=baseline/'review-replay.json',original_review=original_review,seconds_limit=max(1,int(deadline-time.time())) if deadline else None)
    save(output/'receipt.json',receipt)
    if receipt['phase']=='prepared':
        receipt=intake.run(receipt['id'])
        if receipt['phase']=='awaiting_human_retest':
            state=Path(receipt['state_dir'])/'tasks/repair/state.json'
            candidate=intake.strict_read(state);digest=candidate.get('accepted_digest')
            matches=[]
            for path in state.parent.rglob('review-replay.json'):
                observed=intake.strict_read(path)
                if observed.get('target_digest')==digest and observed.get('replayed_request')==record['request']:
                    matches.append((path,observed))
            if not matches:raise ValueError('Accepted candidate has no bound replay observation.')
            path,observed=matches[-1]
            receipt['comparison']={'answer':observed['response']['answer']['summary'],'observation':str(path),'candidate_digest':digest,'baseline_observation':str(baseline/'review-replay.json'),'human_retest_required':True}
        if receipt['phase']=='decision_required':
            state_path=Path(receipt.get('state_dir',output))/'tasks/repair/state.json'
            if state_path.is_file():
                worker=intake.strict_read(state_path)
                receipt['worker_status']=worker.get('status')
                receipt['reason']='; '.join(worker.get('decision_requests') or []) or worker.get('handoff',{}).get('reason') or worker.get('status','Worker requires a decision.')
            else:receipt['reason']=receipt.get('handoff',{}).get('engine',{}).get('reason','Execution requires a decision.')
        save(output/'receipt.json',receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--notes',required=True);p.add_argument('--policy',required=True);p.add_argument('--output',required=True);p.add_argument('--deadline',type=float)
    args=p.parse_args()
    try:dispatch(intake.strict_read(args.notes),args.policy,args.output,deadline=args.deadline)
    except Exception as e:
        folder=Path(args.output);folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        save(folder/'receipt.json',{'phase':'decision_required','reason':str(e),'merge_authorized':False})
        return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
