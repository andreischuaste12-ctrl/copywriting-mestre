"""Operational regressions: synthetic fixtures, opt-in logs, batch integrity and release artifacts."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from copywriter_runtime import InputError, validate_copy
from copywriter_runtime.cli import batch, init_example
from copywriter_runtime.observability import append_events, summarize
from copywriter_runtime.validation import load_json
from copywriter_runtime.reporting import render


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


release = module('operational_release', 'tools/release.py')
evaluate = module('operational_evaluate', 'tools/evaluate.py')


class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.brief = load_json(ROOT / 'examples/validation/brief.pt-BR.json')
        self.draft = load_json(ROOT / 'examples/validation/output.pt-BR.json')
        self.report = validate_copy(self.brief, self.draft)

    def test_sector_corpus_good_bad_pairs(self):
        path = ROOT / 'evaluation/operational-cases.json'
        corpus = load_json(path)
        self.assertEqual(len(corpus['cases']), 6)
        for case in corpus['cases']:
            with self.subTest(case=case['id']):
                self.assertEqual(case['evidence_type'], 'synthetic')
                brief = load_json(path.parent / case['brief'])
                good = validate_copy(brief, load_json(path.parent / case['good_draft']))
                bad = validate_copy(brief, load_json(path.parent / case['bad_draft']))
                self.assertEqual(good['automated_checks'], 'passed')
                self.assertEqual(bad['automated_checks'], 'failed')
                self.assertTrue(set(case['expected_bad_codes']) <= {r['code'] for r in bad['findings']})

    def test_competing_claims_cannot_hide_pending_authorization(self):
        competing = copy.deepcopy(self.brief['claims'][0])
        competing.update(id='held', kind='regulated', authorization={'status': 'pending', 'reference': ''})
        self.brief['claims'].append(competing)
        report = validate_copy(self.brief, self.draft)
        self.assertEqual(report['disposition'], 'blocked')
        self.assertIn('authorization_pending', [r['code'] for r in report['findings']])

    def test_init_never_overwrites_existing_user_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'case'
            init_example('en-US', dest)
            before = (dest / 'brief.json').read_bytes()
            with self.assertRaises(InputError):
                init_example('pt-BR', dest)
            self.assertEqual((dest / 'brief.json').read_bytes(), before)

    def test_cli_has_no_logging_without_opt_in_and_logs_no_raw_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            log = directory / 'events.jsonl'
            command = [sys.executable, str(ROOT / 'tools/copywriter.py'), 'validate', '--brief',
                       str(ROOT / 'examples/validation/brief.pt-BR.json'), '--draft',
                       str(ROOT / 'examples/validation/output.pt-BR.json')]
            result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(directory.iterdir()), [])
            result = subprocess.run(command + ['--log', str(log)], cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = log.read_text(encoding='utf-8')
            self.assertNotIn('Pauta', text)
            self.assertNotIn(self.brief['id'], text)
            self.assertNotIn(self.draft['items'][0]['text'], text)
            self.assertEqual(summarize(log)['event_count'], 1)

    def test_logging_cannot_append_to_existing_brief_or_corrupt_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'not-events.json'
            for content in (json.dumps(self.brief), 'private unrelated content'):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(InputError):
                    append_events(path, [self.report])
                self.assertEqual(path.read_text(encoding='utf-8'), content)
                self.assertFalse(path.with_name(path.name + '.lock').exists())

    def test_locked_log_is_not_deleted_or_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'events.jsonl'
            lock = log.with_name(log.name + '.lock')
            lock.write_text('another writer')
            with self.assertRaises(InputError):
                append_events(log, [self.report])
            self.assertEqual(lock.read_text(), 'another writer')
            self.assertFalse(log.exists())

    def test_concurrent_writers_leave_whole_unique_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'events.jsonl'
            def write(_):
                try:
                    append_events(log, [self.report])
                    return 1
                except InputError:
                    return 0
            with ThreadPoolExecutor(max_workers=4) as pool:
                successes = sum(pool.map(write, range(12)))
            self.assertGreater(successes, 0)
            self.assertEqual(summarize(log)['event_count'], successes)

    def test_summary_denominators_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / 'events.jsonl'
            bad = copy.deepcopy(self.draft)
            bad['items'][0]['text'] += ' 999%'
            append_events(log, [self.report, validate_copy(self.brief, bad)])
            summary = summarize(log)
            self.assertEqual(summary['event_count'], 2)
            self.assertEqual(summary['block_rate'], 0.5)
            self.assertEqual(summary['human_review_required_rate'], 1.0)
            original = log.read_text(encoding='utf-8').splitlines()
            for mutation in ('status', 'category', 'duplicate', 'catalog'):
                with self.subTest(mutation=mutation):
                    event = json.loads(original[0])
                    if mutation == 'status':
                        event['automated_checks'] = 'failed'
                    elif mutation == 'category':
                        event['category_counts'] = {}
                    elif mutation == 'catalog':
                        event['rule_catalog_sha256'] = '0' * 64
                    content = json.dumps(event) + '\n'
                    if mutation == 'duplicate':
                        content += content
                    log.write_text(content, encoding='utf-8')
                    with self.assertRaises(InputError):
                        summarize(log)

    def test_batch_preflight_and_reserved_case_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / 'batch.json'
            base = {'schema_version': '1.0', 'cases': [{'id': 'test', 'brief': str(ROOT / 'examples/validation/brief.pt-BR.json'),
                                                        'draft': str(ROOT / 'examples/validation/output.pt-BR.json')}]}
            invalid = copy.deepcopy(base)
            invalid['cases'][0]['draft'] = 'missing.json'
            manifest.write_text(json.dumps(invalid), encoding='utf-8')
            with self.assertRaises(InputError):
                batch(manifest, root / 'bad')
            self.assertFalse((root / 'bad').exists())
            for cid in ('summary', 'CON', 'lpt1'):
                base['cases'][0]['id'] = cid
                manifest.write_text(json.dumps(base), encoding='utf-8')
                with self.assertRaises(InputError):
                    batch(manifest, root / 'reserved')
            manifest.write_text(json.dumps({'schema_version': '1.0', 'cases': [
                {**base['cases'][0], 'id': 'one'}, {**base['cases'][0], 'id': 'ONE'}]}), encoding='utf-8')
            with self.assertRaises(InputError):
                batch(manifest, root / 'collision')

    def test_batch_exports_both_formats_and_preserves_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'reports'
            result = batch(ROOT / 'examples/sectors/batch.json', dest)
            self.assertEqual(result['case_count'], 6)
            self.assertEqual(result['blocked_count'], 0)
            self.assertTrue((dest / 'health.md').is_file())
            self.assertEqual(load_json(dest / 'fintech.json')['disposition'], 'needs_human_review')
            with self.assertRaises(InputError):
                batch(ROOT / 'examples/sectors/batch.json', dest)

    def test_html_report_escapes_instead_of_executing_content(self):
        report = copy.deepcopy(self.report)
        report['findings'][0]['remediation'] = '<script>test()</script>'
        text = render(report, 'html')
        self.assertNotIn('<script>', text)
        self.assertIn('&lt;script&gt;', text)

    def test_release_is_reproducible_and_detects_archive_tampering(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            first, second = Path(tmp) / 'a', Path(tmp) / 'b'
            a = release.build(first)
            b = release.build(second)
            self.assertEqual(a['archive_sha256'], b['archive_sha256'])
            self.assertIn('copywriter-master/NOTICE', a['files'])
            self.assertIn('copywriter-master/runtime-contract.json', a['files'])
            with self.assertRaises(InputError):
                release.build(first)
            archive = first / a['archive']
            archive.write_bytes(archive.read_bytes() + b'changed')
            with self.assertRaises(InputError):
                release.verify(first)

    def test_release_rejects_wrong_tag_before_creating_destination(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            dest = Path(tmp) / 'wrong-version'
            with self.assertRaises(InputError):
                release.build(dest, 'v99.0.0')
            self.assertFalse(dest.exists())

    def reviewed_run(self, condition, repetition):
        suite = evaluate.load_suite()
        return {'schema_version': 1, 'condition': condition, 'model': 'unit-test-fixture', 'settings': 'not a model run',
                'repetition': repetition, 'reviewer': 'test-fixture',
                'suite_sha256': evaluate.digest(evaluate.SUITE_PATH.read_bytes()), 'rubric_version': suite['rubric_version'],
                'skill_sha256': None if condition == 'generic' else ('a' if condition == 'baseline' else 'b') * 64,
                'records': [{'case_id': c['id'], 'prompt': c['prompt'], 'expected': c['expected'],
                             'response': 'Synthetic scoring fixture; not a generated response.',
                             'review_note': 'Fixture to test comparison only.',
                             'scores': dict.fromkeys(suite['dimensions'], 2),
                             'hard_failures': dict.fromkeys(suite['hard_failures'], False)} for c in suite['cases']]}

    def test_benchmark_comparison_requires_matched_repetitions(self):
        runs = [self.reviewed_run(c, n) for c in evaluate.CONDITIONS for n in range(1, 4)]
        self.assertEqual(evaluate.compare_runs(runs)['comparison_status'], 'complete')
        self.assertEqual(evaluate.compare_runs(runs[:-1])['comparison_status'], 'incomplete')
        with self.assertRaises(ValueError):
            evaluate.compare_runs(runs + [copy.deepcopy(runs[0])])
        runs[-1]['model'] = 'different-model'
        with self.assertRaises(ValueError):
            evaluate.compare_runs(runs)

    def test_benchmark_report_preserves_failures_and_escapes_html(self):
        run = self.reviewed_run('candidate', 1)
        run['records'][0]['hard_failures']['changed_terms'] = True
        run['model'] = '<script>unsafe()</script>'
        report = evaluate.compare_runs([run])
        self.assertEqual(report['cases'][0]['hard_failures'], 1)
        self.assertEqual(report['cases'][0]['pass_rate'], 0.0)
        html = evaluate.render_comparison(report, 'html')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)


if __name__ == '__main__':
    unittest.main()
