"""Check that a lesson shows only code that ran and output that code printed.

    python3 scripts/verify_lessons.py 01-optimization-mindset [26-multi-period-timing ...]
    python3 scripts/verify_lessons.py --all

For each module it runs every program in `<module>/src/*.py` (with `00-base` and `<module>/src` on
the path, from the course root), then reads every `README_S.M.L.md` lesson and checks:

* every ```python fence is lifted from a program in `src/` (each non-blank line, in order, after
  removing the common indent), so no code on the page is unrun;
* every ```text fence is printed by some program of the module (its lines appear, in order and
  contiguous, in one program's output), so no output on the page is invented;
* every program in `src/` is quoted or linked by at least one lesson.

A fence right after `<!-- snapshot: steps/NN/path -->` quotes a project snapshot (section 14) instead
of `src/`: it is checked against `<module>/steps/NN/path` alone, a python fence line by line in order
as above, any other fence as contiguous lines of the file. A fence right after `<!-- unverified -->`
is skipped; keep that marker for output no program of the module prints.

It prints one line per problem and exits 1 if there are any. Outputs are written to
`.scratch/outputs/<module>/<program>.txt` for the next writer to read.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(r"^```(\w+)[^\n]*\n(.*?)^```\s*$", re.S | re.M)
SKIP_FENCE = "<!-- unverified -->"
SNAPSHOT = re.compile(r"<!-- snapshot: (steps/\d\d/[\w./-]+) -->")


def run_programs(module: Path) -> dict[str, str]:
    outputs = {}
    out_dir = ROOT / ".scratch" / "outputs" / module.name
    out_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(ROOT / "00-base"), str(module / "src")]),
           "PYTHONHASHSEED": "0", "MPLBACKEND": "Agg"}
    for program in sorted((module / "src").glob("*.py")):
        done = subprocess.run([sys.executable, str(program)], cwd=ROOT, env=env, capture_output=True,
                              text=True, timeout=600)
        text = done.stdout + (f"\n[exit {done.returncode}]\n{done.stderr}" if done.returncode else "")
        (out_dir / f"{program.stem}.txt").write_text(text, encoding="utf-8")
        outputs[program.name] = text
    return outputs


def lines(text: str) -> list[str]:
    return [line.rstrip() for line in textwrap.dedent(text).splitlines() if line.strip()]


def contiguous(needle: list[str], hay: list[str]) -> bool:
    n = len(needle)
    return any(hay[i:i + n] == needle for i in range(len(hay) - n + 1))


def in_order(needle: list[str], hay: list[str]) -> bool:
    it = iter(hay)
    return all(any(line == h for h in it) for line in needle)


def snapshot_problems(module: Path, path: str, lang: str, want: list[str], where: str) -> list[str]:
    """A fence that quotes a project snapshot file, checked against that file alone."""
    source = module / path
    if not source.is_file():
        return [f"{where}: {lang} block names {path}, which {module.name} does not have"]
    have = lines(source.read_text(encoding="utf-8"))
    if lang == "python":
        ok = in_order([line.strip() for line in want], [line.strip() for line in have])
    else:
        ok = contiguous(want, have)
    return [] if ok else [f"{where}: {lang} block is not lifted from {path}"]


def check(module: Path) -> list[str]:
    problems = []
    outputs = run_programs(module)
    for name, text in outputs.items():
        if "[exit " in text:
            problems.append(f"{module.name}/src/{name}: exited non-zero")
    sources = {p.name: lines(p.read_text(encoding="utf-8")) for p in (module / "src").glob("*.py")}
    output_lines = {name: lines(text) for name, text in outputs.items()}
    mentioned = set()
    for lesson in sorted(module.glob("README_*.md")):
        text = lesson.read_text(encoding="utf-8")
        mentioned |= {name for name in sources if name in text}
        for match in FENCE.finditer(text):
            lang, body = match.group(1), match.group(2)
            start = text[:match.start()].count("\n") + 1
            preceding = text[:match.start()].rstrip().splitlines()[-1:] or [""]
            if preceding[0].strip() == SKIP_FENCE:
                continue
            want = lines(body)
            quoted = SNAPSHOT.fullmatch(preceding[0].strip())
            if quoted:
                problems += snapshot_problems(module, quoted.group(1), lang, want, f"{lesson.relative_to(ROOT)}:{start}")
                continue
            if lang == "python":
                stripped = [line.strip() for line in want]
                if not any(in_order(stripped, [l.strip() for l in src]) for src in sources.values()):
                    problems.append(f"{lesson.relative_to(ROOT)}:{start}: python block is in no program of src/")
            elif lang == "text":
                if not any(contiguous(want, out) for out in output_lines.values()):
                    problems.append(f"{lesson.relative_to(ROOT)}:{start}: text block was printed by no program")
    for name in sources:
        if name not in mentioned:
            problems.append(f"{module.name}/src/{name}: no lesson quotes or links it")
    return problems


def main(argv: list[str]) -> int:
    if argv == ["--all"]:
        modules = sorted(p for p in ROOT.glob("[0-9][0-9]-*") if (p / "src").is_dir() and p.name != "00-base")
    else:
        modules = [ROOT / a.rstrip("/") for a in argv]
    problems = [p for m in modules for p in check(m)]
    for p in problems:
        print(p)
    print(f"{len(modules)} module(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
