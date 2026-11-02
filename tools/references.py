#!/usr/bin/env python3
"""Maintain the reference registry: regenerate generated references or check for drift."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from copywriter_runtime.references import check, write_index
from copywriter_runtime.validation import InputError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('index', help='Regenerate references/index.md and the evidence/*.md files from their sources')
    sub.add_parser('check', help='Fail if the registry, files, profiles or generated index disagree')
    args = parser.parse_args(argv)
    try:
        if args.command == 'index':
            print(f'Wrote {write_index()}')
        else:
            registry = check()
            print(f'Reference registry OK: {len(registry["references"])} references.')
    except (InputError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
