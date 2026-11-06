"""Verify bilingual rendering preserves revision-bound machine evidence."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from delivery_publish import render_report


class BilingualReportTests(unittest.TestCase):
    def test_english_then_full_korean_prose_with_identical_raw_evidence(self):
        report = {'status': 'ready_for_merge_approval', 'source_branch': 'task', 'source_sha': 'abc123',
                  'target_branch': 'main', 'target_sha': 'def456', 'compare_url': 'https://example.invalid/compare',
                  'diff_summary': '1 file changed', 'review': {'criteria': [{'id': 'quality', 'passed': True}]},
                  'ci': {'status': 'success'}, 'message': 'Original diagnostic with ``` and 한국어',
                  'change_summary': 'A task description', 'implementation_summaries': [], 'findings': None,
                  'proposed_action': 'Owner authorization required', 'limits': ['No automatic merge']}
        text = render_report(report, Path('/evidence/report.json'))
        en, ko = text.split('\n---\n\n')
        self.assertTrue(en.startswith('<!-- document-language: en -->'))
        self.assertTrue(ko.startswith('<!-- document-language: ko -->\n# 한국어 번역'))
        for block in [en, ko]:
            self.assertIn('abc123', block); self.assertIn('def456', block)
            self.assertIn('/evidence/report.json', block)
            payload = json.loads(block.split('```json\n')[1].split('\n```')[0])
            self.assertEqual(payload['message'], report['message'])
            self.assertEqual(payload['limits'], report['limits'])
        self.assertIn('does not authorize a merge', en)
        self.assertIn('병합을 승인하지는 않는다', ko)


if __name__ == '__main__':
    unittest.main()
