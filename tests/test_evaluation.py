"""Regression checks for incomplete reviews and editorial release gates."""
import copy
import importlib.util
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('evaluate', ROOT / 'tools/evaluate.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.path = Path(tmp) / 'run.json'
            ev.prepare(SimpleNamespace(condition='candidate', model='test-fixture/not-a-model-run',
                                       settings='unit test only', repetition=1, skill_dir=None, out=self.path))
            self.run = json.loads(self.path.read_text(encoding='utf-8'))
        self.run['reviewer'] = 'unit-test-fixture'
        for r in self.run['records']:
            r['response'] = 'Synthetic fixture to test score validation; not a generated answer.'
            r['review_note'] = 'Unit test fixture only; no editorial evaluation performed.'
            r['scores'] = dict.fromkeys(r['scores'], 2)
            r['hard_failures'] = dict.fromkeys(r['hard_failures'], False)

    def test_high_score_does_not_override_hard_failure(self):
        for failure in self.run['records'][0]['hard_failures']:
            with self.subTest(failure=failure):
                run = copy.deepcopy(self.run)
                run['records'][0]['hard_failures'][failure] = True
                report = ev.score_run(run)
                self.assertFalse(report['all_passed'])
                self.assertEqual(report['cases'][0]['total'], 16)
                self.assertEqual(report['cases'][0]['hard_failures'], [failure])

    def test_threshold_and_zero_gate(self):
        rec = self.run['records'][0]
        keys = list(rec['scores'])
        for k in keys[:3]:
            rec['scores'][k] = 1
        self.assertTrue(ev.score_run(self.run)['all_passed'])  # 13, no zeros
        rec['scores'][keys[3]] = 1
        self.assertFalse(ev.score_run(self.run)['all_passed'])  # 12
        rec['scores'] = dict.fromkeys(keys, 2)
        rec['scores'][keys[0]] = 0
        self.assertFalse(ev.score_run(self.run)['all_passed'])  # 14, but one zero

    def test_rejects_incomplete_or_invalid_reviews(self):
        for field, value in [('response', ''), ('review_note', ''),
                             ('scores', dict.fromkeys(self.run['records'][0]['scores'], True)),
                             ('hard_failures', dict.fromkeys(self.run['records'][0]['hard_failures'], None))]:
            with self.subTest(field=field):
                run = copy.deepcopy(self.run)
                run['records'][0][field] = value
                with self.assertRaises(ValueError):
                    ev.score_run(run)

    def test_rejects_modified_or_missing_evidence(self):
        mutations = [lambda r: r['records'].pop(),
                     lambda r: r['records'].__setitem__(0, copy.deepcopy(r['records'][1])),
                     lambda r: r['records'][0].update(prompt='Changed brief'),
                     lambda r: r.update(suite_sha256='changed'),
                     lambda r: r.update(reviewer='')]
        for mutate in mutations:
            run = copy.deepcopy(self.run)
            mutate(run)
            with self.assertRaises(ValueError):
                ev.score_run(run)

    def test_prepare_refuses_overwriting_a_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'existing.json'
            out.write_text('preserve me')
            with self.assertRaises(FileExistsError):
                ev.prepare(SimpleNamespace(condition='generic', model='fixture', settings='none',
                                           repetition=1, skill_dir=None, out=out))
            self.assertEqual(out.read_text(), 'preserve me')

    def test_cli_exit_codes_distinguish_failed_and_invalid_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'run.json'
            def invoke(data):
                path.write_text(json.dumps(data), encoding='utf-8')
                return subprocess.run([sys.executable, str(ROOT / 'tools/evaluate.py'), 'score', str(path)],
                                      capture_output=True, text=True)
            self.assertEqual(invoke(self.run).returncode, 0)
            self.run['records'][0]['hard_failures']['changed_terms'] = True
            result = invoke(self.run)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)['all_passed'])
            self.run['records'][0]['response'] = ''
            self.assertEqual(invoke(self.run).returncode, 2)
            self.assertEqual(invoke([]).returncode, 2)

    def test_fingerprint_includes_reference_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'SKILL.md').write_text('skill')
            (folder / 'reference.md').write_text('before')
            previous = ev.skill_digest(folder)
            (folder / 'reference.md').write_text('after')
            self.assertNotEqual(previous, ev.skill_digest(folder))


if __name__ == '__main__':
    unittest.main()
