"""Entry points of the maintainer tools: argument handling, exit codes and exclusive output files."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluate = load('tools_evaluate_main', 'tools/evaluate.py')
release = load('tools_release_main', 'tools/release.py')


def run_main(module, *argv):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.object(sys, 'argv', ['tool', *argv]), redirect_stdout(out), redirect_stderr(err):
        try:
            code = module.main()
        except SystemExit as exit_:
            code = exit_.code
    return code or 0, out.getvalue(), err.getvalue()


class EvaluateMainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def prepared(self, condition='candidate', repetition='1'):
        path = self.dir / f'{condition}-{repetition}.json'
        args = ['prepare', '--condition', condition, '--model', 'test/model-1', '--settings', 'fresh session',
                '--repetition', repetition, '--out', str(path)]
        if condition == 'baseline':
            args += ['--skill-dir', str(ROOT / 'skills/copywriter-master')]
        code, _, err = run_main(evaluate, *args)
        self.assertEqual(code, 0, err)
        return path

    def complete(self, path):
        run = json.loads(path.read_text(encoding='utf-8'))
        run['reviewer'] = 'reviewer-1'
        for record in run['records']:
            record['response'] = 'actual reviewed answer'
            record['review_note'] = 'meets the expected criteria'
            record['scores'] = {k: 2 for k in record['scores']}
            record['hard_failures'] = {k: False for k in record['hard_failures']}
        path.write_text(json.dumps(run), encoding='utf-8')

    def test_check_command(self):
        self.assertEqual(run_main(evaluate, 'check')[0], 0)

    def test_unreviewed_run_is_rejected_with_exit_two(self):
        code, _, err = run_main(evaluate, 'score', str(self.prepared()))
        self.assertEqual(code, 2)
        self.assertIn('Error:', err)

    def test_reviewed_run_scores_and_report_file_is_exclusive(self):
        path = self.prepared()
        self.complete(path)
        report = self.dir / 'report.json'
        code, _, _ = run_main(evaluate, 'score', str(path), '--out', str(report))
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(report.read_text(encoding='utf-8'))['all_passed'])
        code, _, err = run_main(evaluate, 'score', str(path), '--out', str(report))
        self.assertEqual(code, 2)
        code, out, _ = run_main(evaluate, 'score', str(path))
        self.assertEqual(code, 0)
        self.assertIn('"all_passed": true', out)

    def test_failed_hard_failure_makes_score_exit_one(self):
        path = self.prepared()
        self.complete(path)
        run = json.loads(path.read_text(encoding='utf-8'))
        first = run['records'][0]['hard_failures']
        first[next(iter(first))] = True
        path.write_text(json.dumps(run), encoding='utf-8')
        self.assertEqual(run_main(evaluate, 'score', str(path))[0], 1)

    def test_compare_reports_incomplete_evidence_and_never_overwrites(self):
        path = self.prepared()
        self.complete(path)
        out_file = self.dir / 'comparison.md'
        code, _, _ = run_main(evaluate, 'compare', str(path), '--out', str(out_file), '--format', 'markdown')
        self.assertEqual(code, 1)
        self.assertIn('Status: incomplete', out_file.read_text(encoding='utf-8'))
        code, _, _ = run_main(evaluate, 'compare', str(path), '--out', str(out_file))
        self.assertEqual(code, 2)

    def test_prepare_rejects_invalid_arguments(self):
        code, _, err = run_main(evaluate, 'prepare', '--condition', 'baseline', '--model', 'm', '--settings', 's',
                                '--out', str(self.dir / 'x.json'))
        self.assertEqual(code, 2)
        self.assertIn('--skill-dir', err)
        code, _, _ = run_main(evaluate, 'prepare', '--condition', 'candidate', '--model', 'm', '--settings', 's',
                              '--repetition', '0', '--out', str(self.dir / 'y.json'))
        self.assertEqual(code, 2)


class ReleaseMainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_check_build_verify_and_refuse_overwrite(self):
        dist = self.dir / 'dist'
        self.assertEqual(run_main(release, 'check')[0], 0)
        code, _, err = run_main(release, 'build', '--out', str(dist))
        self.assertEqual(code, 0, err)
        self.assertEqual(run_main(release, 'verify', '--directory', str(dist))[0], 0)
        code, _, err = run_main(release, 'build', '--out', str(dist))
        self.assertEqual(code, 2)
        self.assertIn('refuse to overwrite', err)

    def test_wrong_expected_version_is_rejected_before_writing(self):
        dist = self.dir / 'dist'
        code, _, err = run_main(release, 'build', '--out', str(dist), '--expected-version', 'v0.0.1')
        self.assertEqual(code, 2)
        self.assertIn('does not match VERSION', err)
        self.assertFalse(dist.exists())

    def test_verify_rejects_a_damaged_manifest_and_missing_directory(self):
        dist = self.dir / 'dist'
        run_main(release, 'build', '--out', str(dist))
        manifest_path = dist / 'manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        mutations = {
            'extra field': lambda m: m.update(extra=1),
            'bad version': lambda m: m.update(version='latest'),
            'wrong archive name': lambda m: m.update(archive='other.zip'),
            'missing required file': lambda m: m['files'].pop('copywriter-master/LICENSE'),
            'unsafe entry': lambda m: m['files'].update({'copywriter-master/../evil': '0' * 64}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                damaged = json.loads(json.dumps(manifest))
                mutate(damaged)
                manifest_path.write_text(json.dumps(damaged), encoding='utf-8')
                self.assertEqual(run_main(release, 'verify', '--directory', str(dist))[0], 2)
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        self.assertEqual(run_main(release, 'verify', '--directory', str(dist))[0], 0)
        self.assertEqual(run_main(release, 'verify', '--directory', str(self.dir / 'absent'))[0], 2)

    def test_installer_pin_mismatch_is_a_lint_error(self):
        with mock.patch.object(release, 'ROOT', self.dir):
            (self.dir / 'VERSION').write_text('9.9.9\n', encoding='utf-8')
            (self.dir / 'install.sh').write_text('RELEASE_VERSION="1.0.0"\n', encoding='utf-8')
            (self.dir / 'install.ps1').write_text("$ReleaseVersion = '9.9.9'\n", encoding='utf-8')
            with self.assertRaisesRegex(release.InputError, 'install.sh release pin'):
                release.check_installer_pins()
            (self.dir / 'install.sh').write_text('RELEASE_VERSION="9.9.9"\n', encoding='utf-8')
            release.check_installer_pins()


if __name__ == '__main__':
    unittest.main()
