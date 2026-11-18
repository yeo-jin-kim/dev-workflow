"""Trusted adapter from a web review record to the bounded W2/W1 code runner."""
import argparse
from pathlib import Path
import review_intake as intake
from development_loop import save


def dispatch(notes,policy,output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False,mode=0o700)
    document={'schemaVersion':1,'records':[notes['reviewRecord']]}
    review=output/'review.json';intake.durable(review,document,exclusive=True)
    cfg,project,contract,files,authority=intake.policy_inputs(policy)
    record,_=intake.select_record(document)
    target=intake.version_guard(record,project,cfg)
    selected=output/'selected-baseline.json';intake.durable(selected,record,exclusive=True)
    from review_replay_gate import replay
    baseline=output/'baseline';baseline.mkdir(mode=0o700)
    command=[a.replace('{review}',str(selected)).replace('{evidence}',str(baseline)) for a in cfg['replay_check']]
    replay(target,selected,baseline,command)
    if intake.fingerprint(files)!=authority:raise ValueError('Answer authority changed during baseline replay.')
    receipt=intake.prepare(review,policy,baseline_observation=baseline/'review-replay.json')
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
        save(output/'receipt.json',receipt)
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--notes',required=True);p.add_argument('--policy',required=True);p.add_argument('--output',required=True)
    args=p.parse_args()
    try:dispatch(intake.strict_read(args.notes),args.policy,args.output)
    except Exception as e:
        folder=Path(args.output);folder.mkdir(parents=True,exist_ok=True,mode=0o700)
        save(folder/'receipt.json',{'phase':'decision_required','reason':str(e),'merge_authorized':False})
        return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
