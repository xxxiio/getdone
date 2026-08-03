#!/usr/bin/env python3
"""Validate GetDone's repository workflow and template front matter."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from development.tools.validate_frontmatter import main

if __name__ == "__main__":
    raise SystemExit(main())
