"""The evidence base must stay traceable, conditioned, free of invented figures and in step with its generated files."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from copywriter_runtime import evidence
from copywriter_runtime.validation import InputError

REAL = ROOT / 'skills/copywriter-master/references/evidence'


class EvidenceBaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / 'evidence'
        shutil.copytree(REAL, self.dir)
        for patch in (mock.patch.object(evidence, 'EVIDENCE_DIR', self.dir),
                      mock.patch.object(evidence, 'STUDIES', self.dir / 'studies.json')):
            patch.start()
            self.addCleanup(patch.stop)
        self.data = json.loads((self.dir / 'studies.json').read_text(encoding='utf-8'))

    def save(self, data):
        (self.dir / 'studies.json').write_text(json.dumps(data), encoding='utf-8')

    def study(self, data, sid):
        return next(s for s in data['studies'] if s['id'] == sid)

    def test_repository_evidence_is_valid_complete_and_generated(self):
        data = evidence.check()
        self.assertEqual([s['number'] for s in sorted(data['studies'], key=lambda s: s['number'])], list(range(1, 22)))
        for study in data['studies']:
            self.assertTrue(study['limits'], study['id'])
            self.assertTrue(study['rule']['if'] and study['rule']['then'], study['id'])

    def test_known_corrections_to_the_supplied_base_stay_in_place(self):
        rains = self.study(self.data, 'rains-2013')
        self.assertEqual((rains['citation_status']['state'], rains['citation']['details']), ('corrected', '39(1), 47-73'))
        self.assertIn('Revisited', rains['citation']['title'])
        okeefe = self.study(self.data, 'okeefe-hoeken-2021')
        self.assertEqual(okeefe['citation']['venue'], 'Frontiers in Psychology')
        self.assertEqual(okeefe['citation_status']['state'], 'corrected')
        # Claims that circulate in practitioner material but that we could not support must not appear in what the
        # assistant is told to do. Caveats may name them in order to say they are unsupported.
        guidance = ' '.join(f'{s["finding"]} {s["rule"]["if"]} {s["rule"]["then"]} {s["practice"]} {s.get("example", "")}'
                            for s in self.data['studies']).lower()
        for unsupported in ('highly durable', 'twice as fast', '2 vezes', '1,400', '1.400', 'r = 0.15',
                            'descriptive norms are generally stronger', 'always works'):
            self.assertNotIn(unsupported, guidance)

    def test_every_extrapolated_rule_names_where_it_stops_applying(self):
        for study in self.data['studies']:
            with self.subTest(study['id']):
                self.assertGreaterEqual(len(study['limits'][0]), 20)

    def test_invalid_studies_are_rejected(self):
        mutations = {
            'no limits': lambda d: self.study(d, 'sweller-1988').update(limits=[]),
            'unknown axis': lambda d: self.study(d, 'sweller-1988').update(axis='nowhere'),
            'bad citation state': lambda d: self.study(d, 'sweller-1988')['citation_status'].update(state='trusted'),
            'blank note': lambda d: self.study(d, 'sweller-1988')['citation_status'].update(note=' '),
            'missing field': lambda d: self.study(d, 'sweller-1988').pop('finding'),
            'extra field': lambda d: self.study(d, 'sweller-1988').update(roi='high'),
            'duplicate id': lambda d: self.study(d, 'sweller-1988').update(id='thaler-1985'),
            'gap in numbering': lambda d: self.study(d, 'sweller-1988').update(number=40),
            'bad transfer': lambda d: self.study(d, 'sweller-1988').update(transfer='direct'),
            'example with invented figure': lambda d: self.study(d, 'sweller-1988').update(example='Join 1,400 clinics today.'),
            'guarantee language': lambda d: self.study(d, 'sweller-1988')['rule'].update(then='guarantees a higher conversion'),
            'bad related status': lambda d: self.study(d, 'sweller-1988')['related'][0].update(status='verified'),
            'unnamed axis file': lambda d: d['axes'][0].update(file='nested/x.md'),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                data = copy.deepcopy(self.data)
                mutate(data)
                self.save(data)
                with self.assertRaises(InputError):
                    evidence.load_studies()

    def test_examples_may_use_placeholders_with_numbers_inside_brackets(self):
        data = copy.deepcopy(self.data)
        self.study(data, 'sweller-1988')['example'] = 'Join [verified number, source 1] teams.'
        self.save(data)
        evidence.load_studies()

    def test_stale_generated_markdown_is_detected_and_regenerated(self):
        path = self.dir / 'decision-and-pricing.md'
        path.write_text(path.read_text(encoding='utf-8') + '\nhand edit\n', encoding='utf-8')
        with self.assertRaisesRegex(InputError, 'stale'):
            evidence.check()
        evidence.write_generated()
        evidence.check()

    def test_editing_the_source_requires_regeneration(self):
        data = copy.deepcopy(self.data)
        self.study(data, 'thaler-1985')['practice'] = 'A different instruction.'
        self.save(data)
        with self.assertRaisesRegex(InputError, 'decision-and-pricing.md is stale'):
            evidence.check()


if __name__ == '__main__':
    unittest.main()
