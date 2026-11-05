"""Run W1 fault rehearsals and validate separately executed real pilot receipts.

Synthetic model/GitHub fixtures are explicitly labeled, not presented as live AI
judgments. Acceptance still requires independent source/evidence review.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest

from development_loop import save, valid_review, effective_contract
from delivery_evidence import manifest, git

ROOT = Path(__file__).resolve().parents[1]
MAP = {
    'W02': ['test_w02_'], 'W03': ['test_w03_', 'test_negative_review_'], 'W04': ['test_w04_', 'test_environment_change_', 'test_command_environment_'],
    'W05': ['test_w05_', 'test_w04_'], 'W06': ['test_w06_'], 'W07': ['test_w07_'],
    'W08': ['test_w08_'], 'W09': ['test_w09_'], 'W10': ['test_w10_', 'test_budget_timeout_'],
    'W11': ['test_w11_', 'test_w01_', 'test_publication_receipts_', 'test_report_is_idempotent_'],
    'W12': ['test_w12_'], 'W13': ['test_w13_'], 'W14': ['test_w14_'],
    'W15': ['test_w15_'], 'W16': ['test_w16_', 'test_legacy_state_'],
    'W18': ['test_w01_', 'test_legacy_state_', 'test_report_failure_'],
}


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({'id': test.id(), 'status': 'pass'})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({'id': test.id(), 'status': 'skipped', 'reason': reason})

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.records.append({'id': test.id(), 'status': 'failed', 'error': self._exc_info_to_string(error, test)})

    def addError(self, test, error):
        super().addError(test, error)
        self.records.append({'id': test.id(), 'status': 'error', 'error': self._exc_info_to_string(error, test)})


def evaluate(pilot_state, output):
    definition_path = ROOT/'contracts/dev-workflow/evaluations/W1-reviewable-delivery.json'
    definition = json.loads(definition_path.read_text())
    contract = json.loads((ROOT/'contracts/dev-workflow/W1-reviewable-delivery.json').read_text())
    if hashlib.sha256(definition_path.read_bytes()).hexdigest() != contract['evaluation_file_sha256'] or definition != contract['acceptance_evaluation']:
        raise ValueError('Frozen W1 evaluation changed.')
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result = unittest.TextTestRunner(verbosity=1, resultclass=RecordedResult).run(suite)
    cases = {}
    for key, prefixes in MAP.items():
        records = [r for r in result.records if any(p in r['id'] for p in prefixes)]
        cases[key] = {'pass': bool(records) and all(r['status']=='pass' for r in records),
                      'kind': 'Synthetic model/GitHub faults; real temporary Git/bare remotes. W06 uses installed actual Chrome.',
                      'tests': records}
    live = json.loads(pilot_state.read_text())
    target = Path(live['target'])
    task = effective_contract(json.loads((ROOT/'contracts/cora/W1-state-type-pilot.json').read_text()))
    checks = []
    browser = []
    model_commands = []
    for attempt in live['attempts']:
        folder = Path(attempt['folder'])
        for p in folder.glob('*-execution.json'):
            record = json.loads(p.read_text())
            if p.name.startswith('check-'):
                checks.append(record)
            if p.name in {'implementation-execution.json','review-execution.json'}:
                model_commands.append(record)
        if (folder/'browser-binding.json').exists():
            binding = json.loads((folder/'browser-binding.json').read_text())
            browser.append(binding)
    latest = Path(live['attempts'][-1]['folder']) if live['attempts'] else None
    latest_checks = [json.loads(p.read_text()) for p in latest.glob('check-*-execution.json')] if latest else []
    ledger = [json.loads(p.read_text()) for p in pilot_state.parent.rglob('*-execution.json')]
    no_pr = not any(len(r['argv'])>1 and r['argv'][0]=='gh' and r['argv'][1]=='pr' for r in ledger)
    live_ok = (live['status']=='ready_for_merge_approval' and valid_review(live.get('last_review', {}), task['criteria'])
               and len(latest_checks)==len(task['checks']) and all(r['exit_code']==0 for r in latest_checks)
               and browser and browser[-1]['target_digest']==live['accepted_digest']
               and manifest(target)['digest']==live['accepted_digest'] and git(target,'rev-parse','HEAD')==live['published_sha']
               and live.get('last_ci',{}).get('status')=='success' and no_pr and len(model_commands)>=2
               and Path(live['report']).exists())
    for key in ['W01','W17']:
        cases[key]={'pass':bool(live_ok),'kind':'Actual CoRA worker/reviewer/checks/Chrome/GitHub push CI/report; no manual stage handoffs.',
                    'state':str(pilot_state),'head':live.get('published_sha'),'no_pr_calls':no_pr,'model_commands':model_commands,
                    'browser':browser,'ci':live.get('last_ci')}
    expected = {r['id'] for r in definition['cases']}
    if set(cases)!=expected:
        raise ValueError('Incomplete W1 scenario coverage: '+repr(expected-set(cases)))
    report={'status':'PASS' if result.wasSuccessful() and all(c['pass'] for c in cases.values()) else 'INCOMPLETE',
            'definition_sha256':contract['evaluation_file_sha256'],'cases':cases,'unit_tests':result.testsRun,
            'unit_results':result.records,'controller_manifest':manifest(ROOT),'pilot':str(pilot_state),
            'limits':['Independent final source/evidence review is still mandatory.','Synthetic faults do not establish general AI semantic reliability.']}
    save(output,report)
    print(json.dumps({'status':report['status'],'unit_tests':result.testsRun,'cases':{k:v['pass'] for k,v in cases.items()}},sort_keys=True))
    return report['status']=='PASS'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot-state',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    sys.exit(0 if evaluate(a.pilot_state,a.output) else 2)
