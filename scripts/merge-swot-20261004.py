"""Merge the saved 2026-10-04 CERNIC browser queries without requerying old records."""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / 'data/dataset.json').exists():
    raise SystemExit('Legacy batch script disabled after schema 2.0 migration; use scripts/build_dataset.py.')
DATE = '2026-10-04'
SHA = 'b2dee08283cfee0ba43630779b6bf702bf5df76e'
SOURCE = 'https://www.nic.edu.cn/cgi-bin/reg/otherobj'

def load_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def write_csv(path, fields, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

fields, old = load_csv(ROOT / 'data/edu-cn-roots-whois-2026-09-26.csv')
raw = json.loads((ROOT / 'data/cernic-swot-raw-2026-10-04.json').read_text())
_, candidates = load_csv(ROOT / 'data/swot-new-candidates-2026-10-04.csv')
provenance = {x['root_domain']: x for x in candidates}
assert len(raw) == 63 and {x['domain'] for x in raw} == set(provenance)
new = []
for result in raw:
    domain, text = result['domain'], result['text']
    assert re.fullmatch(r'[a-z0-9-]+\.edu\.cn', domain)
    match = re.search(r'域名\s+' + re.escape(domain) + r'\s+已于(\d{8})\s+在CERNIC注册\s*\[([^\]]+)\]', text)
    record = dict(root_domain=domain, type='', org_en=None, org_cn=None, domain_name=None,
                  network_name=None, admin_contact=None, nameservers=[], address=[], raw_note=None,
                  whois_queried=DATE, source_url=SOURCE+'?query='+domain, raw_text=text)
    if match:
        record.update(type='cn_status', org_cn=match[2], reg_date=match[1], raw_note=match[0])
    else:
        assert 'Domain Name:' in text, (domain, text)
        body = re.split(r'Whois\s+' + re.escape(domain) + r'\s*\?\s*\n', text, maxsplit=1)[1]
        header = body.split('Domain Name:')[0]
        lines = [x.strip() for x in header.splitlines() if x.strip()]
        record.update(type='full_record', org_en=lines[0], address=lines[1:])
        for key, pattern in [('domain_name', r'^\s*Domain Name:[ \t]*([^\n]*)'),
                             ('network_name', r'^\s*Network Name:[ \t]*([^\n]*)'),
                             ('admin_contact', r'Administrative Contact, Technical Contact:[ \t]*\n[ \t]*([^\n]+)')]:
            m = re.search(pattern, body, re.M)
            record[key] = re.sub(r'\s+', ' ', m[1]).strip() if m and m[1].strip() else None
        assert record['domain_name'].lower() == domain
        for line in body.split('Domain Servers in listed order:')[1].splitlines():
            parts = line.split()
            if parts and '.' in parts[0]:
                ns = {'host': parts[0], 'ip': parts[1] if len(parts)>1 else ''}
                if len(parts)>2: ns['ipv6'] = parts[2]
                record['nameservers'].append(ns)
    row = {key: '' for key in fields}
    row.update(root_domain=domain, organization_or_record_name=record['org_cn'] or record['org_en'] or '',
               collected_from='JetBrains/swot: '+ '; '.join('https://github.com/JetBrains/swot/blob/'+SHA+'/'+p for p in provenance[domain]['source_paths'].split('; ')),
               source_last_observed=DATE, current_dns_status='Not checked in 2026-10-04 WHOIS update',
               CERNIC_WHOIS_status='Confirmed '+ ('full CERNIC WHOIS record' if record['type']=='full_record' else 'CERNIC Chinese registration status')+' (queried '+DATE+')',
               evidence_hostnames='; '.join('.'.join(reversed(p.removeprefix('lib/domains/').removesuffix('.txt').split('/'))) for p in provenance[domain]['source_paths'].split('; ')),
               review_notes='SWOT candidate confirmed via CERNIC in system Chrome on 2026-10-04. Current DNS and CERNET address-list association were not checked; WHOIS nameserver addresses are registration data. Subdomains rolled up; no organization-type filtering.',
               whois_result_type=record['type'], whois_org_cn=record['org_cn'] or '', whois_org_en=record['org_en'] or '',
               whois_reg_date=record.get('reg_date',''), whois_network_name=record['network_name'] or '',
               whois_admin_contact=record['admin_contact'] or '',
               whois_ns='; '.join(ns['host']+'('+ '; '.join(v for v in [ns.get('ip'),ns.get('ipv6')] if v)+')' for ns in record['nameservers']), whois_queried=DATE)
    new.append(row)
    for folder in ['data/whois-json', 'whois-json']:
        write_json(ROOT / folder / (domain+'.json'), record)
assert not {x['root_domain'] for x in old} & {x['root_domain'] for x in new}
rows = sorted(old+new, key=lambda x:x['root_domain'])
assert len(rows)==len({x['root_domain'] for x in rows})==1380
write_csv(ROOT/'edu-cn-roots.csv', fields, rows)
write_csv(ROOT/'data/edu-cn-roots-whois-2026-10-04.csv', fields, rows)
summary = json.loads((ROOT/'data/edu-cn-roots-whois-2026-09-26.json').read_text())
summary.update(whois_queried='2026-09-26 and 2026-10-04; see each record', updated=DATE, count=len(rows), records=rows,
               query_batches=[{'date':'2026-09-26','count':1317},{'date':DATE,'count':63}],
               notes='Mixed-date cumulative dataset. Only the 63 SWOT additions were queried on 2026-10-04; previous records are unchanged.')
write_json(ROOT/'data/edu-cn-roots-whois-2026-10-04.json', summary)
print('New:', dict(Counter(x['whois_result_type'] for x in new)))
print('Total:', dict(Counter(x['whois_result_type'] for x in rows)))
