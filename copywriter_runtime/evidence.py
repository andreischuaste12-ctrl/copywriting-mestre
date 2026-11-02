"""Evidence base: studies.json is the source of truth; evidence/<axis>.md files are generated from it.

Each study records what it found, an if/then rule, how to apply it, where it stops applying and how far its
citation has been checked. The lint rules mirror the skill's integrity rules: no unqualified guarantees, no
invented figures in example copy, and every study carries limits.
"""
from __future__ import annotations

import re

from .validation import InputError, ROOT, load_json

EVIDENCE_DIR = ROOT / 'skills/copywriter-master/references/evidence'
STUDIES = EVIDENCE_DIR / 'studies.json'
CITATION_STATES = ('supplied', 'index-checked', 'corrected')
RELATED_STATES = ('index-checked', 'confirm-before-quoting')
TRANSFER = ('adjacent', 'extrapolated')
STUDY_FIELDS = {'number', 'id', 'axis', 'topic', 'citation', 'citation_status', 'evidence_type', 'transfer', 'finding',
                'rule', 'practice', 'limits', 'caveats'}
OPTIONAL_FIELDS = {'example', 'related'}
CITATION_FIELDS = {'authors', 'year', 'title', 'venue', 'details'}
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
# Phrases that turn a heuristic into a guarantee. Studies must not teach the assistant to say them.
GUARANTEE = re.compile(r'\b(?:guarantees?|always (?:works|converts)|proven to convert|will convert)\b', re.IGNORECASE)


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise InputError(f'{where} must be nonempty text')
    return value


def load_studies():
    data = load_json(STUDIES)
    if data.get('schema_version') != '1.0':
        raise InputError('Unsupported evidence schema version')
    axes, studies = data.get('axes'), data.get('studies')
    if not isinstance(axes, list) or not axes or not isinstance(studies, list) or not studies:
        raise InputError('Evidence file needs axes and studies')
    axis_ids = set()
    for axis in axes:
        if not isinstance(axis, dict) or set(axis) != {'id', 'file', 'title', 'load_when'}:
            raise InputError('Each axis needs exactly: id, file, title, load_when')
        for field in axis:
            _text(axis[field], f'axis {field}')
        if axis['id'] in axis_ids or not SLUG.match(axis['id']) or not axis['file'].endswith('.md') or '/' in axis['file']:
            raise InputError(f'Invalid or duplicate axis {axis["id"]!r}')
        axis_ids.add(axis['id'])
    seen_ids, numbers = set(), []
    for study in studies:
        if not isinstance(study, dict):
            raise InputError('Each study must be an object')
        missing = STUDY_FIELDS - set(study)
        extra = set(study) - STUDY_FIELDS - OPTIONAL_FIELDS
        if missing or extra:
            raise InputError(f'Study {study.get("id")!r}: missing {sorted(missing)}, unexpected {sorted(extra)}')
        sid = study['id']
        if not isinstance(sid, str) or not SLUG.match(sid) or sid in seen_ids:
            raise InputError(f'Invalid or duplicate study id {sid!r}')
        seen_ids.add(sid)
        if type(study['number']) is not int or study['number'] < 1:
            raise InputError(f'{sid}: number must be a positive integer')
        numbers.append(study['number'])
        if study['axis'] not in axis_ids:
            raise InputError(f'{sid}: unknown axis {study["axis"]!r}')
        citation = study['citation']
        if not isinstance(citation, dict) or not CITATION_FIELDS <= set(citation) or set(citation) - CITATION_FIELDS - {'doi'}:
            raise InputError(f'{sid}: citation needs {sorted(CITATION_FIELDS)} and optionally doi')
        for field, value in citation.items():
            if field == 'year':
                if type(value) is not int or not 1800 < value < 2100:
                    raise InputError(f'{sid}: citation year is invalid')
            else:
                _text(value, f'{sid}: citation {field}')
        status = study['citation_status']
        if not isinstance(status, dict) or set(status) != {'state', 'note'} or status['state'] not in CITATION_STATES:
            raise InputError(f'{sid}: citation_status needs state in {CITATION_STATES} and a note')
        _text(status['note'], f'{sid}: citation_status note')
        if study['transfer'] not in TRANSFER:
            raise InputError(f'{sid}: transfer must be one of {TRANSFER}')
        for field in ('evidence_type', 'finding', 'practice'):
            _text(study[field], f'{sid}: {field}')
        rule = study['rule']
        if not isinstance(rule, dict) or set(rule) != {'if', 'then'}:
            raise InputError(f'{sid}: rule needs if and then')
        _text(rule['if'], f'{sid}: rule if')
        _text(rule['then'], f'{sid}: rule then')
        for field in ('limits', 'caveats'):
            values = study[field]
            if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
                raise InputError(f'{sid}: {field} must be a list of nonempty text')
        if not study['limits']:
            raise InputError(f'{sid}: every study needs at least one limit on where the rule stops applying')
        _text(study['topic'], f'{sid}: topic')
        for text in (study['finding'], rule['then'], study['practice']):
            if GUARANTEE.search(text):
                raise InputError(f'{sid}: avoid guarantee language in findings and rules')
        if 'example' in study:
            example = _text(study['example'], f'{sid}: example')
            if re.search(r'\d', re.sub(r'\[[^\]]*\]', '', example)):
                raise InputError(f'{sid}: example copy must use [placeholders], not concrete figures')
        for related in study.get('related', []):
            if not isinstance(related, dict) or set(related) != {'citation', 'status'} or related['status'] not in RELATED_STATES:
                raise InputError(f'{sid}: related entries need citation and status in {RELATED_STATES}')
            _text(related['citation'], f'{sid}: related citation')
    if sorted(numbers) != list(range(1, len(numbers) + 1)):
        raise InputError('Study numbers must be unique and contiguous starting at 1')
    for axis in axes:
        if not any(s['axis'] == axis['id'] for s in studies):
            raise InputError(f'Axis {axis["id"]} has no studies')
    return data


