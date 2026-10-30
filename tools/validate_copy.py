#!/usr/bin/env python3
"""Backward-compatible version 1.2 entry point; implementation lives in the runtime."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from copywriter_runtime.cli import add_validate_arguments, validate_command
from copywriter_runtime.validation import InputError, contains, fingerprint, load_json, normalize, validate_copy, validate_structure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_validate_arguments(parser)
    args = parser.parse_args()
    try:
        return validate_command(args)
    except (InputError, OSError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    sys.exit(main())
