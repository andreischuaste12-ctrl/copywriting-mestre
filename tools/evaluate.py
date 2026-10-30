#!/usr/bin/env python3
"""Prepare and score human-reviewed copy evaluations; never calls a model API."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SUITE_PATH = ROOT / 'evaluation/cases.json'
CONDITIONS = ('generic', 'baseline', 'candidate')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_suite():
    suite = json.loads(SUITE_PATH.read_text(encoding='utf-8'))
    if suite['schema_version'] != 1:
        raise ValueError('Unsupported case schema')
    ids = [c['id'] for c in suite['cases']]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Case IDs must be nonempty and unique')
    for c in suite['cases']:
        for field in ('id', 'mode', 'language', 'prompt', 'expected'):
            if not isinstance(c[field], str) or not c[field].strip():
                raise ValueError(f'Empty or invalid case field: {field}')
    return suite


def skill_digest(folder):
    if not (folder / 'SKILL.md').is_file():
        raise ValueError('Skill directory must contain SKILL.md')
    # Hash names and lengths too, so renamed files and ambiguous concatenations differ.
    payload = bytearray()
    for p in sorted(folder.rglob('*')):
        if p.is_file():
            for part in (p.relative_to(folder).as_posix().encode(), p.read_bytes()):
                payload.extend(len(part).to_bytes(8, 'big'))
                payload.extend(part)
    return digest(payload)


def check_repository():
    suite = load_suite()
    folder = ROOT / 'skills/copywriter-master'
    text = (folder / 'SKILL.md').read_text(encoding='utf-8')
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('VERSION must be a semantic version')
    if f'  version: {version}\n' not in text or 'license: Apache-2.0\n' not in text:
        raise ValueError('Skill metadata must match VERSION and Apache-2.0')
    if '  author: Andrei Schuaste\n' not in text:
        raise ValueError('Skill author attribution missing')
    rubric = (folder / 'references/quality-rubric.md').read_text(encoding='utf-8')
    if f'Rubric version: {suite["rubric_version"]}.' not in rubric:
        raise ValueError('Case suite must match the separately versioned rubric')
    for name in ('brief', 'output'):
        schema = json.loads((folder / 'schemas' / f'{name}.schema.json').read_text(encoding='utf-8'))
        if schema.get('$schema') != 'https://json-schema.org/draft/2020-12/schema':
            raise ValueError('Local validation schemas must declare Draft 2020-12')
    for name in ('LICENSE', 'NOTICE'):
        if (ROOT / name).read_bytes() != (folder / name).read_bytes():
            raise ValueError(f'Installable {name} differs from repository copy')
    if 'Copyright 2026 Andrei Schuaste' not in (ROOT / 'NOTICE').read_text(encoding='utf-8'):
        raise ValueError('Copyright holder missing')
    # Resolve relative Markdown links in the installable package, never remote links.
    for p in folder.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'):
                continue
            resolved = (p.parent / target.split('#')[0]).resolve()
            if not resolved.is_relative_to(folder.resolve()) or not resolved.exists():
                raise ValueError(f'Broken or escaping package link in {p.relative_to(ROOT)}: {target}')
    print(f'Checked version {version}, {len(suite["cases"])} fixed cases, package links, and license attribution.')


def prepare(args):
    suite = load_suite()
    if args.condition == 'generic' and args.skill_dir:
        raise ValueError('Generic condition does not load a skill directory')
    if args.condition == 'baseline' and not args.skill_dir:
        raise ValueError('Baseline condition requires the historical --skill-dir')
    skill = Path(args.skill_dir).resolve() if args.skill_dir else ROOT / 'skills/copywriter-master'
    fingerprint = None if args.condition == 'generic' else skill_digest(skill)
    rev = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    run = {
        'schema_version': 1,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'condition': args.condition,
        'model': args.model,
        'settings': args.settings,
        'repetition': args.repetition,
        'repository_commit': rev.stdout.strip() or None,
        'skill_sha256': fingerprint,
        'suite_sha256': digest(SUITE_PATH.read_bytes()),
        'rubric_version': suite['rubric_version'],
        'reviewer': '',
        'records': [{
            'case_id': c['id'], 'prompt': c['prompt'], 'expected': c['expected'],
            'response': '', 'scores': {d: None for d in suite['dimensions']},
            'hard_failures': {f: None for f in suite['hard_failures']}, 'review_note': '',
        } for c in suite['cases']],
    }
    with Path(args.out).open('x', encoding='utf-8') as f:
        json.dump(run, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'Prepared {len(run["records"])} unexecuted cases in {args.out}; no responses or scores generated.')


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def score_run(run):
    if not isinstance(run, dict):
        raise ValueError("Run must be a JSON object")
    suite = load_suite()
    if run.get('schema_version') != 1:
        raise ValueError('Unsupported run schema')
    if run.get('suite_sha256') != digest(SUITE_PATH.read_bytes()) or run.get('rubric_version') != suite['rubric_version']:
        raise ValueError('Run belongs to a different case suite or rubric')
    if run.get('condition') not in CONDITIONS:
        raise ValueError('Invalid benchmark condition')
    for field in ('model', 'settings', 'reviewer'):
        if not nonempty(run.get(field)):
            raise ValueError(f'Missing {field}; complete the run and human review first')
    if type(run.get('repetition')) is not int or run['repetition'] < 1:
        raise ValueError('Repetition must be a positive integer')
    fp = run.get('skill_sha256')
    if run['condition'] == 'generic':
        if fp is not None:
            raise ValueError('Generic condition must not include a skill fingerprint')
    elif not isinstance(fp, str) or not re.fullmatch('[0-9a-f]{64}', fp):
        raise ValueError('Missing or invalid skill fingerprint')
    records = run.get('records')
    if not isinstance(records, list) or any(not isinstance(x, dict) for x in records):
        raise ValueError('Records must be a list of case objects')
    ids = [x.get('case_id') for x in records]
    expected = {c['id']: c for c in suite['cases']}
    if len(ids) != len(expected) or set(ids) != set(expected):
        raise ValueError('Run must contain each fixed case exactly once')
    rows = []
    for rec in records:
        cid = rec['case_id']
        if rec.get('prompt') != expected[cid]['prompt'] or rec.get('expected') != expected[cid]['expected']:
            raise ValueError(f'{cid}: prompt or expected criteria changed')
        if not nonempty(rec.get('response')) or not nonempty(rec.get('review_note')):
            raise ValueError(f'{cid}: missing actual response or review rationale')
        scores = rec.get('scores')
        if not isinstance(scores, dict) or set(scores) != set(suite['dimensions']):
            raise ValueError(f'{cid}: score all eight rubric dimensions')
        if any(type(v) is not int or v not in (0, 1, 2) for v in scores.values()):
            raise ValueError(f'{cid}: scores must be integers 0, 1 or 2, not booleans')
        failures = rec.get('hard_failures')
        if not isinstance(failures, dict) or set(failures) != set(suite['hard_failures']):
            raise ValueError(f'{cid}: review all hard failures')
        if any(type(v) is not bool for v in failures.values()):
            raise ValueError(f'{cid}: hard failures must be explicitly true or false')
        total = sum(scores.values())
        blockers = [k for k, v in failures.items() if v]
        passed = total >= 13 and min(scores.values()) > 0 and not blockers
        rows.append({'case_id': cid, 'total': total, 'passed': passed, 'hard_failures': blockers,
                     'zero_dimensions': [k for k, v in scores.items() if v == 0]})
    return {
        'evaluation_type': 'human-reviewed editorial quality; not conversion evidence',
        'condition': run['condition'], 'model': run['model'], 'settings': run['settings'],
        'repetition': run['repetition'], 'reviewer': run['reviewer'],
        'skill_sha256': fp, 'suite_sha256': run['suite_sha256'], 'rubric_version': run['rubric_version'],
        'case_count': len(rows), 'passed_count': sum(x['passed'] for x in rows),
        'mean_score': round(sum(x['total'] for x in rows) / len(rows), 3),
        'all_passed': all(x['passed'] for x in rows), 'cases': rows,
    }


def compare_runs(runs):
    """Summarize actual reviewed runs; never fabricate responses or infer conversion lift."""
    if not runs:
        raise ValueError('At least one completed run is required')
    reports = [score_run(run) for run in runs]
    contexts = {(r['model'], r['settings'], r['suite_sha256'], r['rubric_version']) for r in reports}
    if len(contexts) != 1:
        raise ValueError('Comparison requires identical model, settings, suite and rubric')
    seen = set()
    fingerprints = {}
    groups = {c: [] for c in CONDITIONS}
    for report in reports:
        key = (report['condition'], report['repetition'])
        if key in seen:
            raise ValueError('Duplicate condition/repetition would count evidence twice')
        seen.add(key)
        cond = report['condition']
        previous = fingerprints.setdefault(cond, report['skill_sha256'])
        if previous != report['skill_sha256']:
            raise ValueError('Do not pool different skill fingerprints in one condition')
        groups[cond].append(report)
    repetitions = [{r['repetition'] for r in groups[c]} for c in CONDITIONS]
    complete = len(repetitions[0]) >= 3 and all(r == repetitions[0] for r in repetitions)
    if fingerprints.get('baseline') and fingerprints.get('baseline') == fingerprints.get('candidate'):
        raise ValueError('Baseline and candidate fingerprints are identical')
    cells = []
    for cond, rows in groups.items():
        for cid in [c['id'] for c in load_suite()['cases']]:
            values = [next(c for c in r['cases'] if c['case_id'] == cid) for r in rows]
            if not values:
                continue
            cells.append({'condition': cond, 'case_id': cid, 'runs': len(values),
                          'mean_score': sum(v['total'] for v in values) / len(values),
                          'score_min': min(v['total'] for v in values), 'score_max': max(v['total'] for v in values),
                          'pass_rate': sum(v['passed'] for v in values) / len(values),
                          'hard_failures': sum(len(v['hard_failures']) for v in values)})
    return {'comparison_status': 'complete' if complete else 'incomplete',
            'model': reports[0]['model'], 'settings': reports[0]['settings'],
            'suite_sha256': reports[0]['suite_sha256'], 'rubric_version': reports[0]['rubric_version'],
            'skill_fingerprints': fingerprints, 'run_count': len(reports), 'cases': cells,
            'limitation': 'Human editorial ratings only, not conversion evidence. Complete means matched repetitions, not proven improvement.'}


def render_comparison(report, format):
    if format == 'json':
        return json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    lines = ['# Editorial benchmark comparison', '', 'Status: ' + report['comparison_status'],
             'Model: ' + report['model'], 'Settings: ' + report['settings'], '',
             '| Condition | Case | Runs | Mean / 16 | Range | Pass rate | Hard failures |', '|---|---|---|---|---|---|---|']
    for row in report['cases']:
        lines.append(f"| {row['condition']} | {row['case_id']} | {row['runs']} | {row['mean_score']:.2f} | {row['score_min']}–{row['score_max']} | {row['pass_rate']:.1%} | {row['hard_failures']} |")
    lines += ['', report['limitation']]
    text = '\n'.join(lines) + '\n'
    if format == 'html':
        import html
        return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Editorial benchmark</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px}pre{white-space:pre-wrap;line-height:1.6}</style><body><pre>' + html.escape(text) + '</pre></body></html>\n'
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check', help='Validate package, cases, versions, links and legal files')
    p = sub.add_parser('prepare', help='Create an empty manual benchmark run; does not call an API')
    p.add_argument('--condition', choices=CONDITIONS, required=True)
    p.add_argument('--model', required=True, help='Exact model/provider identifier')
    p.add_argument('--settings', required=True, help='Generation settings, tool availability, or explicit platform defaults')
    p.add_argument('--repetition', type=int, default=1)
    p.add_argument('--skill-dir')
    p.add_argument('--out', required=True)
    p = sub.add_parser('score', help='Score a completed human-reviewed run')
    p.add_argument('run')
    p.add_argument('--out', help='New report path; refuses to overwrite existing files')
    p = sub.add_parser('compare', help='Compare completed reviewed runs; no model API calls')
    p.add_argument('runs', nargs='+')
    p.add_argument('--out', required=True)
    p.add_argument('--format', choices=('json', 'markdown', 'html'), default='json')
    args = parser.parse_args()
    try:
        if args.command == 'check':
            check_repository()
        elif args.command == 'prepare':
            if args.repetition < 1 or not nonempty(args.model) or not nonempty(args.settings):
                raise ValueError('Provide model, settings and a positive repetition')
            prepare(args)
        elif args.command == 'compare':
            report = compare_runs([json.loads(Path(p).read_text(encoding='utf-8')) for p in args.runs])
            with Path(args.out).open('x', encoding='utf-8') as stream:
                stream.write(render_comparison(report, args.format))
            return 0 if report['comparison_status'] == 'complete' else 1
        else:
            report = score_run(json.loads(Path(args.run).read_text(encoding='utf-8')))
            output = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
            if args.out:
                with Path(args.out).open('x', encoding='utf-8') as f:
                    f.write(output)
            else:
                print(output, end='')
            return 0 if report['all_passed'] else 1
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
