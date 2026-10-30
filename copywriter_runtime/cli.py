"""Offline workflow CLI: initialize examples, validate, batch and summarize opt-in logs."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile

from .observability import append_events, summarize
from .reporting import render
from .validation import InputError, ROOT, load_json, validate_copy, validate_structure


def emit(data, args):
    content = render(data, args.format)
    if args.out:
        with Path(args.out).open('x', encoding='utf-8') as stream:
            stream.write(content)
    else:
        print(content, end='')


def validate_command(args):
    report = validate_copy(load_json(args.brief), load_json(args.draft))
    emit(report, args)
    if args.log:
        append_events(args.log, [report])
    return 1 if report['automated_checks'] == 'failed' else 0


def init_example(locale, destination):
    dest = Path(destination)
    if dest.exists():
        raise InputError('Example destination already exists; choose a new directory')
    # Stage example files before reserving and copying into the destination.
    with tempfile.TemporaryDirectory(prefix='.copywriter-init-', dir=dest.parent) as tmp:
        stage = Path(tmp) / 'example'
        stage.mkdir()
        for kind in ('brief', 'output'):
            shutil.copyfile(ROOT / f'examples/validation/{kind}.{locale}.json', stage / f'{kind}.json')
        # Exclusive mkdir reserves the destination and avoids replacing another process's folder.
        dest.mkdir()
        try:
            for source in stage.iterdir():
                shutil.copyfile(source, dest / source.name)
        except OSError:
            shutil.rmtree(dest)
            raise
    return dest


def batch(manifest_path, destination, log=None):
    path = Path(manifest_path)
    manifest = load_json(path)
    validate_structure(manifest, 'batch')
    ids = [c['id'] for c in manifest['cases']]
    reserved = {'SUMMARY', 'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
    if len(ids) != len({cid.casefold() for cid in ids}) or any(cid.upper() in reserved for cid in ids):
        raise InputError('Batch case IDs must be unique ignoring case and must not use reserved filenames')
    dest = Path(destination)
    if dest.exists():
        raise InputError('Batch destination already exists; choose a new directory')
    results = []
    # Validate all inputs before creating report files; malformed cases cannot leave a partial batch.
    for case in manifest['cases']:
        report = validate_copy(load_json(path.parent / case['brief']), load_json(path.parent / case['draft']))
        results.append((case['id'], report))
    with tempfile.TemporaryDirectory(prefix='.copywriter-batch-', dir=dest.parent) as tmp:
        stage = Path(tmp) / 'reports'
        stage.mkdir()
        for cid, report in results:
            (stage / f'{cid}.json').write_text(render(report), encoding='utf-8')
            (stage / f'{cid}.md').write_text(render(report, 'markdown'), encoding='utf-8')
        summary = {'case_count': len(results), 'blocked_count': sum(r['automated_checks'] == 'failed' for _, r in results),
                   'human_review_required': True}
        (stage / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        # Reserve output; never replace an existing directory, including during a race.
        dest.mkdir()
        try:
            for source in stage.iterdir():
                shutil.copyfile(source, dest / source.name)
        except OSError:
            shutil.rmtree(dest)
            raise
    if log:
        append_events(log, [r for _, r in results])
    return summary


def add_validate_arguments(parser):
    parser.add_argument('--brief', required=True)
    parser.add_argument('--draft', required=True)
    parser.add_argument('--out', help='New report file; existing evidence is preserved')
    parser.add_argument('--format', choices=('json', 'markdown', 'html'), default='json')
    parser.add_argument('--log', help='Explicit opt-in local JSONL event path; raw copy is never logged')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init', help='Copy a working synthetic brief and draft into a new directory')
    p.add_argument('--example', choices=('pt-BR', 'en-US'), default='pt-BR')
    p.add_argument('--dest', required=True)
    add_validate_arguments(sub.add_parser('validate', help='Validate existing copy; does not generate it'))
    p = sub.add_parser('batch', help='Validate all manifest cases and save JSON/Markdown reports')
    p.add_argument('--manifest', required=True)
    p.add_argument('--out-dir', required=True)
    p.add_argument('--log')
    p = sub.add_parser('summary', help='Summarize explicitly logged validation events')
    p.add_argument('--log', required=True)
    p.add_argument('--out')
    p.add_argument('--format', choices=('json', 'markdown', 'html'), default='json')
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            print(f'Created synthetic example in {init_example(args.example, args.dest)}')
        elif args.command == 'validate':
            return validate_command(args)
        elif args.command == 'batch':
            summary = batch(args.manifest, args.out_dir, args.log)
            print(json.dumps(summary, indent=2))
            return 1 if summary['blocked_count'] else 0
        else:
            emit(summarize(args.log), args)
    except (InputError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')
    return 0
