import copy
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build_dataset.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.validator = Draft202012Validator(builder.read_json(ROOT/'schemas/whois-record.schema.json'))
        self.record = builder.read_json(ROOT/'data/whois-json/cupk.edu.cn.json')

    def invalid(self, change, filename='cupk.edu.cn.json'):
        record=copy.deepcopy(self.record)
        change(record)
        with self.assertRaises((ValueError, TypeError)):
            builder.validate_record(record,filename,self.validator)

    def test_missing_metadata_field(self):
        self.invalid(lambda r:r['metadata'].pop('collected_from'))

    def test_bad_type_and_unknown_field(self):
        self.invalid(lambda r:r.update(type='timeout'))
        self.invalid(lambda r:r.update(typo='accidental field'))

    def test_filename_and_domain_mismatch(self):
        self.invalid(lambda r:None,filename='other.edu.cn.json')
        self.invalid(lambda r:r.update(domain_name='OTHER.EDU.CN'))
        self.invalid(lambda r:r.update(root_domain='www.cupk.edu.cn'))

    def test_bad_date_ip_and_source(self):
        self.invalid(lambda r:r.update(whois_queried='2026-02-30'))
        self.invalid(lambda r:r['nameservers'][0].update(ip='999.1.1.1'))
        self.invalid(lambda r:r.update(source_url='https://example.com'))

    def test_response_type_requires_evidence(self):
        self.invalid(lambda r:r.update(raw_text='cupk.edu.cn: 403 Forbidden'))
        self.invalid(lambda r:r.update(type='cn_status',org_cn=None,reg_date=None))

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_text('{"type":"full_record","type":"not_found"}')
            with self.assertRaises(ValueError):builder.read_json(p)

    def test_all_records_export_roundtrip_and_determinism(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)
            rows=builder.build(ROOT/'data/whois-json',ROOT/'data/dataset.json',ROOT/'schemas/whois-record.schema.json',output)
            csv_path=next(output.glob('*.csv'))
            self.assertTrue(csv_path.read_bytes().startswith(b'\xef\xbb\xbf'))
            with csv_path.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f);self.assertEqual(reader.fieldnames,builder.FIELDS)
                self.assertEqual(list(reader),rows)
            summary=builder.read_json(next(output.glob('edu*.json')))
            self.assertEqual(summary['records'],rows)
            self.assertEqual(summary['count'],len(rows))
            self.assertEqual(sum(b['count'] for b in summary['query_batches']),len(rows))
            before={p.name:p.read_bytes() for p in output.iterdir()}
            builder.build(ROOT/'data/whois-json',ROOT/'data/dataset.json',ROOT/'schemas/whois-record.schema.json',output)
            self.assertEqual(before,{p.name:p.read_bytes() for p in output.iterdir()})
            # Migration must preserve all published fields except explicit legacy notes
            # and the standardized display separator between nameserver addresses.
            old=builder.read_json(ROOT/'data/edu-cn-roots-whois-2026-10-04.json')['records']
            by={r['root_domain']:r for r in rows}
            for row in old:
                for key,value in row.items():
                    if key not in {'review_notes','whois_ns'}:
                        self.assertEqual(by[row['root_domain']][key],value)

if __name__=='__main__':unittest.main()
