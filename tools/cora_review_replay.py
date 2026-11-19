"""Wrap the target's native copy-only CLI with controller source/review bindings."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from delivery_evidence import manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['review','evidence','graph','snapshot']:p.add_argument('--'+key,required=True,type=Path)
    p.add_argument('--python',default=sys.executable)
    for key in ['model','soba-repo','mlx-python']:p.add_argument('--'+key,default='')
    p.add_argument('--revalidate-current',action='store_true');p.add_argument('--expected-graph-content',default='')
    args=p.parse_args();args.evidence.mkdir(parents=True,exist_ok=True,mode=0o700)
    target=Path.cwd();digest=manifest(target)['digest'];original=args.review.read_bytes()
    native=args.evidence/'native-replay.json';result=args.evidence/'review-replay.json'
    if native.exists() or result.exists():raise ValueError('Fresh replay output required.')
    command=[args.python,'-m','cora.recall.review_replay','--review',str(args.review),'--graph',str(args.graph),'--snapshot',str(args.snapshot),'--output',str(native)]
    for key in ['model','soba_repo','mlx_python']:
        if getattr(args,key):command+=['--'+key.replace('_','-'),getattr(args,key)]
    if args.revalidate_current:command+=['--revalidate-current','--expected-graph-content',args.expected_graph_content]
    import os
    process=subprocess.run(command,cwd=target,env={**os.environ,'PYTHONPATH':str(target/'src')},capture_output=True,text=True)
    if process.returncode:raise ValueError((process.stderr.strip().splitlines() or ['Native replay failed'])[-1][:1000])
    if manifest(target)['digest']!=digest or args.review.read_bytes()!=original:raise ValueError('Source or review changed during replay.')
    observation=json.loads(native.read_text());observation.update(target_digest=digest,selected_review_sha256=hashlib.sha256(original).hexdigest())
    with result.open('x') as stream:json.dump(observation,stream,ensure_ascii=False)
    result.chmod(0o600)


if __name__=='__main__':main()
