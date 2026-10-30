#!/usr/bin/env python3
"""Check a structured draft against a trusted brief, locally, without a model API."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'skills/copywriter-master/schemas'
# Preserve separators: 2,300 is not silently rewritten as 2300 or 2.300.
NUMBER = re.compile(r'(?<!\w)\d+(?:[.,:/-]\d+)*(?:\s*%)?(?!\w)')
# Signals require review; their presence does not establish a false or illegal claim.



class InputError(ValueError):
    """Invalid structured input; not a copy-quality failure."""


def normalize(text):
    return ' '.join(unicodedata.normalize('NFC', text).casefold().split())


def contains(text, phrase):
    text, phrase = normalize(text), normalize(phrase)
    left = r'(?<!\w)' if phrase[0].isalnum() or phrase[0] == '_' else ''
    right = r'(?!\w)' if phrase[-1].isalnum() or phrase[-1] == '_' else ''
    return re.search(left + re.escape(phrase) + right, text) is not None


def load_json(path):
    # Reject duplicate keys and nonstandard constants instead of accepting ambiguous input.
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InputError('Duplicate JSON keys are not accepted')
            result[key] = value
        return result
    def invalid_constant(value):
        raise InputError('Nonstandard JSON constants are not accepted')
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                          parse_constant=invalid_constant)
    except InputError:
        raise
    except json.JSONDecodeError as exc:
        raise InputError(f'Invalid JSON at line {exc.lineno}, column {exc.colno}') from exc
    except (OSError, UnicodeError) as exc:
        raise InputError('Cannot read input as UTF-8 JSON') from exc


def validate_structure(data, name):
    if Draft202012Validator is None:
        raise InputError('Install the optional validator: python -m pip install -r requirements-validation.txt')
    schema = load_json(SCHEMAS / f'{name}.schema.json')
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(list(e.absolute_path)))
    if errors:
        paths = [f'{name}.' + '.'.join(map(str, e.absolute_path)) + ': ' + f'violates {e.validator}' for e in errors]
        raise InputError('; '.join(paths))


def unique_ids(records, label):
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        raise InputError(f'Duplicate {label} IDs')


def check_contract(brief, output):
    validate_structure(brief, 'brief')
    validate_structure(output, 'output')
    unique_ids(brief['sources'], 'source')
    unique_ids(brief['claims'], 'claim')
    unique_ids(output['items'], 'item')
    sources = {s['id'] for s in brief['sources']}
    for claim in brief['claims']:
        if set(claim['source_ids']) - sources:
            raise InputError(f'Claim {claim["id"]} references an unknown source')
        if claim['kind'] == 'regulated' and claim['authorization']['status'] == 'not_applicable':
            raise InputError(f'Regulated claim {claim["id"]} must declare confirmed or pending authorization')
    for key in ('required_phrases', 'forbidden_phrases'):
        phrases = brief['constraints'][key]
        if len(phrases) != len({normalize(p) for p in phrases}):
            raise InputError(f'Duplicate normalized {key}')
    required = brief['constraints']['required_phrases']
    forbidden = brief['constraints']['forbidden_phrases']
    # No acceptable CTA, or a mandatory phrase itself forbidden, is a contradictory brief.
    if any(contains(r, f) for r in required for f in forbidden):
        raise InputError('A required phrase contains a forbidden phrase')
    if all(any(contains(c, f) for f in forbidden) for c in brief['cta']['accepted_phrases']):
        raise InputError('All accepted CTAs contain forbidden phrases')
    return {c['id']: c for c in brief['claims']}


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def validate_copy(brief, output):
    claims = check_contract(brief, output)
    catalog = load_json(ROOT / 'skills/copywriter-master/rules/validation.json')
    rules = {rule['code']: rule for rule in catalog['rules']}
    findings = []
    def add(code, severity, message, item_id=None):
        rule = rules[code]
        if severity != rule['severity']:
            raise InputError('Rule catalog severity differs from runtime implementation')
        finding = {'code': code, 'severity': severity, 'message': message,
                   'category': rule['category'], 'priority': rule['priority'], 'remediation': rule['remediation']}
        if item_id is not None:
            finding['item_id'] = item_id
        findings.append(finding)
    for key, expected in [('brief_id', brief['id']), ('language', brief['language']), ('format', brief['format'])]:
        if output[key] != expected:
            add(f'{key}_mismatch', 'error', f'Output {key} must match the trusted brief.')
    constraints = brief['constraints']
    if len(output['items']) != constraints['item_count']:
        add('item_count', 'error', 'Output item count differs from the brief.')
    all_text = [unicodedata.normalize('NFC', i['text']) for i in output['items']]
    total_chars = sum(map(len, all_text))
    if 'max_total_characters' in constraints and total_chars > constraints['max_total_characters']:
        add('total_length', 'error', 'Combined item text exceeds the total character limit.')
    trusted_text = brief['offer']['facts'] + [c['text'] for c in brief['claims']]
    trusted_text += constraints['required_phrases'] + brief['cta']['accepted_phrases'] + [brief['offer']['name']]
    allowed_numbers = {normalize(m.group()) for text in trusted_text for m in NUMBER.finditer(text)}
    for item, text in zip(output['items'], all_text):
        iid = item['id']
        if 'max_characters_per_item' in constraints and len(text) > constraints['max_characters_per_item']:
            add('item_length', 'error', 'Item exceeds its character limit.', iid)
        for phrase in constraints['required_phrases']:
            if not contains(text, phrase):
                add('required_phrase', 'error', 'A required price, date, condition or phrase is missing or changed.', iid)
        for phrase in constraints['forbidden_phrases']:
            if contains(text, phrase):
                add('forbidden_phrase', 'error', 'A phrase forbidden by the brief appears in the item.', iid)
        if not any(contains(text, c) for c in brief['cta']['accepted_phrases']):
            add('cta_mismatch', 'error', 'No accepted CTA phrase appears in the item.', iid)
        if any(normalize(m.group()) not in allowed_numbers for m in NUMBER.finditer(text)):
            add('unprovided_number', 'error', 'A numeric token was not provided in trusted offer/claim/constraint/CTA text.', iid)
        # Never trust a model's claim registry or treat a source reference as verification.
        annotated = set()
        for annotation in item['claims']:
            cid = annotation['claim_id']
            if cid in annotated:
                add('duplicate_annotation', 'error', 'The same claim was annotated more than once in an item.', iid)
            annotated.add(cid)
            if not contains(text, annotation['quote']):
                add('quote_not_in_copy', 'error', 'Claim quote is absent from this item.', iid)
            if cid not in claims:
                add('unknown_claim', 'error', 'Output references a claim absent from the trusted brief.', iid)
                continue
            claim = claims[cid]
            if normalize(annotation['quote']) != normalize(claim['text']):
                add('claim_wording_changed', 'error', 'Claim quote differs from registered wording; register a reviewed revision first.', iid)
        for cid, claim in claims.items():
            present = contains(text, claim['text']) or cid in annotated
            if not present:
                continue
            if cid not in annotated:
                add('unannotated_claim', 'error', 'A registered claim appears without its output annotation.', iid)
            if not claim['source_ids']:
                add('claim_without_source', 'error', 'A used claim has no registered supporting source.', iid)
            if claim['authorization']['status'] == 'pending':
                add('authorization_pending', 'error', 'A held claim appears in the draft before authorization is confirmed.', iid)
            if claim['kind'] in ('regulated', 'testimonial', 'scarcity'):
                add('sensitive_claim_review', 'review', 'Verify current permission, scope, consent and conditions for this claim.', iid)
        for rule in catalog['rules']:
            code, pattern = rule['code'], rule.get('pattern')
            if pattern and re.search(pattern, normalize(text)):
                severity = 'error' if code == 'private_data_signal' else 'review'
                add(code, severity, 'Pattern signal found; check its context. Pattern matching is not semantic verification.', iid)
    if brief['category'] != 'general':
        add('category_review', 'review', 'The stated category requires current market/channel and claim review.')
    # Always retain human review: unannotated paraphrases, context and actual language are not proven by these rules.
    add('semantic_review', 'review', 'Review factual meaning, source validity, real language, implied claims and legal permission; these cannot be certified by this validator.')
    priorities = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    findings.sort(key=lambda f: (priorities[f['priority']], f['code'], f.get('item_id', '')))
    blocked = any(f['severity'] == 'error' for f in findings)
    return {'schema_version': '1.0', 'validator_version': (ROOT / 'VERSION').read_text().strip(),
            'runtime_contract_version': '1.0', 'rule_catalog_version': catalog['version'],
            'rule_catalog_sha256': fingerprint(catalog),
            'brief_id': brief['id'], 'brief_sha256': fingerprint(brief), 'output_sha256': fingerprint(output),
            'automated_checks': 'failed' if blocked else 'passed',
            'disposition': 'blocked' if blocked else 'needs_human_review', 'human_review_required': True,
            'character_counts': {i['id']: len(t) for i, t in zip(output['items'], all_text)},
            'total_characters': total_chars, 'findings': findings}

