#!/usr/bin/env python3
"""Generate or validate GetDone's registry indexes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from development.tools.generate_registry_indexes import main

if __name__ == "__main__":
    raise SystemExit(main())
