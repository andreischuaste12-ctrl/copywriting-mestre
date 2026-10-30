#!/usr/bin/env python3
"""Offline Copywriter Master CLI."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from copywriter_runtime.cli import main

if __name__ == '__main__':
    sys.exit(main())
