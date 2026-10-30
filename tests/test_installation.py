"""Check distributable attribution and preservation during installer operations."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('bash'), 'Bash required')
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
