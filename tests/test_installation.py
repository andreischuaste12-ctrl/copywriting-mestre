"""Check distributable attribution and preservation during installer operations."""
from pathlib import Path
import shutil
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('bash') and os.name != 'nt', 'Native Bash tests; Windows uses the PowerShell CI job')
class InstallationTests(unittest.TestCase):
    def install(self, destination, *args, success=True):
        proc = subprocess.run(['bash', str(ROOT / 'install.sh'), '--dest', str(destination), *args],
                              capture_output=True, text=True)
        if success:
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        else:
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return proc

    def test_distribution_update_dry_run_and_uninstall(self):
        with tempfile.TemporaryDirectory(prefix='copywriter test ') as tmp:
            dest = Path(tmp) / 'assistant skills'
            self.install(dest, '--dry-run')
            self.assertFalse(dest.exists())
            self.install(dest)
            target = dest / 'copywriter-master'
            for name in ('LICENSE', 'NOTICE'):
                self.assertEqual((ROOT / name).read_bytes(), (target / name).read_bytes())
            for name in ('brief', 'output'):
                relative = f'schemas/{name}.schema.json'
                self.assertEqual((ROOT / 'skills/copywriter-master' / relative).read_bytes(),
                                 (target / relative).read_bytes())
            (target / 'old-local-marker').write_text('previous installation')
            self.install(dest, '--dry-run')
            self.assertTrue((target / 'old-local-marker').exists())
            self.install(dest)
            self.assertFalse((target / 'old-local-marker').exists())
            self.assertTrue((target / 'references/quality-rubric.md').is_file())
            unrelated = dest / 'another-skill'
            unrelated.mkdir()
            (unrelated / 'keep').write_text('unrelated')
            self.install(dest, '--uninstall')
            self.assertFalse(target.exists())
            self.assertEqual((unrelated / 'keep').read_text(), 'unrelated')

    def test_project_install_targets_both_assistant_directories(self):
        with tempfile.TemporaryDirectory(prefix='copywriter project ') as tmp:
            for arguments in (['--project', '--dry-run'], ['--project'], ['--project', '--uninstall']):
                proc = subprocess.run(['bash', str(ROOT / 'install.sh'), *arguments], cwd=tmp,
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                for parent in ('.claude', '.agents'):
                    target = Path(tmp) / parent / 'skills/copywriter-master'
                    if '--dry-run' in arguments or '--uninstall' in arguments:
                        self.assertFalse(target.exists())
                    else:
                        for relative in ('SKILL.md', 'LICENSE', 'NOTICE', 'runtime-contract.json', 'rules/validation.json'):
                            self.assertEqual((ROOT / 'skills/copywriter-master' / relative).read_bytes(),
                                             (target / relative).read_bytes())

    def test_refuses_unknown_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            target = dest / 'copywriter-master'
            target.mkdir()
            (target / 'keep').write_text('unrecognized data')
            self.install(dest, success=False)
            self.assertEqual((target / 'keep').read_text(), 'unrecognized data')

    def test_rejects_source_overlap(self):
        self.install(ROOT / 'skills', '--dry-run', success=False)


if __name__ == '__main__':
    unittest.main()
