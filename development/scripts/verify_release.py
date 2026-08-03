#!/usr/bin/env python3
"""Verify GetDone repository release metadata from a source checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from development.tools.verify_release import main

if __name__ == "__main__":
    raise SystemExit(main())
