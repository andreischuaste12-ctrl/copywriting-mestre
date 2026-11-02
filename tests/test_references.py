"""The reference registry must stay in step with the files, the profile index and the generated routing index."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from copywriter_runtime import references
from copywriter_runtime.validation import InputError

REAL = ROOT / 'skills/copywriter-master/references'


class ReferenceRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.refs = Path(self.tmp.name) / 'references'
        shutil.copytree(REAL, self.refs)
        patches = [mock.patch.object(references, 'REFERENCES', self.refs),
                   mock.patch.object(references, 'REGISTRY', self.refs / 'registry.json'),
                   mock.patch.object(references, 'INDEX', self.refs / 'index.md')]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def registry(self):
        return json.loads((self.refs / 'registry.json').read_text(encoding='utf-8'))

    def save(self, registry):
        (self.refs / 'registry.json').write_text(json.dumps(registry), encoding='utf-8')

    def test_repository_registry_is_consistent(self):
        references.check()

    def test_unregistered_file_is_rejected(self):
        (self.refs / 'new-topic.md').write_text('# New topic\n', encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'not in registry.json: new-topic.md'):
            references.check()

    def test_registered_file_missing_on_disk_is_rejected(self):
        (self.refs / 'humanization.md').unlink()
        with self.assertRaisesRegex(InputError, 'missing on disk: humanization.md'):
            references.check()

    def test_stale_generated_index_is_rejected_and_regenerated(self):
        (self.refs / 'index.md').write_text('# Reference index\n\nedited by hand\n', encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'stale'):
            references.check()
        references.write_index()
        references.check()

    def test_new_reference_flow_registers_and_routes_it(self):
        (self.refs / 'jurisdictions/portugal.md').write_text(
            '# Portugal\n\nThis is not legal advice.\n', encoding='utf-8')
        registry = self.registry()
        registry['references'].append({'path': 'jurisdictions/portugal.md', 'kind': 'jurisdiction', 'title': 'Portugal notes',
                                       'load_when': 'Portugal applies.', 'modes': ['Write', 'Review']})
        self.save(registry)
        references.write_index()
        references.check()
        self.assertIn('[Portugal notes](jurisdictions/portugal.md)', (self.refs / 'index.md').read_text(encoding='utf-8'))

    def test_jurisdiction_without_legal_disclaimer_is_rejected(self):
        path = self.refs / 'jurisdictions/brazil.md'
        path.write_text(path.read_text(encoding='utf-8').replace('not legal advice', 'a checklist'), encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'not legal advice'):
            references.check()

    def test_profile_without_source_note_is_rejected(self):
        path = self.refs / 'copywriters/schwab.md'
        text = path.read_text(encoding='utf-8')
        path.write_text(text[:text.rindex('Source note')].replace('source', 'origin'), encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'source note'):
            references.check()

    def test_file_over_word_budget_is_rejected(self):
        registry = self.registry()
        registry['budget']['max_words_per_file'] = 50
        self.save(registry)
        with self.assertRaisesRegex(InputError, 'budget is 50'):
            references.check()

    def test_profile_index_must_match_registered_profiles(self):
        path = self.refs / 'copywriters/index.md'
        path.write_text(path.read_text(encoding='utf-8').replace('| powers.md |', '| missing-profile.md |'), encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'disagree on profiles'):
            references.check()

    def test_registry_entry_validation(self):
        base = self.registry()
        mutations = {
            'duplicate path': lambda r: r['references'].append(dict(r['references'][0])),
            'unknown kind': lambda r: r['references'][0].update(kind='nonsense'),
            'bad mode': lambda r: r['references'][0].update(modes=['Dance']),
            'empty modes': lambda r: r['references'][0].update(modes=[]),
            'path escape': lambda r: r['references'][0].update(path='../SKILL.md'),
            'pipe in text': lambda r: r['references'][0].update(title='a | b'),
            'extra field': lambda r: r['references'][0].update(extra=1),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                registry = json.loads(json.dumps(base))
                mutate(registry)
                self.save(registry)
                with self.assertRaises(InputError):
                    references.load_registry()

    def test_cli_check_and_index(self):
        spec_path = ROOT / 'tools/references.py'
        import importlib.util
        spec = importlib.util.spec_from_file_location('references_tool', spec_path)
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(tool.main(['check']), 0)
            self.assertEqual(tool.main(['index']), 0)
        self.assertIn('Reference registry OK', out.getvalue())
        (self.refs / 'stray.md').write_text('# Stray\n', encoding='utf-8')
        with self.assertRaises(SystemExit) as raised:
            tool.main(['check'])
        self.assertEqual(raised.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
