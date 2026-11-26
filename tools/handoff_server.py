"""Loopback review console. Browser notes cannot authorize merges or execute commands."""
import argparse
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
from urllib.parse import urlsplit
import delivery_handoff as h


def item(folder, key):
    if not re.fullmatch('[a-f0-9]{64}',key):raise ValueError('Invalid item ID.')
    path=folder/(key+'.json');packet=h.verify(path);report=packet['report']
    result={'id':key,'query':packet['review']['request']['query'],'reason':packet['review']['review']['reason'],
            'status':'awaiting_human_retest','before':packet['review']['response'],
            'after':packet['candidate']['response'],'report':report,'canRetest':True,'regressions':packet.get('regressions',[]),'binding':{'sourceSha':report['source_sha'],'snapshotSha':packet['candidate']['snapshot_sha256'],'graphContentSha':packet['candidate'].get('graph_content_sha256')}}
    if packet.get('historical_only'):
        result.update(status='historical_comparison_only',canRetest=False,proofIssue=packet.get('proof_issue'))
    for suffix,name in [('.retest.json','retest'),('.merge.json','merge'),('.case.json','case'),('.integration.json','integration')]:
        p=path.with_suffix(suffix)
        if p.exists():result[name]=h.read(p)
    if result.get('integration') and result['integration']['status'] != 'awaiting_human_retest':
        result['status']=result['integration']['status'];result['canRetest']=False
    elif result.get('merge'):result['status']=result['merge']['status']
    elif result.get('retest'):result['status']='awaiting_owner_merge_authorization' if result['retest']['decision']=='pass' else result['retest']['decision']
    return result


def queued_items(queue):
    result=[]
    if not queue.exists():return result
    for path in queue.glob('*.json'):
        if not re.fullmatch('[a-f0-9]{64}',path.stem):continue
        r=h.read(path);record=r.get('notes',{}).get('reviewRecord')
        if not record:continue
        status=r.get('status','unknown');reason=r.get('reason','')
        after=current=None
        if r.get('run'):
            run=h.private(r['run']);receipt=run/'receipt.json'
            if receipt.exists():
                outcome=h.read(receipt);status=outcome.get('phase',status)
                comparison=outcome.get('comparison',{})
                if comparison.get('observation'):after=h.read(h.private(comparison['observation'])).get('response')
                if (run/'current-review.json').exists():current=h.read(run/'current-review.json')['records'][0]['response']
                # State is owned by the existing bounded runner; never resume it here.
                progress=outcome
                if r.get('answer_policy') and r.get('status')=='running' and outcome.get('id'):
                    import review_intake as ri
                    journal=ri.locations(outcome['id'])[1]
                    if journal.exists():progress=h.read(h.private(journal))
                if progress.get('state_dir') and r.get('status')=='running':
                    state=h.private(progress['state_dir'])/'tasks/repair/state.json'
                    if state.exists():status=h.read(state).get('status',status)
        result.append({'id':path.stem,'query':record['request']['query'],'reason':reason,'status':status,
                       'before':record['response'],'after':after,'current':current,'canRetest':False})
    return result


def make_server(folder,port=0,queue=None):
    folder=h.private(folder);folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    queue=h.private(queue or h.ROOT/'.local/quality-requests');token=secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup();self.connection.settimeout(5)
        def send(self,code,data,mime='application/json'):
            body=data if isinstance(data,bytes) else json.dumps(data,ensure_ascii=False).encode()
            self.send_response(code)
            for k,v in {'Content-Type':mime,'Content-Length':str(len(body)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"}.items():self.send_header(k,v)
            self.end_headers();self.wfile.write(body)
        def guard(self,post=False):
            origin='http://127.0.0.1:'+str(self.server.server_port)
            if self.headers.get('Host')!=urlsplit(origin).netloc or self.headers.get('Sec-Fetch-Site')=='cross-site':raise PermissionError('Invalid host or cross-site request.')
            supplied=self.headers.get('Origin')
            if (supplied and supplied!=origin) or (post and supplied!=origin):raise PermissionError('Same-origin request required.')
            if self.path.startswith('/api/') and self.path!='/api/session' and not hmac.compare_digest(self.headers.get('X-Review-Token',''),token):raise PermissionError('Session expired; refresh the page.')
        def do_GET(self):
            try:
                self.guard();route=urlsplit(self.path).path
                if route=='/':self.send(200,Path(__file__).with_name('handoff_console.html').read_bytes(),'text/html; charset=utf-8');return
                if route=='/api/session':self.send(200,{'token':token});return
                packets=[]
                for p in folder.glob('*.json'):
                    if not re.fullmatch('[a-f0-9]{64}',p.stem):continue
                    try:packets.append(item(folder,p.stem))
                    except (ValueError,OSError,KeyError) as error:packets.append({'id':p.stem,'query':'Evidence needs revalidation / 검증 자료 재확인 필요','reason':str(error),'status':'decision_required','canRetest':False})
                entries=packets+[v for v in queued_items(queue) if v['id'] not in {p['id'] for p in packets}]
                if route=='/api/items':self.send(200,[{k:v[k] for k in ('id','query','status')} for v in entries]);return
                if route.startswith('/api/items/'):
                    value=next((v for v in entries if v['id']==route.removeprefix('/api/items/')),None)
                    if value is not None:self.send(200,value);return
                raise ValueError('Unknown endpoint.')
            except PermissionError as e:self.send(403,{'error':str(e)})
            except (ValueError,OSError,KeyError,StopIteration) as e:self.send(409,{'error':str(e)})
        def do_POST(self):
            try:
                self.guard(True);parts=self.path.split('/')
                if len(parts)!=5 or parts[1:3]!=['api','items'] or not re.fullmatch('[a-f0-9]{64}',parts[3]) or parts[4] not in {'retest','preserve'}:raise ValueError('Only retest notes and regression preservation supported; no merge endpoint.')
                if self.headers.get('Content-Type')!='application/json' or self.headers.get('Transfer-Encoding'):raise ValueError('JSON required.')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=32768:raise ValueError('Invalid request size.')
                data=json.loads(self.rfile.read(size));path=folder/(parts[3]+'.json')
                if parts[4]=='retest':value=h.retest(path,data.get('decision'),data.get('reason'))
                else:
                    required,forbidden=data.get('required',[]),data.get('forbidden',[])
                    if not all(isinstance(v,list) and all(isinstance(x,str) for x in v) for v in (required,forbidden)):raise ValueError('Claim arrays required.')
                    value={'saved':str(h.preserve_case(path,required,forbidden))}
                self.send(200,value)
            except PermissionError as e:self.send(403,{'error':str(e)})
            except (ValueError,OSError,KeyError,TypeError) as e:self.send(409,{'error':str(e)})
        def log_message(self,*args):pass
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',default=str(h.ROOT/'.local/handoffs'));p.add_argument('--queue');p.add_argument('--port',type=int,default=8780);a=p.parse_args()
    server=make_server(a.folder,a.port,a.queue);print('Development review: http://127.0.0.1:'+str(server.server_port),flush=True)
    try:server.serve_forever()
    finally:server.server_close()


if __name__=='__main__':main()
