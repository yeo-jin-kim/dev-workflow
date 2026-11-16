"""Loopback-only, durable review-note intake for fixed quality policies."""
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import tempfile
import threading
import time
from urllib.parse import urlsplit

import quality_workflow as q
from development_loop import execute, lock, save
from delivery_evidence import manifest


def plan_hash(plan):
    return hashlib.sha256(json.dumps({k:v for k,v in plan.items() if k!='plan_digest'},sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()


class Intake:
    def __init__(self, folder, policy):
        self.folder=Path(folder).resolve();self.policy=Path(policy).resolve()
        if not self.policy.is_relative_to(q.ROOT/'projects'):raise ValueError('Trusted projects/ policy required.')
        self.cfg=q.read(self.policy)
        if self.cfg.get('enabled') is not True or not self.cfg.get('authorization_reference'):raise ValueError('Enabled owner policy required.')
        if self.cfg.get('intake',{}).get('enabled') is not True:raise ValueError('Intake is disabled in trusted policy.')
        seconds=self.cfg.get('total_seconds',3600)
        if type(seconds) is not int or not 1<=seconds<=3600:raise ValueError('Invalid deadline.')
        if not self.folder.is_relative_to(q.ROOT/'.local'):raise ValueError('Review must be private external evidence.')
        self.plan=q.read(self.folder/'trial/plan.json')
        if plan_hash(self.plan)!=self.plan.get('plan_digest'):raise ValueError('Review plan digest is invalid.')
        if self.plan['node_id']!=self.cfg['node_id']:raise ValueError('Policy and reviewed node differ.')
        self.policy_hash=hashlib.sha256(self.policy.read_bytes()).hexdigest()
        self.source=manifest(Path(self.cfg['target']))['digest']
        self.contract=self.cfg['intake'].get('contract')
        contract_path=(q.ROOT/str(self.contract)).resolve()
        if not contract_path.is_relative_to(q.ROOT/'contracts'):raise ValueError('Trusted intake contract required.')
        self.contract_path=contract_path;self.contract_hash=hashlib.sha256(contract_path.read_bytes()).hexdigest()
        self.fixed=q.read(contract_path)
        maximum=self.fixed.get('limits',{}).get('total_seconds_max',3600)
        if type(maximum) is not int or not 1<=maximum<=3600 or seconds>maximum:raise ValueError('Policy exceeds the fixed contract deadline.')
        if self.fixed.get('production_apply_authorized') is not False:raise ValueError('Only copy-only contracts supported.')
        if self.fixed.get('repair_mode')!=self.cfg['intake'].get('repair_mode'):raise ValueError('Contract repair mode mismatch.')
        trial=self.cfg['commands']['trial'];mode=self.fixed['repair_mode']
        if trial.count('--repair-mode')!=1 or trial[trial.index('--repair-mode')+1]!=mode:raise ValueError('Trusted trial command must declare exact repair mode.')
        if trial.count('--expected-review')!=1 or trial[trial.index('--expected-review')+1]!='{run}/review-binding.json':raise ValueError('Trial must bind the exact reviewed graph and snapshot.')
        if 'repair_project' in self.cfg:raise ValueError('Intake currently supports fixed domain repair, not open code editing.')
        self.queue=q.ROOT/'.local/quality-requests';self.queue.mkdir(parents=True,exist_ok=True);self.queue.chmod(0o700)
        self.token=secrets.token_urlsafe(32);self.mutex=threading.Lock();self.wake=threading.Event();self.stop=threading.Event()

    def guard(self):
        if hashlib.sha256(self.policy.read_bytes()).hexdigest()!=self.policy_hash:raise ValueError('Trusted policy changed; restart and review again.')
        if hashlib.sha256(self.contract_path.read_bytes()).hexdigest()!=self.contract_hash:raise ValueError('Trusted contract changed; review again.')
        snapshot=(Path(self.cfg['target'])/self.cfg['snapshot']).resolve()
        if hashlib.sha256(snapshot.read_bytes()).hexdigest()!=self.plan['snapshot_sha256']:raise ValueError('Snapshot changed since review.')
        if plan_hash(q.read(self.folder/'trial/plan.json'))!=self.plan['plan_digest']:raise ValueError('Reviewed plan changed.')
        if manifest(Path(self.cfg['target']))['digest']!=self.source:raise ValueError('Target code changed; refresh review binding.')

    def accept(self, notes):
        if not isinstance(notes,dict) or notes.get('schemaVersion')!=1:raise ValueError('Expected schemaVersion 1.')
        if notes.get('decision')!='changes_requested':raise ValueError('Choose changes_requested to request a repair. Approval/application is not supported here.')
        if notes.get('planDigest')!=self.plan['plan_digest']:raise ValueError('Stale or wrong plan digest; refresh the review.')
        reason=notes.get('reason')
        if not isinstance(reason,str) or not 1<=len(reason.strip())<=8000:raise ValueError('A reason of 1–8000 characters is required.')
        record=notes.get('reviewRecord');scope=notes.get('repairScope','mixed_node')
        if scope not in {'mixed_node','recall_answer'}:raise ValueError('Unsupported request scope.')
        if 'repairScope' in notes and not isinstance(record,dict):raise ValueError('A completed Recall review is required.')
        if record is not None:
            context=record.get('context',{});response=record.get('response',{});request=record.get('request',{});review=record.get('review',{})
            if not all(isinstance(x,dict) for x in [context,response,request,review]):raise ValueError('Review context/request/response/judgment must be objects.')
            if context.get('snapshotSha256')!=self.plan['snapshot_sha256'] or context.get('graphSequence')!=self.plan['binding']['graph_sequence'] or response.get('retrieval',{}).get('graphSequence')!=self.plan['binding']['graph_sequence']:raise ValueError('Recall review uses a different graph/snapshot version; refresh and rerun it.')
            if not isinstance(request.get('query'),str) or not 1<=len(request['query'])<=4000 or not isinstance(response.get('answer'),dict) or review.get('decision')!='changes_requested' or review.get('reason')!=reason:raise ValueError('Completed question, answer and matching review required.')
        # Notes/response are data, never commands, scope expansion or approval.
        notes={k:notes[k] for k in ('schemaVersion','planDigest','decision','reason')}
        if record is not None:notes.update(reviewRecord=record,repairScope=scope)
        with self.mutex,lock(self.queue/'intake.lock'):
            self.guard()
            key=q.sha({'plan':self.plan['plan_digest'],'policy':self.policy_hash,'contract':self.contract_hash})
            if scope=='recall_answer':key=q.sha({'fixed_key':key,'request':record['request'],'record_id':record.get('id')})
            path=self.queue/(key+'.json')
            if path.exists():
                if record is not None:
                    attachments=self.queue/'review-context';attachments.mkdir(exist_ok=True);attachments.chmod(0o700)
                    attachment=attachments/(key+'-'+q.sha(record)+'.json')
                    if not attachment.exists():save(attachment,record);attachment.chmod(0o600)
                return q.read(path),True
            now=time.time()
            with tempfile.TemporaryDirectory(prefix='audit-',dir=self.queue) as td:
                output=Path(td)/'audit.json';args=[a.replace('{graph}',str(self.cfg['graph'])).replace('{run}',str(td)) for a in self.cfg['commands']['audit']]
                if execute(args,Path(self.cfg['target']),Path(td)/'audit.log',min(20,self.cfg.get('total_seconds',3600))) or q.read(output)['binding']!=self.plan['binding']:raise ValueError('Graph changed since review; regenerate review before submitting.')
            self.guard()
            r={'schema_version':1,'id':key,'status':'queued','created_at':now,'deadline':now+self.cfg.get('total_seconds',3600),'policy':str(self.policy),'policy_hash':self.policy_hash,'contract_hash':self.contract_hash,'source_digest':self.source,'binding':self.plan['binding'],'notes':notes,'production_apply_authorized':False,'review_folder':str(self.folder)}
            if scope=='recall_answer':r.update(status='decision_required',reason='답변·검색 수정 요청을 기록했습니다. 현재 자동 계약은 혼합 노드 제거만 허용하므로 별도 작업 범위 검토가 필요합니다.')
            save(path,r);path.chmod(0o600);self.wake.set();return r,False

    def get(self,key):
        if not re.fullmatch('[a-f0-9]{64}',key):raise ValueError('Invalid request ID.')
        r=q.read(self.queue/(key+'.json'))
        if r['policy_hash']!=self.policy_hash or r['review_folder']!=str(self.folder):raise ValueError('Request belongs to a different review.')
        return r

    def process(self,key):
        path=self.queue/(key+'.json')
        with lock(self.queue/(key+'.lock')):
            r=self.get(key)
            if r['status']!='queued':return r
            try:
                if r.get('contract_hash')!=self.contract_hash:raise ValueError('Queued request is bound to a previous contract; owner review required.')
                if r.get('source_digest')!=self.source:raise ValueError('Queued request is bound to previous target code; owner review required.')
                self.guard()
                if time.time()>=r['deadline']:raise ValueError('Original request deadline expired; no allowance reset.')
                r.update(status='running',started_at=time.time());save(path,r)
                out=self.queue/key
                receipt=q.run(self.policy,out,expected_binding=r['binding'],deadline_limit=r['deadline'],issue_evidence=r['notes'],expected_target=r['source_digest'],expected_snapshot=self.plan['snapshot_sha256'],authority_files={str(self.contract_path):self.contract_hash,str((Path(self.cfg['target'])/self.cfg['snapshot']).resolve()):self.plan['snapshot_sha256']})
                r.update(status=receipt['status'],run=str(out),ended_at=time.time())
            except Exception as e:
                r.update(status='decision_required',reason=str(e),ended_at=time.time())
            save(path,r);return r

    def worker(self):
        while not self.stop.is_set():
            for path in self.queue.glob('*.json'):
                try:
                    r=q.read(path)
                    if r.get('policy_hash')!=self.policy_hash or r.get('review_folder')!=str(self.folder):continue
                    if r.get('status')=='queued':self.process(r['id'])
                except (OSError,ValueError,KeyError):continue
            self.wake.wait(1);self.wake.clear()

    def recover(self):
        # Never restart an interrupted running repair or replenish its deadline.
        for path in self.queue.glob('*.json'):
            r=q.read(path)
            if r.get('policy_hash')==self.policy_hash and r.get('status')=='running':
                r.update(status='decision_required',reason='Service interrupted during execution; preserved artifacts require review.');save(path,r)




def make_server(intake,port):
    allowed={'':'index.html','plan.json':'plan.json','result.json':'result.json','recall-comparison.json':'recall-comparison.json'}
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup();self.connection.settimeout(5)
        def send_body(self,status,body,mime='application/json'):
            if not isinstance(body,bytes):body=json.dumps(body,ensure_ascii=False).encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY');self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(body)
        def secure(self,post=False):
            origin='http://127.0.0.1:'+str(self.server.server_port)
            if self.headers.get('Host')!=urlsplit(origin).netloc:raise PermissionError('Invalid Host.')
            if self.headers.get('Sec-Fetch-Site')=='cross-site':raise PermissionError('Cross-site request denied.')
            supplied=self.headers.get('Origin')
            if (supplied and supplied!=origin) or (post and supplied!=origin):raise PermissionError('Same-origin request required.')
            if post or self.path.startswith('/api/requests/'):
                if not hmac.compare_digest(self.headers.get('X-Review-Token',''),intake.token):raise PermissionError('Review session expired; refresh page.')
        def do_POST(self):
            try:
                self.secure(post=True)
                if self.path!='/api/requests':raise ValueError('Unknown endpoint.')
                if self.headers.get('Content-Type')!='application/json':raise ValueError('JSON content type required.')
                if self.headers.get('Transfer-Encoding'):raise ValueError('Chunked requests unsupported.')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=8388608:raise ValueError('Request must be 1–8388608 bytes.')
                r,duplicate=intake.accept(json.loads(self.rfile.read(size)))
                self.send_body(200 if duplicate else 202,{'id':r['id'],'status':r['status'],'duplicate':duplicate})
            except PermissionError as e:self.send_body(403,{'error':str(e)})
            except (ValueError,OSError,KeyError) as e:self.send_body(409,{'error':str(e)})
        def do_GET(self):
            try:
                self.secure()
                if self.path=='/':
                    matching=[q.read(p) for p in intake.queue.glob('*.json') if q.read(p).get('policy_hash')==intake.policy_hash and q.read(p).get('review_folder')==str(intake.folder)]
                    if matching:
                        latest=max(matching,key=lambda r:r.get('created_at',0));target=None
                        if latest.get('run') and (Path(latest['run'])/'trial/index.html').is_file():target='/results/'+latest['id']+'/'
                        elif latest['notes'].get('reviewRecord'):target='/feedback/'+latest['id']+'/'
                        if target:
                            self.send_response(302);self.send_header('Location',target);self.send_header('Cache-Control','no-store');self.send_header('Content-Length','0');self.end_headers();return
                if self.path=='/api/session':
                    matching=[q.read(p) for p in intake.queue.glob('*.json') if q.read(p).get('policy_hash')==intake.policy_hash and q.read(p).get('review_folder')==str(intake.folder)]
                    latest=max(matching,key=lambda r:r.get('created_at',0))['id'] if matching else None
                    self.send_body(200,{'token':intake.token,'planDigest':intake.plan['plan_digest'],'latestRequestId':latest});return
                if self.path.startswith('/api/requests/'):
                    r=intake.get(self.path.removeprefix('/api/requests/'));body={k:r[k] for k in ['id','status','deadline','production_apply_authorized']}
                    if 'reason' in r:body['reason']=r['reason']
                    run=Path(r['run']) if r.get('run') else intake.queue/r['id']
                    if (run/'receipt.json').is_file():
                        receipt=q.read(run/'receipt.json');body['phase']=receipt['status'] if receipt['status'] not in {'auditing'} else 'auditing'
                    if r['status'] not in {'queued','running'}:body.pop('phase',None)
                    if (run/'trial/index.html').is_file():body['resultUrl']='/results/'+r['id']+'/'
                    elif r['notes'].get('reviewRecord'):body['resultUrl']='/feedback/'+r['id']+'/'
                    self.send_body(200,body);return
                if self.path.startswith('/feedback/'):
                    from html import escape
                    parts=self.path.split('/')
                    if len(parts)!=4 or parts[3]:raise ValueError('Invalid receipt path.')
                    r=intake.get(parts[2]);record=r['notes'].get('reviewRecord')
                    if not record:raise ValueError('No Recall review attached.')
                    html='<meta charset="utf-8"><title>Recall review request</title><main style="max-width:960px;margin:30px auto;font:16px system-ui;line-height:1.7"><h1>Recall 수정 요청 접수 내역</h1><h2>검토한 질문</h2><p>'+escape(record['request']['query'])+'</p><h2>검토 당시 답변</h2><p>'+escape(record['response']['answer'].get('summary',''))+'</p><h2>요청한 수정</h2><p>'+escape(r['notes']['reason'])+'</p><h2>다음 판단</h2><p>'+escape(r.get('reason','작업 범위를 검토 중입니다.'))+'</p><p>아직 변경 후 답변이 없습니다. 원본 그래프는 변경하지 않았습니다.</p></main>'
                    review_url=getattr(intake,'review_url',None)
                    if review_url:html+='<a href="'+escape(review_url,quote=True)+'">Recall 검토 화면으로 돌아가기</a>'
                    self.send_body(200,html.encode(),'text/html; charset=utf-8');return
                if self.path=='/receipt.json':path=intake.folder/'receipt.json'
                elif self.path.startswith('/results/'):
                    parts=self.path.split('/')
                    if len(parts)!=4:raise ValueError('Invalid result path.')
                    r=intake.get(parts[2]);name=allowed.get(parts[3])
                    if name is None or not r.get('run'):raise ValueError('Result unavailable.')
                    path=Path(r['run'])/'trial'/name
                else:
                    name=allowed.get(self.path.lstrip('/'))
                    if name is None:raise ValueError('Unknown endpoint.')
                    path=intake.folder/'trial'/name
                if not path.resolve().is_relative_to(q.ROOT/'.local') or path.is_symlink() or not path.is_file():raise ValueError('Artifact unavailable.')
                body=path.read_bytes();mime='application/json'
                if path.suffix=='.html':
                    mime='text/html; charset=utf-8'
                    view=intake.queue.parent/'quality-views'/q.sha(str(path.parent))
                    if (view/'index.html').is_file() and q.read(view/'view-binding.json').get('plan_digest')==q.read(path.parent/'plan.json')['plan_digest']:body=(view/'index.html').read_bytes()
                    from html import escape
                    if self.path.startswith('/results/'):
                        record=r['notes'].get('reviewRecord')
                        if record:
                            body=('<section><h2>Submitted question / 제출한 질문</h2><p>'+escape(record['request']['query'])+'</p><h3>Answer at review / 검토 당시 답변</h3><p>'+escape(record['response']['answer'].get('summary',''))+'</p><p>'+escape(r['notes']['reason'])+'</p></section>').encode()+body
                        else:body='<p>This request predates question capture; no original-question replay is claimed. / 질문 연결 이전에 접수된 요청이므로, 당시 질문의 전후 비교를 제공할 수 없습니다.</p>'.encode()+body
                    review_url=getattr(intake,'review_url',None) or intake.cfg.get('intake',{}).get('review_url')
                    if review_url:body=('<nav><a href="'+escape(review_url,quote=True)+'">Back to Recall review / Recall 검토로 돌아가기</a></nav>').encode()+body
                self.send_body(200,body,mime)
            except PermissionError as e:self.send_body(403,{'error':str(e)})
            except (ValueError,OSError,KeyError) as e:self.send_body(404,{'error':str(e)})
        def log_message(self,*args):pass
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def serve_intake(folder,port,policy,review_url=None):
    intake=Intake(folder,policy)
    if review_url:
        u=urlsplit(review_url)
        if u.scheme!='http' or u.hostname!='127.0.0.1' or not u.port or u.username or u.password or u.query or u.fragment:raise ValueError('Review URL must be a loopback page.')
    intake.review_url=review_url
    # One service owns the queue; another server cannot recover a live worker.
    with lock(intake.queue/'service.lock'):
        intake.recover();server=make_server(intake,port)
        threading.Thread(target=intake.worker,daemon=True).start()
        print('Review intake: http://127.0.0.1:'+str(server.server_port),flush=True)
        try:server.serve_forever()
        finally:intake.stop.set();intake.wake.set();server.server_close()
