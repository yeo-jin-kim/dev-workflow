"""CoRA subprocess evaluator adapter; imports no target packages.

Gold cases grade frozen explicit expectations. Real-source cases grade runtime
and grounding failures only, never semantic correctness of accepted topics.
"""
import argparse
import json
from pathlib import Path
import subprocess
from development_loop import digest, save
from quality_improvement import read, sha


def expected_cases(config):
    gold=read(config['gold']);manifest=read(config['manifest'])
    cases={'gold:'+c['id']:sha(c) for c in gold['cases']}
    for row in manifest['sources']:
        if not row.get('digest'):raise ValueError('Real sources must already have pinned digests')
        cases['runtime:'+row['id']]=sha({'source':row,'expectation':'Runtime v2: no processing/grounding errors; unresolved context or scope is deferred, not repaired or semantic gold'})
    additional=config.get('additional_context_fixtures',[])
    if not isinstance(additional,list) or any(not isinstance(p,str) for p in additional):raise ValueError('Additional contextual fixtures must be paths')
    if additional and not config.get('context_fixtures'):raise ValueError('Additional contextual fixtures require a primary fixture')
    contextual=[c for path in ([config['context_fixtures'],*additional] if config.get('context_fixtures') else []) for c in read(path)['cases']]
    cases.update({'context:'+c['id']:sha(c) for c in contextual})
    if len(cases)!=len(gold['cases'])+len(manifest['sources'])+len(contextual):raise ValueError('Duplicate evaluation case IDs')
    return cases


def convert(config,gold,real,source,contextual=None):
    expected=expected_cases(config);rows=[]
    runs={r['sourceId']:r for r in gold['runs']}
    for case in gold['goldEvaluation']:
        run=runs[case['id']]
        normal=run['status']=='completed' and not any(o['status'] in {'schema_error','model_error','unsupported_quote'} for o in run.get('outcomes',[]))
        if case.get('semanticVersion')==1:
            verdict=case.get('semanticStatus')
            if verdict not in {'pass','fail','needs_review'}:raise ValueError('Invalid semantic evaluation verdict')
            status=('deferred' if verdict=='needs_review' else verdict) if normal and not case['forbiddenCategoryPresent'] else 'fail'
        elif any(c.get('semanticTargets') for c in read(config['gold'])['cases']):
            raise ValueError('Semantic fixtures require semantic evaluation; exact fallback refused')
        else:
            good=normal and not case['forbiddenCategoryPresent'] and (case['exactMatch'] is True or case['exactMatch'] is None)
            status='pass' if good else 'fail'
        id_='gold:'+case['id'];rows.append({'id':id_,'expected_digest':expected[id_],'status':status})
    for run in real['runs']:
        good=run['status']=='completed' and not any(o['status'] in {'schema_error','model_error','resolver_error','unsupported_quote'} for o in run.get('outcomes',[]))
        unresolved=any(o.get('status') in {'needs_scope','interpretation_deferred','interpretation_revision_required'} for o in run.get('outcomes',[]))
        status='fail' if not good else 'deferred' if unresolved else 'pass'
        id_='runtime:'+run['sourceId'];rows.append({'id':id_,'expected_digest':expected[id_],'status':status})
    if config.get('context_fixtures'):
        if not isinstance(contextual,dict) or not isinstance(contextual.get('cases'),list):raise ValueError('Missing contextual evaluation coverage')
        for case in contextual['cases']:
            id_='context:'+case['id']
            if id_ not in expected:raise ValueError('Unknown contextual case')
            rows.append({'id':id_,'expected_digest':expected[id_],'status':'pass' if case.get('passed') is True else 'fail'})
    if len(rows)!=len(expected) or {r['id'] for r in rows}!=set(expected):raise ValueError('Native evaluation coverage missing/duplicated')
    identities=sorted({(s.get('completion',{}).get('llm_provider') or '',s.get('completion',{}).get('llm_model') or '') for report in [gold,real] for run in report['runs'] for s in run.get('stages',[]) if s.get('completion')})
    identities=sorted(set(identities)|{(c['semanticCompletion'].get('llm_provider') or '',c['semanticCompletion'].get('llm_model') or '') for c in gold['goldEvaluation'] if c.get('semanticCompletion')})
    if contextual:
        identities=sorted(set(identities)|{(t['completion'].get('llm_provider') or '',t['completion'].get('llm_model') or '') for c in contextual['cases'] for t in c.get('trace',[]) if t.get('completion')})
    return {'model_identity':[{'provider':p,'model':m} for p,m in identities],'schema_version':1,'source_digest':source,'dataset_digest':sha(expected),'cases':rows,'decision_requests':[],'semantic_quality_accepted':False,'limitations':['Real-source pass means no recorded processing/grounding failure; semantic quality still requires human review.','No-source output and deferrals are not real-source semantic gold. Positive frozen gold cases prevent universal empty output from passing the complete suite.']}


def evaluate(config,target,output):
    target,output=Path(target).resolve(),Path(output).resolve();source=digest(target)
    if (output/'step.json').exists():raise ValueError('Evaluation evidence is immutable')
    output.mkdir(parents=True,exist_ok=True)
    command=[config['python'],str(target/'tools/evaluate_topic_subjects.py'),'--soba-repo',config['soba_repo'],'--mlx-python',config['mlx_python']]
    import os
    env=dict(os.environ,PYTHONPATH=str(target/'src'))
    for name in ['gold','real']:
        args=command+['--database',str(output/(name+'.db')),'--output',str(output/(name+'.json'))]
        if name=='gold':args+=['--fixtures',config['gold']]
        else:
            local_manifest=output/'manifest.json';local_manifest.write_bytes(Path(config['manifest']).read_bytes())
            args+=['--snapshot',config['snapshot'],'--manifest',str(local_manifest),'--evidence-endpoint',config['evidence_endpoint']]
        with (output/(name+'.log')).open('w') as log:subprocess.run(args,cwd=target,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    contextual=None
    if config.get('context_fixtures'):
        cmd=[config['python'],str(target/'tools/evaluate_contextual_review.py'),'--fixtures',config['context_fixtures'],'--output',str(output/'context.json'),'--soba-repo',config['soba_repo'],'--mlx-python',config['mlx_python']]
        for fixture in config.get('additional_context_fixtures',[]):cmd+=['--additional-fixtures',fixture]
        with (output/'context.log').open('w') as log:subprocess.run(cmd,cwd=target,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        contextual=read(output/'context.json')
    if digest(target)!=source:raise ValueError('Target changed during evaluation')
    result=convert(config,read(output/'gold.json'),read(output/'real.json'),source,contextual)
    result['evidence']=[str(output/(name+'.json')) for name in (['gold','real','context'] if contextual else ['gold','real'])]
    save(output/'step.json',result);return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['freeze','evaluate']);p.add_argument('--config',required=True);p.add_argument('--target');p.add_argument('--output',required=True);p.add_argument('--input')
    args=p.parse_args();cfg=read(args.config)
    if args.action=='freeze':
        out=Path(args.output)
        if out.exists():raise ValueError('Frozen registry cannot be overwritten')
        save(out,{'cases':expected_cases(cfg),'semantic_authority':'Uses existing explicit gold labels; runtime expectations do not adopt semantic labels from model output'})
    else:
        if not args.target:p.error('Target required')
        evaluate(cfg,args.target,args.output)

if __name__=='__main__':main()
