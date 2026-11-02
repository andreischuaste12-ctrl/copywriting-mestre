"""Reference registry: single source for what exists under references/, when to load it, and its size budget.

`registry.json` is the source of truth. `references/index.md` is generated from it so the
assistant-facing routing table cannot drift from the files that are actually packaged.
"""
from __future__ import annotations

from pathlib import Path
import re

from .validation import InputError, ROOT, load_json

REFERENCES = ROOT / 'skills/copywriter-master/references'
REGISTRY = REFERENCES / 'registry.json'
INDEX = REFERENCES / 'index.md'
MODES = ('Diagnose', 'Write', 'Review', 'Research', 'Optimize')
ENTRY_FIELDS = {'path', 'kind', 'title', 'load_when', 'modes'}
# Generated index and templates are listed separately from the task-routing table.
MAINTENANCE_KINDS = ('template',)
SECTION_ORDER = (
    ('protocol', 'Protocol and quality gates'),
    ('guide', 'Strategy and craft'),
    ('process', 'Review processes'),
    ('sector', 'Sector and market review'),
    ('jurisdiction', 'Jurisdiction packs'),
    ('profile-index', 'Copywriter and framework profiles'),
    ('example', 'Examples'),
    ('source', 'Sources'),
)


def load_registry():
    registry = load_json(REGISTRY)
    if registry.get('schema_version') != '1.0':
        raise InputError('Unsupported reference registry version')
    budget = registry.get('budget', {})
    if not isinstance(budget.get('max_words_per_file'), int) or not isinstance(budget.get('max_profiles_per_task'), int):
        raise InputError('Reference registry budget is incomplete')
    kinds = registry.get('kinds')
    entries = registry.get('references')
    if not isinstance(kinds, list) or not isinstance(entries, list) or not entries:
        raise InputError('Reference registry needs kinds and references')
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise InputError('Each reference entry must have exactly: ' + ', '.join(sorted(ENTRY_FIELDS)))
        path = entry['path']
        if not isinstance(path, str) or not path.endswith('.md') or path.startswith('/') or '..' in Path(path).parts:
            raise InputError(f'Invalid reference path: {path!r}')
        if path in seen:
            raise InputError(f'Duplicate reference path: {path}')
        seen.add(path)
        if entry['kind'] not in kinds:
            raise InputError(f'{path}: unknown kind {entry["kind"]!r}')
        for field in ('title', 'load_when'):
            if not isinstance(entry[field], str) or not entry[field].strip() or '|' in entry[field]:
                raise InputError(f'{path}: {field} must be nonempty text without a pipe character')
        modes = entry['modes']
        if not isinstance(modes, list) or not modes or any(m not in MODES for m in modes) or len(modes) != len(set(modes)):
            raise InputError(f'{path}: modes must be a unique, nonempty subset of {MODES}')
    return registry


def render_index(registry):
    entries = registry['references']
    lines = [
        '# Reference index',
        '',
        '<!-- Generated from registry.json by `python tools/references.py index`. Do not edit by hand. -->',
        '',
        'Load a reference only when its condition applies. Prefer the smallest set that resolves the task; '
        f'use at most {registry["budget"]["max_profiles_per_task"]} copywriter profiles per task. '
        'SKILL.md and operating-protocol.md remain the authority on behavior.',
        '',
    ]
    for kind, heading in SECTION_ORDER:
        rows = [e for e in entries if e['kind'] == kind]
        if not rows:
            continue
        lines += [f'## {heading}', '', '| Reference | Load when | Modes |', '|---|---|---|']
        for e in sorted(rows, key=lambda e: e['path']):
            lines.append(f'| [{e["title"]}]({e["path"]}) | {e["load_when"]} | {", ".join(e["modes"])} |')
        lines.append('')
    profiles = sorted(e['path'] for e in entries if e['kind'] == 'profile')
    lines += [
        '## Individual profiles', '',
        f'{len(profiles)} profiles live in `copywriters/`. Open [copywriters/index.md](copywriters/index.md) first and '
        'then only the one or two profiles it selects.', '',
    ]
    templates = [e for e in entries if e['kind'] in MAINTENANCE_KINDS]
    if templates:
        lines += ['## For maintainers', '',
                  'Not loaded during normal tasks. Adding a reference means: copy a template, register it in '
                  '`registry.json`, then run `python tools/references.py index` and `python tools/release.py check`.', '']
        lines += [f'- [{e["title"]}]({e["path"]})' for e in sorted(templates, key=lambda e: e['path'])]
        lines.append('')
    return '\n'.join(lines)


def _words(path):
    return len(path.read_text(encoding='utf-8').split())


def check(registry=None):
    """Raise InputError on any registry/filesystem/structure drift; return the registry."""
    registry = registry or load_registry()
    entries = registry['references']
    registered = {e['path'] for e in entries}
    on_disk = {p.relative_to(REFERENCES).as_posix() for p in REFERENCES.rglob('*.md')}
    missing = sorted(registered - on_disk)
    unregistered = sorted(on_disk - registered)
    if missing:
        raise InputError('Registered references missing on disk: ' + ', '.join(missing))
    if unregistered:
        raise InputError('References not in registry.json: ' + ', '.join(unregistered))
    limit = registry['budget']['max_words_per_file']
    for entry in entries:
        path = REFERENCES / entry['path']
        words = _words(path)
        if words > limit:
            raise InputError(f'{entry["path"]} has {words} words; budget is {limit}. Split it and register the parts.')
        text = path.read_text(encoding='utf-8')
        if not text.startswith('# '):
            raise InputError(f'{entry["path"]} must start with a level-1 heading')
        if entry['kind'] == 'profile':
            lowered = text.lower()
            if 'consult' not in lowered or 'source' not in lowered:
                raise InputError(f'{entry["path"]} must say when to consult it and carry a source note')
        if entry['kind'] == 'jurisdiction' and 'not legal advice' not in text.lower():
            raise InputError(f'{entry["path"]} must state that it is not legal advice')
    profile_index = (REFERENCES / 'copywriters/index.md').read_text(encoding='utf-8')
    listed = set(re.findall(r'\|\s*([a-z0-9-]+\.md)\s*\|', profile_index))
    profile_files = {Path(e['path']).name for e in entries if e['kind'] == 'profile'}
    if listed != profile_files:
        diff = sorted(listed ^ profile_files)
        raise InputError('copywriters/index.md and the registry disagree on profiles: ' + ', '.join(diff))
    if not INDEX.is_file() or INDEX.read_text(encoding='utf-8') != render_index(registry):
        raise InputError('references/index.md is stale; run: python tools/references.py index')
    return registry


def write_index():
    registry = load_registry()
    text = render_index(registry)
    INDEX.write_text(text, encoding='utf-8', newline='\n')
    return INDEX
