from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
compiler = shutil.which("g++")
if compiler is None:
    raise SystemExit("g++ is required for this rollout case")

with tempfile.TemporaryDirectory() as directory:
    executable = Path(directory) / "window_average_test"
    compile_result = subprocess.run(
        [
            compiler,
            "-std=c++20",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT / "include"),
            str(ROOT / "tests/window_average_test.cpp"),
            "-o",
            str(executable),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if compile_result.returncode != 0:
        raise SystemExit(compile_result.stdout + compile_result.stderr)
    completed = subprocess.run([str(executable)], check=False)
    raise SystemExit(completed.returncode)
