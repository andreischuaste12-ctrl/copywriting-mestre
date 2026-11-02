"""Command-line behavior: exit codes, report files, summaries and entrypoints."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from copywriter_runtime import cli
from copywriter_runtime.observability import append_events
from copywriter_runtime.validation import InputError, load_json, validate_copy

EXAMPLES = ROOT / 'examples/validation'


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = cli.main(list(argv))
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_init_validate_round_trip_and_exit_codes(self):
        case = self.dir / 'case'
        code, out, _ = run_cli('init', '--example', 'en-US', '--dest', str(case))
        self.assertEqual(code, 0)
        self.assertIn('Created synthetic example', out)
        args = ('validate', '--brief', str(case / 'brief.json'), '--draft', str(case / 'output.json'))
        code, out, _ = run_cli(*args)
        self.assertEqual((code, json.loads(out)['automated_checks']), (0, 'passed'))
        blocked = EXAMPLES / 'output.blocked.pt-BR.json'
        code, out, _ = run_cli('validate', '--brief', str(EXAMPLES / 'brief.pt-BR.json'), '--draft', str(blocked))
        self.assertEqual((code, json.loads(out)['automated_checks']), (1, 'failed'))

    def test_init_refuses_existing_destination(self):
        code, _, err = run_cli('init', '--dest', str(self.dir))
        self.assertEqual(code, 2)
        self.assertIn('already exists', err)

    def test_missing_input_is_exit_code_two(self):
        code, _, err = run_cli('validate', '--brief', str(self.dir / 'nope.json'), '--draft', str(self.dir / 'nope2.json'))
        self.assertEqual(code, 2)
        self.assertIn('Cannot read input', err)

    def test_report_out_file_is_exclusive_and_formats_render(self):
        brief, draft = str(EXAMPLES / 'brief.en-US.json'), str(EXAMPLES / 'output.en-US.json')
        for fmt, marker in (('markdown', '# Copy validation'), ('html', '<!doctype html>')):
            out_file = self.dir / f'report.{fmt}'
            code, _, _ = run_cli('validate', '--brief', brief, '--draft', draft, '--format', fmt, '--out', str(out_file))
            self.assertEqual(code, 0)
            self.assertIn(marker, out_file.read_text(encoding='utf-8'))
            before = out_file.read_text(encoding='utf-8')
            code, _, err = run_cli('validate', '--brief', brief, '--draft', draft, '--format', fmt, '--out', str(out_file))
            self.assertEqual(code, 2)
            self.assertIn('exists', err)
            self.assertEqual(out_file.read_text(encoding='utf-8'), before)

    def test_batch_command_reports_blocked_cases_and_logs_events(self):
        out_dir, log = self.dir / 'reports', self.dir / 'events.jsonl'
        code, out, _ = run_cli('batch', '--manifest', str(ROOT / 'examples/sectors/batch.json'),
                               '--out-dir', str(out_dir), '--log', str(log))
        summary = json.loads(out)
        self.assertEqual(code, 1 if summary['blocked_count'] else 0)
        self.assertGreater(summary['case_count'], 0)
        self.assertTrue((out_dir / 'summary.json').is_file())
        code, out, _ = run_cli('summary', '--log', str(log), '--format', 'markdown')
        self.assertEqual(code, 0)
        self.assertIn('Events: ' + str(summary['case_count']), out)
        code, _, err = run_cli('batch', '--manifest', str(ROOT / 'examples/sectors/batch.json'), '--out-dir', str(out_dir))
        self.assertEqual(code, 2)
        self.assertIn('already exists', err)

    def test_summary_of_missing_log_is_a_clean_error(self):
        code, _, err = run_cli('summary', '--log', str(self.dir / 'missing.jsonl'))
        self.assertEqual(code, 2)
        self.assertIn('Error:', err)

    def test_stale_lock_message_identifies_the_owner_without_removing_it(self):
        brief, output = load_json(EXAMPLES / 'brief.en-US.json'), load_json(EXAMPLES / 'output.en-US.json')
        report = validate_copy(brief, output)
        log = self.dir / 'events.jsonl'
        lock = self.dir / 'events.jsonl.lock'
        lock.write_text('pid=4242 created=2026-01-01T00:00:00+00:00\n', encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'pid=4242'):
            append_events(log, [report])
        self.assertTrue(lock.exists())
        lock.unlink()
        append_events(log, [report])
        self.assertFalse(lock.exists())
        self.assertNotIn('pid=', log.read_text(encoding='utf-8'))


class EntrypointTests(unittest.TestCase):
    def run_script(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / script), *args], capture_output=True, text=True)

    def test_friendly_cli_entrypoint(self):
        proc = self.run_script('tools/copywriter.py', 'validate', '--brief', str(EXAMPLES / 'brief.en-US.json'),
                               '--draft', str(EXAMPLES / 'output.en-US.json'))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['disposition'], 'needs_human_review')

    def test_v12_validator_entrypoint_keeps_its_exit_codes(self):
        brief = str(EXAMPLES / 'brief.pt-BR.json')
        self.assertEqual(self.run_script('tools/validate_copy.py', '--brief', brief,
                                         '--draft', str(EXAMPLES / 'output.pt-BR.json')).returncode, 0)
        self.assertEqual(self.run_script('tools/validate_copy.py', '--brief', brief,
                                         '--draft', str(EXAMPLES / 'output.blocked.pt-BR.json')).returncode, 1)
        self.assertEqual(self.run_script('tools/validate_copy.py', '--brief', brief, '--draft', 'missing.json').returncode, 2)

    def test_references_tool_entrypoint(self):
        proc = self.run_script('tools/references.py', 'check')
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == '__main__':
    unittest.main()
