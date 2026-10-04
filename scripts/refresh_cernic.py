"""Bounded CERNIC HTTP refresh with checkpoints, timings and preserved history."""
import argparse,concurrent.futures,hashlib,html,json,re,subprocess,time,threading,statistics,ipaddress
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from html.parser import HTMLParser
import build_dataset as builder
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
class TextParser(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.pre=[];self.depth=0
    def handle_starttag(self,tag,attrs):
        if tag=='pre':self.depth+=1
        if tag in {'br','p','h2','hr'}:self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag=='pre':self.depth-=1
        if tag in {'h2','p'}:self.parts.append('\n')
    def handle_data(self,data):
        self.parts.append(data)
        if self.depth:self.pre.append(data)

def parse(domain,raw,old,day):
    p=TextParser();p.feed(raw.decode('gbk'));text=''.join(p.parts);body=''.join(p.pre).strip()
    if not body:body=text
    record=json.loads(json.dumps(old));record.update(org_en=None,org_cn=None,domain_name=None,network_name=None,admin_contact=None,reg_date=None,nameservers=[],address=[],raw_note=None,raw_text=text,whois_queried=day,source_url='https://www.nic.edu.cn/cgi-bin/reg/otherobj?query='+domain)
    m=re.search(r'域名\s+'+re.escape(domain)+r'\s+已于(\d{8})\s+在CERNIC注册\s*\[([^\]]+)\]',body)
    if m:record.update(type='cn_status',org_cn=m[2],reg_date=m[1],raw_note=m[0])
    elif 'Domain Name:' in body:
        lines=[x.strip() for x in body.split('Domain Name:')[0].splitlines() if x.strip()]
        record.update(type='full_record',org_en=lines[0],address=lines[1:])
        for key,pattern in [('domain_name',r'^\s*Domain Name:[ \t]*([^\n]*)'),('network_name',r'^\s*Network Name:[ \t]*([^\n]*)'),('admin_contact',r'Administrative Contact(?:, Technical Contact)?:[ \t]*\n[ \t]*([^\n]+)')]:
            match=re.search(pattern,body,re.M);record[key]=re.sub(r'\s+',' ',match[1]).strip() if match and match[1].strip() else None
        if 'Domain Servers in listed order:' not in body:raise ValueError('Incomplete WHOIS record')
        for line in body.split('Domain Servers in listed order:')[1].splitlines():
            parts=line.split()
            if parts and '.' in parts[0]:
                addresses=parts[1:]
                ipv4=[a for a in addresses if ipaddress.ip_address(a).version==4]
                ipv6=[a for a in addresses if ipaddress.ip_address(a).version==6]
                ns={'host':parts[0],'ip':ipv4[0] if ipv4 else (ipv6[0] if ipv6 else '')}
                if ipv6:ns['ipv6']=ipv6[0]
                if len(ipv4)>1 or len(ipv6)>1:ns['addresses']=addresses
                record['nameservers'].append(ns)
    elif '没有找到' in body and domain.lower() in body.lower():record.update(type='not_found',raw_note=body.strip())
    else:raise ValueError('Unrecognized or incomplete response')
    record['metadata']['organization_or_record_name']=record['org_cn'] or record['org_en'] or old['metadata']['organization_or_record_name']
    record['metadata']['CERNIC_WHOIS_status']=f'CERNIC HTTP query: {record["type"]} (queried {day})'
    notes=record['metadata']['review_notes']
    notes=re.sub(r'; Legacy schema migration:.*?per-domain file\.','',notes)
    record['metadata']['review_notes']=notes+f'; CERNIC rechecked by background HTTP on {day}; original discovery and DNS evidence dates retained.'
    return record

class Fetcher:
    def __init__(self,out,rate=8):self.out=out;self.lock=threading.Lock();self.next=0;self.rate=rate
    def fetch(self,domain):
        with self.lock:
            now=time.monotonic();wait=max(0,self.next-now);self.next=max(now,self.next)+1/self.rate
        if wait:time.sleep(wait)
        path=self.out/(domain+'.html');start=time.monotonic()
        run=subprocess.run(['curl','--silent','--show-error','--connect-timeout','10','--max-time','30','--output',str(path),'--write-out','%{http_code} %{time_connect} %{time_starttransfer} %{time_total}', 'https://www.nic.edu.cn/cgi-bin/reg/otherobj?query='+domain],capture_output=True,text=True)
        pieces=run.stdout.split();result={'domain':domain,'exit_code':run.returncode,'timing':run.stdout,'error':run.stderr,'elapsed':time.monotonic()-start}
        if run.returncode or not pieces or pieces[0]!='200':raise RuntimeError(json.dumps(result))
        result.update(http_status=200,total_seconds=float(pieces[-1]),first_byte_seconds=float(pieces[-2]),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        return result,path.read_bytes()

def main():
    a=argparse.ArgumentParser();a.add_argument('--benchmark',action='store_true');a.add_argument('--workers',type=int,default=4);args=a.parse_args()
    if not 1<=args.workers<=8:raise SystemExit('workers must be within 1..8')
    stamp=datetime.now(ZoneInfo('Asia/Shanghai'));day=stamp.date().isoformat();batch=stamp.strftime('%Y%m%d-%H%M%S')
    out=ROOT/'outputs'/'http-refresh'/batch;out.mkdir(parents=True)
    paths=sorted((ROOT/'data/whois-json').glob('*.json'));old={p.stem:builder.read_json(p) for p in paths}
    validator=Draft202012Validator(builder.read_json(ROOT/'schemas/whois-record.schema.json'))
    fetcher=Fetcher(out)
    if args.benchmark:
        reports=[]
        for workers in [1,2,4,8]:
            start=time.monotonic();results=[];errors=[]
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                futures={pool.submit(fetcher.fetch,d):d for d in list(old)[0:24]}
                for f,d in futures.items():
                    try:
                        timing,raw=f.result();r=parse(d,raw,old[d],day);builder.validate_record(r,d+'.json',validator);results.append(timing)
                    except Exception as e:errors.append(str(e))
            times=sorted(x['total_seconds'] for x in results);wall=time.monotonic()-start
            report={'workers':workers,'count':len(results),'errors':errors,'wall_seconds':wall,'requests_per_second':len(results)/wall,'median_seconds':statistics.median(times) if times else None,'max_seconds':max(times) if times else None,'p95_seconds':times[min(len(times)-1,int(len(times)*.95))] if times else None,'request_timings':results}
            reports.append(report);print(json.dumps({k:v for k,v in report.items() if k!='request_timings'}),flush=True)
            if errors:break
        (ROOT/'data/cernic-http-benchmark-2026-10-04.json').write_text(json.dumps({'connect_timeout_seconds':10,'total_timeout_seconds':30,'global_rate_limit_per_second':8,'note':'Observed bounded test; does not establish server capacity or server-side timeout limit.','runs':reports},indent=2)+'\n')
        return
    # Snapshot every canonical JSON before any query or mutation.
    backup=ROOT/'data'/'history'/('pre-http-refresh-'+batch+'.json');backup.parent.mkdir(exist_ok=True)
    backup.write_text(json.dumps({'records':list(old.values())},ensure_ascii=False,indent=2)+'\n')
    stage=out/'records';stage.mkdir();timings=[];errors=[];start=time.monotonic()
    def task(d):
        for attempt in range(3):
            try:
                t,raw=fetcher.fetch(d);r=parse(d,raw,old[d],day);builder.validate_record(r,d+'.json',validator);return t,r
            except Exception as e:
                if attempt==2:raise
                time.sleep(2*(attempt+1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(task,d):d for d in old}
        for f in concurrent.futures.as_completed(futures):
            d=futures[f]
            try:
                t,r=f.result();timings.append(t);(stage/(d+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
            except Exception as e:errors.append({'domain':d,'error':str(e)})
            if (len(timings)+len(errors))%100==0:print(f'completed={len(timings)} errors={len(errors)} elapsed={time.monotonic()-start:.1f}s',flush=True)
    report={'batch':batch,'date':day,'workers':args.workers,'rate_limit_per_second':8,'total_timeout_seconds':30,'elapsed_seconds':time.monotonic()-start,'count':len(timings),'errors':errors,'requests':timings}
    (ROOT/'data'/('cernic-http-refresh-'+batch+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    if errors:raise SystemExit('Incomplete batch; canonical data unchanged. Check saved report and staged results.')
    rows=builder.build(stage,ROOT/'data/dataset.json',ROOT/'schemas/whois-record.schema.json',out/'generated')
    for p in stage.glob('*.json'):
        (ROOT/'data/whois-json'/p.name).write_bytes(p.read_bytes())
        (ROOT/'whois-json'/p.name).write_bytes(p.read_bytes())
    builder.build(ROOT/'data/whois-json',ROOT/'data/dataset.json',ROOT/'schemas/whois-record.schema.json',ROOT/'build')
    for suffix in ['csv','json']:
        source=ROOT/'build'/f'edu-cn-roots-whois-{day}.{suffix}'
        (ROOT/'data'/f'edu-cn-roots-whois-latest.{suffix}').write_bytes(source.read_bytes())
        (ROOT/'data'/f'edu-cn-roots-whois-{batch}.{suffix}').write_bytes(source.read_bytes())
    (ROOT/'edu-cn-roots.csv').write_bytes((ROOT/'data/edu-cn-roots-whois-latest.csv').read_bytes())
    (ROOT/'data/statistics.json').write_bytes((ROOT/'build/statistics.json').read_bytes())
    print('COMPLETE '+json.dumps(report|{'requests':'saved in report'}),flush=True)
if __name__=='__main__':main()
