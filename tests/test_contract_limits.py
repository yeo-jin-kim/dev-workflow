"""Frozen ceiling boundaries, including direct W1 entry and malformed values."""
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from contract_limits import validate_contract_limits
from delivery_loop import Delivery
from unittest.mock import patch
import tempfile


class ContractLimitsTests(unittest.TestCase):
    def test_actual_contract_boundary(self):
        c=json.loads((Path(__file__).resolve().parents[1]/'contracts/cora/recall-answer-repair.json').read_text())
        validate_contract_limits(c,3600,5)
        for seconds,cycles in [(3601,5),(3600,6),(True,5),(3600,True),(0,1)]:
            with self.assertRaises(ValueError):validate_contract_limits(c,seconds,cycles)
        for invalid in [[],{}, {'total_seconds_max':True,'max_cycles_max':5}]:
            with self.assertRaises(ValueError):validate_contract_limits({'execution_limits':invalid},1,1)

    def test_direct_w1_rejects_excess_before_state_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);contract=root/'contract.json';project=root/'project.json';state=root/'state'
            contract.write_text(json.dumps({'execution_limits':{'total_seconds_max':3600,'max_cycles_max':5},'criteria':[]}))
            project.write_text(json.dumps({'root':str(root/'target'),'contract':str(contract)}))
            with self.assertRaisesRegex(ValueError,'frozen contract limit'):
                Delivery(project,state,3600,6)
            self.assertFalse(state.exists())