def _short_authors(authors):
    names = re.findall(r"((?:van |von |de )?[A-Z][A-Za-z'\-]+),\s+[A-Z]\.", authors)
    if len(names) > 2:
        return f'{names[0]} et al.'
    return ' & '.join(names) or authors


def _citation(study):
    c = study['citation']
    doi = f' https://doi.org/{c["doi"]}' if c.get('doi') else ''
    return f'{c["authors"]} ({c["year"]}). {c["title"]}. {c["venue"]}, {c["details"]}.{doi}'


def render_axis(data, axis):
    lines = [
        f'# {axis["title"]}',
        '',
        '<!-- Generated from studies.json by `python tools/references.py index`. Do not edit by hand. -->',
        '',
        'Each rule is a hypothesis conditioned on audience, channel and barrier, not a guarantee. Read '
        '[principles.md](principles.md) for how to weigh evidence, and apply the brief fidelity, claim and '
        'compliance rules in SKILL.md first. Where an entry says a number or attribution was corrected, use the corrected form.',
        '',
    ]
    for study in sorted((s for s in data['studies'] if s['axis'] == axis['id']), key=lambda s: s['number']):
        status = study['citation_status']
        lines += [
            f'## {study["number"]}. {study["topic"]} ({_short_authors(study["citation"]["authors"])}, {study["citation"]["year"]})',
            '',
            f'- **Finding:** {study["finding"]}',
            f'- **Rule:** if {study["rule"]["if"][0].lower() + study["rule"]["if"][1:].rstrip(".")}, '
            f'then {study["rule"]["then"][0].lower() + study["rule"]["then"][1:]}',
            f'- **Apply:** {study["practice"]}',
        ]
        if 'example' in study:
            lines.append(f'- **Pattern:** {study["example"]}')
        lines.append('- **Limits:** ' + ' '.join(study['limits']))
        if study['caveats']:
            lines.append('- **Caveats:** ' + ' '.join(study['caveats']))
        lines.append(f'- **Evidence:** {study["evidence_type"]}; transfer to commercial copy is {study["transfer"]}.')
        note = status['note'].rstrip('.')
        lines.append(f'- **Citation ({status["state"]}):** {_citation(study)} {note[0].upper() + note[1:]}.')
        for related in study.get('related', []):
            lines.append(f'- **Related ({related["status"]}):** {related["citation"]}')
        lines.append('')
    return '\n'.join(lines)


def generated_files(data=None):
    """Map of absolute path -> expected text for every file generated from studies.json."""
    data = data or load_studies()
    return {EVIDENCE_DIR / axis['file']: render_axis(data, axis) for axis in data['axes']}


def write_generated():
    written = []
    for path, text in generated_files().items():
        path.write_text(text, encoding='utf-8', newline='\n')
        written.append(path)
    return written


def check():
    data = load_studies()
    for path, text in generated_files(data).items():
        if not path.is_file() or path.read_text(encoding='utf-8') != text:
            raise InputError(f'{path.name} is stale or missing; run: python tools/references.py index')
    return data
