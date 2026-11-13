"""Lesson 14.3.8: the finance report for the 500-unit fleet, and the project packed as one runnable file.

The fleet is generated (GridCap is fictional); the code is snapshot steps/08.
"""

import filecmp
import subprocess
import sys
import tempfile
import zipapp
from pathlib import Path

import steps

steps.use(8)
from renewal.cli import main                            # noqa: E402

print("$ renewal --units 500")
main(["--units", "500"])

with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "src"
    (source / "renewal").mkdir(parents=True)
    for module in sorted((steps.step_dir(8) / "renewal").glob("*.py")):
        (source / "renewal" / module.name).write_bytes(module.read_bytes())
    archive = Path(tmp) / "renewal.pyz"
    zipapp.create_archive(source, archive, main="renewal.cli:main")
    print(f"packed {len(list((source / 'renewal').glob('*.py')))} modules into renewal.pyz")
    out = Path(tmp) / "plan_30.md"
    done = subprocess.run([sys.executable, str(archive), "--units", "30", "--budget", "1200", "--gap", "0",
                           "--out", str(out)], capture_output=True, text=True)
    golden = steps.step_dir(8) / "tests" / "golden" / "plan_30.md"
    print(f"renewal.pyz exit {done.returncode}; report equals the golden file: {filecmp.cmp(out, golden, shallow=False)}")

steps.show(8)
