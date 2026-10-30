#!/usr/bin/env python3
"""Lint, build and verify an installable skill archive without publishing it."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from copywriter_runtime.validation import InputError, ROOT, load_json, validate_copy, validate_structure


def lint():
    spec = importlib.util.spec_from_file_location('release_evaluate', ROOT / 'tools/evaluate.py')
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)
    ev.check_repository()
    skill = ROOT / 'skills/copywriter-master'
    contract = load_json(skill / 'runtime-contract.json')
    for field in ('schema_version', 'skill_contract_version', 'runtime_contract_version', 'brief_version',
                  'output_version', 'report_version', 'event_version', 'batch_version'):
        if contract.get(field) != '1.0':
            raise InputError('Contract version changed without a supported migration')
    if contract['logging_default'] != 'off' or not contract['human_review_required']:
        raise InputError('Contract must preserve opt-in logging and human review')
    for name in ('brief', 'output', 'batch', 'event'):
        schema = load_json(skill / f'schemas/{name}.schema.json')
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        if schema.get('additionalProperties') is not False:
            raise InputError('Contract schemas must reject unknown root fields')
    catalog = load_json(skill / 'rules/validation.json')
    codes = [r['code'] for r in catalog['rules']]
    if len(codes) != len(set(codes)):
        raise InputError('Rule codes must be unique')
    for rule in catalog['rules']:
        if rule['priority'] not in ('critical', 'high', 'medium', 'low') or rule['severity'] not in ('error', 'review'):
            raise InputError('Invalid rule risk/severity')
        if rule['category'] not in ('format', 'audience', 'offer', 'cta', 'evidence', 'compliance', 'privacy', 'clarity'):
            raise InputError('Invalid rule category')
        if not rule['remediation'].strip():
            raise InputError('Missing rule remediation')
        if rule.get('pattern'):
            re.compile(rule['pattern'])
    for file in skill.rglob('*'):
        if file.is_symlink():
            raise InputError('Release package must not contain symlinks')
    for path in ('docs/QUICKSTART.pt-BR.md', 'docs/QUICKSTART.en.md', 'docs/COMPATIBILITY.md',
                 'docs/ARCHITECTURE.md', 'docs/MAINTENANCE.md', 'docs/OBSERVABILITY.md'):
        if not (ROOT / path).is_file():
            raise InputError('Required operational documentation missing')
    corpus_path = ROOT / 'evaluation/operational-cases.json'
    corpus = load_json(corpus_path)
    for case in corpus['cases']:
        if case['evidence_type'] != 'synthetic':
            raise InputError('This regression corpus must not claim real customer evidence')
        brief = load_json(corpus_path.parent / case['brief'])
        good = validate_copy(brief, load_json(corpus_path.parent / case['good_draft']))
        bad = validate_copy(brief, load_json(corpus_path.parent / case['bad_draft']))
        if good['automated_checks'] != 'passed' or bad['automated_checks'] != 'failed':
            raise InputError('Sector regression expected status failed')
        if not set(case['expected_bad_codes']).issubset({f['code'] for f in bad['findings']}):
            raise InputError('Sector regression expected finding missing')
    # Check all repository Markdown local links, plus README release identity.
    for doc in [ROOT / 'README.md', * (ROOT / 'docs').glob('*.md')]:
        for link in re.findall(r'\]\(([^)]+)\)', doc.read_text(encoding='utf-8')):
            if '://' in link or link.startswith('#'):
                continue
            dest = (doc.parent / link.split('#')[0]).resolve()
            if not dest.is_relative_to(ROOT) or not dest.exists():
                raise InputError('Broken repository documentation link')
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if f'Version **{version}**' not in (ROOT / 'README.md').read_text(encoding='utf-8'):
        raise InputError('README release version differs from VERSION')
    print(f'Operational lint passed: {len(codes)} rules, {len(corpus["cases"])} sector regressions.')


def build(destination, expected_version=None):
    lint()
    version = (ROOT / 'VERSION').read_text().strip()
    if expected_version and version != expected_version.removeprefix('v'):
        raise InputError('Release tag/version does not match VERSION')
    dest = Path(destination)
    if dest.exists():
        raise InputError('Release destination exists; refuse to overwrite artifacts')
    skill = ROOT / 'skills/copywriter-master'
    files = sorted((p for p in skill.rglob('*') if p.is_file()), key=lambda p: p.relative_to(skill).as_posix())
    hashes = {f'copywriter-master/{p.relative_to(skill).as_posix()}': hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    with tempfile.TemporaryDirectory(prefix='.copywriter-release-', dir=dest.parent) as tmp:
        stage = Path(tmp)
        archive = stage / f'copywriter-master-{version}.zip'
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
            for p in files:
                name = f'copywriter-master/{p.relative_to(skill).as_posix()}'
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, p.read_bytes())
        manifest = {'schema_version': '1.0', 'version': version, 'archive': archive.name,
                    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'files': hashes}
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        (stage / 'SHA256SUMS').write_text(f'{manifest["archive_sha256"]}  {archive.name}\n', encoding='utf-8')
        # Reserve without replacing another process's output directory.
        dest.mkdir()
        try:
            import shutil
            for p in stage.iterdir():
                shutil.copyfile(p, dest / p.name)
        except OSError:
            shutil.rmtree(dest)
            raise
    verify(dest)
    return manifest


def verify(directory):
    dest = Path(directory)
    manifest = load_json(dest / 'manifest.json')
    if not isinstance(manifest, dict) or set(manifest) != {'schema_version', 'version', 'archive', 'archive_sha256', 'files'}:
        raise InputError('Invalid release manifest')
    if manifest['schema_version'] != '1.0' or not re.fullmatch(r'\d+\.\d+\.\d+', manifest['version']):
        raise InputError('Unsupported release manifest/version')
    if manifest['archive'] != f'copywriter-master-{manifest["version"]}.zip':
        raise InputError('Invalid archive filename')
    archive = dest / manifest['archive']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['archive_sha256']:
        raise InputError('Archive checksum mismatch')
    expected_sums = f'{manifest["archive_sha256"]}  {archive.name}\n'
    if (dest / 'SHA256SUMS').read_text(encoding='utf-8') != expected_sums:
        raise InputError('SHA256SUMS mismatch')
    required = {f'copywriter-master/{name}' for name in ('LICENSE', 'NOTICE', 'SKILL.md', 'runtime-contract.json')}
    if not isinstance(manifest['files'], dict) or not required.issubset(manifest['files']):
        raise InputError('Required package files missing')
    with zipfile.ZipFile(archive) as bundle:
        names = bundle.namelist()
        if len(names) != len(set(names)) or set(names) != set(manifest['files']):
            raise InputError('Archive contents differ from manifest')
        for name, expected in manifest['files'].items():
            from pathlib import PurePosixPath
            path = PurePosixPath(name)
            if path.is_absolute() or '..' in path.parts or not name.startswith('copywriter-master/'):
                raise InputError('Unsafe archive entry')
            if hashlib.sha256(bundle.read(name)).hexdigest() != expected:
                raise InputError('Package file hash mismatch')
    print(f'Verified release {manifest["version"]}: {len(names)} packaged files.')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check')
    p = sub.add_parser('build')
    p.add_argument('--out', required=True)
    p.add_argument('--expected-version')
    p = sub.add_parser('verify')
    p.add_argument('--directory', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'check':
            lint()
        elif args.command == 'build':
            build(args.out, args.expected_version)
        else:
            verify(args.directory)
    except (InputError, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        parser.exit(2, f'Error: {exc}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
