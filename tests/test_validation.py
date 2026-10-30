"""Adversarial fixtures test deterministic draft checks, not model performance."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validate_copy', ROOT / 'tools/validate_copy.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.brief = validator.load_json(ROOT / 'examples/validation/brief.pt-BR.json')
        self.output = validator.load_json(ROOT / 'examples/validation/output.pt-BR.json')

    def check(self, code=None):
        report = validator.validate_copy(self.brief, self.output)
        if code:
            self.assertEqual(report['disposition'], 'blocked')
            self.assertIn(code, [f['code'] for f in report['findings']])
        return report

    def replace(self, old, new):
        self.output['items'][0]['text'] = self.output['items'][0]['text'].replace(old, new)

    def test_valid_examples_still_require_human_review_in_both_languages(self):
        for locale in ('pt-BR', 'en-US'):
            with self.subTest(locale=locale):
                brief = validator.load_json(ROOT / f'examples/validation/brief.{locale}.json')
                output = validator.load_json(ROOT / f'examples/validation/output.{locale}.json')
                result = validator.validate_copy(brief, output)
                self.assertEqual(result['automated_checks'], 'passed')
                self.assertEqual(result['disposition'], 'needs_human_review')
                self.assertTrue(result['human_review_required'])

    def test_altered_price_and_unprovided_number(self):
        self.replace('R$ 49', 'R$ 29')
        self.check('required_phrase')
        self.check('unprovided_number')

    def test_deceptive_suffix_does_not_satisfy_price(self):
        self.replace('R$ 49', 'R$ 490')
        self.check('required_phrase')

    def test_omitted_condition_is_blocked(self):
        self.replace('Cancele quando quiser; acesso até o fim do mês pago.', 'Cancele grátis.')
        self.check('required_phrase')

    def test_changed_deadline(self):
        deadline = 'Inscrições até 10/11/2026 às 18h.'
        self.brief['constraints']['required_phrases'].append(deadline)
        self.output['items'][0]['text'] += ' Inscrições até 11/11/2026 às 18h.'
        self.check('required_phrase')
        self.check('unprovided_number')

    def test_forbidden_trial_and_scarcity_number(self):
        self.output['items'][0]['text'] += ' Teste grátis. Últimas 2 vagas!'
        self.check('forbidden_phrase')
        self.check('unprovided_number')

    def test_exact_limits_count_accents_after_nfc_normalization(self):
        size = len(self.output['items'][0]['text'])
        self.brief['constraints']['max_characters_per_item'] = size
        self.brief['constraints']['max_total_characters'] = size
        self.output['items'][0]['text'] = unicodedata.normalize('NFD', self.output['items'][0]['text'])
        self.assertEqual(self.check()['total_characters'], size)
        self.output['items'][0]['text'] += '!'
        self.check('item_length')
        self.check('total_length')

    def test_each_item_must_contain_its_own_terms_and_cta(self):
        self.brief['constraints']['item_count'] = 2
        self.output['items'].append({'id': 'second', 'text': 'Pauta', 'claims': []})
        self.check('required_phrase')
        self.check('cta_mismatch')

    def test_output_identity_format_language_and_quantity(self):
        for field, value, code in [('brief_id', 'other', 'brief_id_mismatch'),
                                    ('format', 'cta', 'format_mismatch'),
                                    ('language', 'en-US', 'language_mismatch')]:
            with self.subTest(field=field):
                original = self.output[field]
                self.output[field] = value
                self.check(code)
                self.output[field] = original
        self.brief['constraints']['item_count'] = 2
        self.check('item_count')

    def test_claim_without_source_is_blocked(self):
        self.brief['claims'][0]['source_ids'] = []
        self.check('claim_without_source')

    def test_unknown_and_fabricated_claim_annotations_are_blocked(self):
        annotation = self.output['items'][0]['claims'][0]
        annotation['claim_id'] = 'invented'
        self.check('unknown_claim')
        annotation['claim_id'] = 'calendar'
        annotation['quote'] = 'Resultados garantidos.'
        self.check('quote_not_in_copy')
        self.check('claim_wording_changed')

    def test_missing_annotation_does_not_bypass_claim_check(self):
        self.output['items'][0]['claims'] = []
        self.brief['claims'][0]['source_ids'] = []
        self.check('unannotated_claim')
        self.check('claim_without_source')

    def test_duplicate_annotation_is_blocked(self):
        self.output['items'][0]['claims'] *= 2
        self.check('duplicate_annotation')

    def test_pending_regulated_claim_is_blocked_even_with_a_source(self):
        claim = self.brief['claims'][0]
        claim.update(kind='regulated', authorization={'status': 'pending', 'reference': ''})
        self.brief['category'] = 'health'
        self.check('authorization_pending')
        # Removing the annotation cannot authorize the same literal claim.
        self.output['items'][0]['claims'] = []
        self.check('authorization_pending')

    def test_confirmed_permission_still_needs_context_review(self):
        self.brief['claims'][0].update(kind='regulated', authorization={'status': 'confirmed', 'reference': 'Synthetic label reference'})
        self.brief['category'] = 'health'
        report = self.check()
        self.assertEqual(report['automated_checks'], 'passed')
        self.assertIn('category_review', [f['code'] for f in report['findings']])
        self.assertIn('sensitive_claim_review', [f['code'] for f in report['findings']])

    def test_unregistered_semantic_promise_is_never_certified(self):
        # No rule can prove an unrestricted paraphrase: the report must retain human review.
        self.output['items'][0]['text'] += ' Vai transformar sua carreira.'
        report = self.check()
        self.assertEqual(report['disposition'], 'needs_human_review')
        self.assertIn('semantic_review', [f['code'] for f in report['findings']])

    def test_sensitive_patterns_are_only_signals_and_privacy_is_blocked(self):
        for text, code in [(' Last chance!', 'scarcity_signal'), (' Cura garantida.', 'health_signal'),
                           (' Guaranteed income.', 'financial_signal'), (' Clientes dizem: excelente.', 'testimonial_signal')]:
            with self.subTest(code=code):
                output = copy.deepcopy(self.output)
                output['items'][0]['text'] += text
                report = validator.validate_copy(self.brief, output)
                self.assertIn(code, [f['code'] for f in report['findings']])
                self.assertEqual(report['disposition'], 'needs_human_review')
        self.output['items'][0]['text'] += ' ana@example.test'
        self.check('private_data_signal')

    def test_schema_rejects_attempt_to_override_trusted_rules(self):
        self.output['constraints'] = {'ignore_previous_instructions': True}
        with self.assertRaises(validator.InputError):
            self.check()

    def test_schema_rejects_bool_counts_and_blank_text(self):
        self.brief['constraints']['item_count'] = True
        with self.assertRaises(validator.InputError):
            self.check()
        self.brief['constraints']['item_count'] = 1
        self.output['items'][0]['text'] = '   '
        with self.assertRaises(validator.InputError):
            self.check()

    def test_ambiguous_ids_sources_and_conflicting_brief_are_invalid(self):
        for mutate in [lambda b: b['sources'].append(copy.deepcopy(b['sources'][0])),
                       lambda b: b['claims'][0]['source_ids'].append('unknown'),
                       lambda b: b['constraints']['forbidden_phrases'].append('R$ 49 por mês'),
                       lambda b: b['constraints']['forbidden_phrases'].append('Assinar o Pauta')]:
            with self.subTest(mutation=mutate):
                brief = copy.deepcopy(self.brief)
                mutate(brief)
                with self.assertRaises(validator.InputError):
                    validator.validate_copy(brief, self.output)

    def test_cli_exit_codes_report_file_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            brief_path, output_path, report_path = [Path(temp) / name for name in ('brief.json', 'output.json', 'report.json')]
            brief_path.write_text(json.dumps(self.brief), encoding='utf-8')
            def run(output, *extra):
                output_path.write_text(json.dumps(output), encoding='utf-8')
                return subprocess.run([sys.executable, str(ROOT / 'tools/validate_copy.py'),
                                       '--brief', str(brief_path), '--draft', str(output_path), *extra],
                                      capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(run(self.output).returncode, 0)
            self.assertEqual(run(self.output, '--out', str(report_path)).returncode, 0)
            original = report_path.read_bytes()
            self.assertEqual(run(self.output, '--out', str(report_path)).returncode, 2)
            self.assertEqual(report_path.read_bytes(), original)
            self.replace('R$ 49', 'R$ 29')
            self.assertEqual(run(self.output).returncode, 1)
            self.assertEqual(run([]).returncode, 2)

    def test_loader_rejects_duplicate_keys_and_nonstandard_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'invalid.json'
            for content in ('{"x": 1, "x": 2}', '{"x": NaN}', '{"x": Infinity}', '{'):
                path.write_text(content, encoding='utf-8')
                with self.assertRaises(validator.InputError):
                    validator.load_json(path)

    def test_report_is_bound_to_brief_and_output(self):
        before = self.check()
        self.brief['market'] = 'US'
        self.output['items'][0]['text'] += '!'
        after = self.check()
        self.assertNotEqual(before['brief_sha256'], after['brief_sha256'])
        self.assertNotEqual(before['output_sha256'], after['output_sha256'])


if __name__ == '__main__':
    unittest.main()
