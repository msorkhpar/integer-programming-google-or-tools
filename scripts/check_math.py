"""Parse every formula of the given lessons with the KaTeX the site ships, and name each one it refuses.

    python3 scripts/check_math.py 01-optimization-mindset 26-multi-period-timing

Display formulas are ```math fences; inline ones are $`...`$ spans (docs/AUTHORING.md). KaTeX is
read from the StudyForge checkout beside this repository (env STUDYFORGE, default ../studyforge),
and run with Node, so a formula that would fall back to raw code on the page fails here first.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KATEX = Path(os.environ.get("STUDYFORGE", ROOT.parent / "studyforge")) / "src/studyforge/render/assets/katex.min.js"
DISPLAY = re.compile(r"^```math\n(.*?)^```", re.S | re.M)
INLINE = re.compile(r"\$`([^`]+)`\$")

NODE = r"""
const fs = require("fs");
global.window = undefined;
const katex = (function () { const module = { exports: {} }; const exports = module.exports;
  eval(fs.readFileSync(process.argv[1], "utf8")); return module.exports.default || module.exports; })();
const items = JSON.parse(fs.readFileSync(0, "utf8"));
const bad = [];
for (const [where, tex, display] of items) {
  try { katex.renderToString(tex, { displayMode: display, throwOnError: true }); }
  catch (e) { bad.push(where + ": " + e.message.split("\n")[0]); }
}
console.log(JSON.stringify(bad));
"""


def formulas(lesson: Path):
    text = lesson.read_text(encoding="utf-8")
    rel = lesson.relative_to(ROOT)
    for m in DISPLAY.finditer(text):
        yield f"{rel}:{text[:m.start()].count(chr(10)) + 1}", m.group(1), True
    for m in INLINE.finditer(text):
        yield f"{rel}:{text[:m.start()].count(chr(10)) + 1}", m.group(1), False


def main(argv: list[str]) -> int:
    lessons = [p for a in argv for p in (
        [ROOT / a] if (ROOT / a).is_file()
        else sorted((ROOT / a).glob("README_*.md")) + sorted((ROOT / a).rglob("statement.md")))]
    items = [f for lesson in lessons for f in formulas(lesson)]
    done = subprocess.run(["node", "-e", NODE, str(KATEX)], input=json.dumps(items), capture_output=True, text=True)
    if done.returncode:
        print(done.stderr)
        return 2
    bad = json.loads(done.stdout)
    for line in bad:
        print(line)
    print(f"{len(items)} formulas, {len(bad)} refused")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
