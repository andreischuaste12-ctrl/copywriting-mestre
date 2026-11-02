"""Check distributable attribution and preservation during installer operations."""
import importlib.util
from pathlib import Path
import shutil
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


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


@unittest.skipUnless(shutil.which('bash') and shutil.which('curl') and shutil.which('unzip') and os.name != 'nt',
                     'Remote-install tests need bash, curl and unzip')
class RemoteInstallationTests(unittest.TestCase):
    """The remote path installs a pinned release archive and refuses anything whose checksum differs."""

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('remote_release', ROOT / 'tools/release.py')
        release = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(release)
        cls.tmp = tempfile.TemporaryDirectory(prefix='copywriter remote ')
        cls.mirror = Path(cls.tmp.name) / 'mirror'
        cls.manifest = release.build(cls.mirror)
        # Run the installer on its own, as `curl | bash` would, so it cannot find a local checkout.
        cls.alone = Path(cls.tmp.name) / 'alone'
        cls.alone.mkdir()
        shutil.copy(ROOT / 'install.sh', cls.alone / 'install.sh')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_remote(self, base, dest, *args):
        env = dict(os.environ, COPYWRITER_RELEASE_BASE_URL=base.as_uri())
        return subprocess.run(['bash', str(self.alone / 'install.sh'), '--dest', str(dest), *args],
                              capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)

    def copy_mirror(self):
        copy = Path(tempfile.mkdtemp(dir=self.tmp.name))
        for item in self.mirror.iterdir():
            shutil.copy(item, copy / item.name)
        return copy

    def test_installs_pinned_release_after_checksum_verification(self):
        dest = Path(tempfile.mkdtemp(dir=self.tmp.name)) / 'skills'
        proc = self.run_remote(self.mirror, dest)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual((ROOT / 'skills/copywriter-master/SKILL.md').read_bytes(),
                         (dest / 'copywriter-master/SKILL.md').read_bytes())
        self.assertTrue((dest / 'copywriter-master/references/registry.json').is_file())

    def test_wrong_listed_checksum_is_refused_and_nothing_is_installed(self):
        mirror = self.copy_mirror()
        name = self.manifest['archive']
        (mirror / 'SHA256SUMS').write_text(f"{'f' * 64}  {name}\n", encoding='utf-8')
        dest = Path(self.tmp.name) / 'refused-sums'
        proc = self.run_remote(mirror, dest)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('checksum mismatch', proc.stderr)
        self.assertFalse((dest / 'copywriter-master').exists())

    def test_altered_archive_is_refused(self):
        mirror = self.copy_mirror()
        archive = mirror / self.manifest['archive']
        archive.write_bytes(archive.read_bytes() + b'tampered')
        dest = Path(self.tmp.name) / 'refused-archive'
        proc = self.run_remote(mirror, dest)
        self.assertNotEqual(proc.returncode, 0)
        self.assertFalse((dest / 'copywriter-master').exists())

    def test_out_of_band_sha256_must_match(self):
        good = self.manifest['archive_sha256']
        dest = Path(self.tmp.name) / 'oob-wrong'
        proc = self.run_remote(self.mirror, dest, '--sha256', 'a' * 64)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('--sha256', proc.stderr)
        self.assertFalse((dest / 'copywriter-master').exists())
        dest = Path(self.tmp.name) / 'oob-right'
        proc = self.run_remote(self.mirror, dest, '--sha256', good.upper())
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_unpublished_release_fails_with_a_clear_message(self):
        empty = Path(tempfile.mkdtemp(dir=self.tmp.name))
        proc = self.run_remote(empty, Path(self.tmp.name) / 'none')
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('been published', proc.stderr)

    def test_installers_pin_the_current_version(self):
        version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
        self.assertIn(f'RELEASE_VERSION="{version}"', (ROOT / 'install.sh').read_text(encoding='utf-8'))
        self.assertIn(f"$ReleaseVersion = '{version}'", (ROOT / 'install.ps1').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
