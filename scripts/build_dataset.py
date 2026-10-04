"""Validate canonical per-domain records and produce deterministic CSV/JSON."""
import argparse
import csv
import io
import json
import ipaddress
from collections import Counter
from datetime import date
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASE_FIELDS = ['root_domain', 'organization_or_record_name', 'collected_from', 'source_last_observed',
               'current_dns_status', 'A_records', 'AAAA_records', 'NS_records', 'CERNIC_WHOIS_status',
               'CERNET_address_list_association', 'evidence_hostnames', 'review_notes']
WHOIS_FIELDS = ['whois_result_type', 'whois_org_cn', 'whois_org_en', 'whois_reg_date',
                'whois_network_name', 'whois_admin_contact', 'whois_ns', 'whois_queried']
FIELDS = BASE_FIELDS + WHOIS_FIELDS

def read_json(path):
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f'{path}: duplicate JSON key {key}')
            obj[key] = value
        return obj
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)

def validate_record(record, filename, validator):
    errors = sorted(validator.iter_errors(record), key=lambda e: str(e.path))
    if errors:
        raise ValueError(f'{filename}: '+ '; '.join(f'{list(e.path)}: {e.message}' for e in errors))
    domain = record['root_domain']
    if filename != domain + '.json':
        raise ValueError(f'{filename}: filename does not match root_domain')
    date.fromisoformat(record['whois_queried'])
    if record['reg_date']:
        date.fromisoformat(record['reg_date'][:4]+'-'+record['reg_date'][4:6]+'-'+record['reg_date'][6:])
    expected_url = 'https://www.nic.edu.cn/cgi-bin/reg/otherobj?query=' + domain
    if record['source_url'] != expected_url:
        raise ValueError(f'{domain}: incorrect CERNIC source_url')
    if record['type'] == 'full_record' and (record['domain_name'] or '').lower() != domain:
        raise ValueError(f'{domain}: WHOIS domain_name mismatch')
    for ns in record['nameservers']:
        for key in ('ip', 'ipv6'):
            value = ns.get(key)
            if value:
                parsed = ipaddress.ip_address(value)
                if key == 'ipv6' and parsed.version != 6:
                    raise ValueError(f'{domain}: ipv6 field is not IPv6')
    raw = record['raw_text']
    if raw:
        if domain.lower() not in raw.lower():
            raise ValueError(f'{domain}: raw_text does not mention queried domain')
        signals = {'full_record': 'Domain Name:', 'cn_status': '在CERNIC注册', 'not_found': '没有找到'}
        if signals[record['type']] not in raw:
            raise ValueError(f'{domain}: raw_text does not support result type')
    elif not record['metadata']['review_notes']:
        raise ValueError(f'{domain}: historical raw-text absence needs review_notes')

def export_row(record):
    row = {'root_domain': record['root_domain'], **record['metadata']}
    row.update(whois_result_type=record['type'], whois_org_cn=record['org_cn'] or '',
               whois_org_en=record['org_en'] or '', whois_reg_date=record['reg_date'] or '',
               whois_network_name=record['network_name'] or '', whois_admin_contact=record['admin_contact'] or '',
               whois_ns='; '.join(n['host']+'('+(';'.join(str(n[k]) for k in ('ip','ipv6') if n.get(k)))+')' for n in record['nameservers']),
               whois_queried=record['whois_queried'])
    return {key: row[key] for key in FIELDS}

def build(input_dir, config_path, schema_path, output_dir):
    schema = read_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    config = read_json(config_path)
    if set(config) != {'schema_version', 'updated'} or config['schema_version'] != '2.0':
        raise ValueError('dataset config requires schema_version 2.0 and updated only')
    date.fromisoformat(config['updated'])
    records = []
    seen = set()
    for path in sorted(input_dir.glob('*.json')):
        record = read_json(path)
        validate_record(record, path.name, validator)
        if record['root_domain'] in seen:
            raise ValueError('Duplicate root_domain: '+record['root_domain'])
        if record['whois_queried'] > config['updated']:
            raise ValueError(path.name+': query date after dataset updated date')
        seen.add(record['root_domain'])
        records.append(record)
    if not records:
        raise ValueError('No records found')
    rows = [export_row(record) for record in records]
    batches = Counter(row['whois_queried'] for row in rows)
    types = Counter(row['whois_result_type'] for row in rows)
    summary = dict(dataset='edu-cn-roots-whois', schema_version='2.0', updated=config['updated'],
                   whois_queried='; '.join(sorted(batches)), source='https://www.nic.edu.cn/cgi-bin/reg/otherobj',
                   scope='One-label domains directly under edu.cn', count=len(rows),
                   query_batches=[{'date': key, 'count': value} for key,value in sorted(batches.items())],
                   notes='Cumulative dataset; actual query dates are recorded per domain.', records=rows)
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = 'edu-cn-roots-whois-'+config['updated']
    (output_dir/(stem+'.csv')).write_bytes(buffer.getvalue().encode('utf-8-sig'))
    (output_dir/(stem+'.json')).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    stats = {'updated':config['updated'], 'count':len(rows), 'result_types':dict(sorted(types.items())),
             'query_dates':dict(sorted(batches.items()))}
    (output_dir/'statistics.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(stats,ensure_ascii=False))
    return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'data/whois-json')
    parser.add_argument('--config', type=Path, default=ROOT/'data/dataset.json')
    parser.add_argument('--schema', type=Path, default=ROOT/'schemas/whois-record.schema.json')
    parser.add_argument('--output', type=Path, default=ROOT/'build')
    args=parser.parse_args()
    build(args.input,args.config,args.schema,args.output)

if __name__=='__main__':
    main()
