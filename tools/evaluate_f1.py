"""Check protected F1 evidence without importing any target package.

First run target's tests/f1_evaluation.py; serve its output locally and save the
actual browser DOM as browser-result.json. This command verifies both artifacts.
"""
import argparse
import hashlib
import json
from pathlib import Path

PROTECTED_SHA256 = '194206ae7fd5c9e02766d3dca482a11d1c4423b1f30c808dcc91b8bc4dec5d4b'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--target', type=Path, required=True)
    args = parser.parse_args()
    definition = Path(__file__).resolve().parents[1] / 'contracts/cora/evaluations/F1-distance-decay.json'
    assert hashlib.sha256(definition.read_bytes()).hexdigest() == PROTECTED_SHA256, 'Protected evaluator changed; owner decision required.'
    contract = json.loads(definition.read_text())
    python = json.loads((args.evidence/'python-result.json').read_text())
    browser = json.loads((args.evidence/'browser-result.json').read_text())
    assert browser['status'] == 'PASS'
    assert len(browser['results']) == 4 and all(row['pass'] for row in browser['results'])
    assert len(browser['invalid']) == 10 and all(row['rejected'] for row in browser['invalid'])
    assert set(python['checks']) == {row['id'] for row in contract['cases']}
    assert all(row['pass'] for row in python['checks'].values())
    assert len(python['routes']) == 2
    for route in python['routes']:
        assert not route['falseActivations'] and not route['missedActivations']
        for boundary in ['kernel','sqliteKernel']:
            actual = [r for r in browser['results'] if r['query']==route['query'] and r['boundary']==boundary]
            assert len(actual)==1 and actual[0]['actual']==route[boundary]
    fixture = args.target/'tests/fixtures/f1-shared-graph.json'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest()==python['fixtureSha256']
    source_hashes = {str(p.relative_to(args.target)): hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['src','tests'] for p in sorted((args.target/folder).rglob('*')) if p.is_file() and p.suffix in {'.py','.json'}}
    assert source_hashes == python['sourceHashes'], 'Source changed since evidence export; rerun evaluation.'
    report = {'status':'PASS','definitionSha256':PROTECTED_SHA256,'caseResults':python['checks'],'routes':python['routes'],'browserComparisons':4,'browserRejectedInputs':10,'sourceHashes':source_hashes,'limits':['Synthetic evidence/context policy, not empirical semantic accuracy.','Browser tests invoke rendered production kernel functions, not the complete interactive UI.','Review gate remains separate from executable case results.']}
    (args.evidence/'evaluation-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 13 protected cases; 4 shared-boundary browser comparisons; 10 invalid browser inputs.')

if __name__=='__main__':
    main()
