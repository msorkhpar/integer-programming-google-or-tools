"""Catch the authoring mistakes the pilot's learner run found, before a module ships.

    python3 scripts/check_exercises.py 01-optimization-mindset 26-multi-period-timing

Seven checks, one per mistake (docs/AUTHORING.md, "What the learner run taught us"):

1. **Key position.** A quiz whose keys sit in one position is answered by position. Refused: every
   key of a quiz in one position, or one position holding more than 40% of a module's keys.
2. **Aspects that answer.** A quiz card shows its aspects' sentences to the reader before the
   quiz. Refused: a quiz aspect sharing a run of five or more words with any option or sentence of
   that quiz.
3. **Practice before its lesson.** Refused: a code practice placed above a section its aspects
   name as their basis, so the reader meets the practice before the page teaches it; and a
   practice whose `heading` is not the section its marker sits in.
4. **Copy of the lesson.** From section 6 on, a practice transfers an idea rather than retyping a
   snippet. Refused there: a practice where more than half of the lines the learner writes (the
   reference less the starter) have the shape of a line in the lesson's own code blocks, names
   collapsed so a renamed copy is still a copy. A bare `for ...:` or `if ...:` line is structure,
   not content, and is not counted.
5. **Too few practices.** Refused: a Core or Deep lesson with fewer than two code practices. A
   project practice (a folder with `project.json`, built from a before/after pair of snapshots)
   counts as a code practice. In section 14 (Growing real projects) each lesson is one step of a
   grown project, and its practice is that step's project practice (docs/plan/blueprint.md), so the
   two-or-three rule does not apply there: a section-14 lesson needs exactly its one project
   practice, beside its quiz.
6. **A sentence cut into a list.** Markdown reads a line that starts with a number and a period as
   a numbered list. Refused, in a lesson page or a practice statement: a wrapped paragraph line
   that starts that way ("... becomes\n0. Adding ..."), and a list that starts at a number other
   than 1 (a list broken by an unindented code or math fence restarts there).
7. **No sources.** A lesson cites what it was written from. Refused: a lesson page with no
   `**Further reading:**` (or `.`) paragraph linking at least one outside source (an `http` link).

Prints one line per finding and exits 1 if there is any.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("CHECK_ROOT") or Path(__file__).resolve().parents[1])
SRC = ROOT / "exercise-src"
CURRICULUM = json.loads((ROOT / "docs/plan/curriculum.json").read_text(encoding="utf-8"))
RUN = 5
MAX_SHARE = 0.40
COPY_SHARE = 0.5
MODELING_FROM_SECTION = 6
#: By the module's depth in the blueprint; StudyForge's plan tiers (introductory, core, advanced)
#: do not name it.
MIN_CODE = {"core": 2, "deep": 2, "survey": 0}
#: Growing real projects: one project practice per step, whatever the module's depth (check 5).
PROJECT_SECTION = 14
PROJECT = "project.json"


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def runs(text: str, n: int = RUN) -> set[tuple[str, ...]]:
    w = words(text)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def depth_of(slug: str) -> str:
    number = int(slug.split("-", 1)[0])
    for module in CURRICULUM["modules"]:
        if int(module["number"]) == number:
            return str(module.get("depth", "Core")).lower()
    raise SystemExit(f"{slug}: not in docs/plan/curriculum.json")


def section_of(slug: str) -> int:
    number = int(slug.split("-", 1)[0])
    for module in CURRICULUM["modules"]:
        if int(module["number"]) == number or module.get("slug") == slug or module.get("directory") == slug:
            return int(module["section"])
    raise SystemExit(f"{slug}: not in docs/plan/curriculum.json")


def headings_and_markers(page: str) -> list[tuple[str, str]]:
    found = []
    for line in page.splitlines():
        if line.startswith("## "):
            found.append(("heading", line[3:].strip()))
        marker = re.match(r"<!-- practice (\d+) -->", line.strip())
        if marker:
            found.append(("marker", marker.group(1)))
    return found


#: Names a line keeps when it is reduced to its shape: Python's own words and the solver's API.
KEEP = {"for", "in", "if", "else", "not", "and", "or", "sum", "range", "len", "lambda", "is", "None",
        "True", "False", "add_linear_constraint", "add_variable", "add_binary_variable", "maximize",
        "minimize", "lb", "ub", "is_integer", "name"}


def shape(line: str) -> str:
    """A line with every other name collapsed, so renaming `project_id` to `pid` is still a copy."""
    reduced = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", lambda m: m.group(0) if m.group(0) in KEEP else "v", line)
    reduced = reduced.replace("()", "")
    reduced = re.sub(r"\s+", "", reduced)
    before = None
    while before != reduced:
        before = reduced
        reduced = re.sub(r"v\.v|v\(v(?:,v)*\)", "v", reduced)
    return reduced


def code_lines(page: str) -> set[str]:
    blocks = re.findall(r"```python\n(.*?)```", page, re.S)
    return {shape(line) for block in blocks for line in block.splitlines() if substantive(line)}


def substantive(line: str) -> bool:
    s = line.strip()
    return bool(s) and not s.startswith(("#", "import ", "from ", '"""', "return", "def ", "@")) and len(s) > 12


def cut_lists(text: str) -> list[tuple[int, str]]:
    """Lines where Markdown would start a numbered list the author did not mean (check 6)."""
    found, fence, in_list, blank = [], False, False, True
    for number, line in enumerate(text.split("\n"), start=1):
        if line.startswith("```"):
            fence, blank = not fence, False
            continue
        if fence:
            continue
        if not line.strip():
            blank = True
            continue
        item = re.match(r"(\d+)[.)](\s|$)", line)
        if blank:
            in_list = bool(re.match(r"\s{0,3}(\d+[.)]|[-*+])(\s|$)", line)) or line.startswith(("|", "#", ">"))
            if item and item.group(1) != "1":
                found.append((number, "a list starting at " + item.group(1)))
        elif item and not in_list:
            found.append((number, "a wrapped line read as a list item"))
        blank = False
    return found


def check_module(slug: str) -> list[str]:
    findings: list[str] = []
    module_dir = SRC / slug
    positions: Counter[int] = Counter()
    modeling = section_of(slug) >= MODELING_FROM_SECTION
    for lesson_dir in sorted(p for p in module_dir.iterdir() if p.is_dir()):
        lesson = lesson_dir.name
        page_path = ROOT / slug / f"README_{lesson}.md"
        page = page_path.read_text(encoding="utf-8")
        for number, what in cut_lists(page):
            findings.append(f"{slug}/README_{lesson}.md:{number}: {what} (check 6)")
        reading = re.search(r"^\*\*Further reading[.:]?\*\*[.:]?(.*?)(?:\n\s*\n|\Z)", page, re.M | re.S)
        if not reading or "](http" not in reading.group(1):
            findings.append(f"{slug}/README_{lesson}.md: no **Further reading:** line with an outside link (check 7)")
        for statement in sorted(lesson_dir.glob("*/statement.md")):
            for number, what in cut_lists(statement.read_text(encoding="utf-8")):
                findings.append(f"{statement.relative_to(ROOT)}:{number}: {what} (check 6)")
        plan = json.loads((lesson_dir / "plan.json").read_text(encoding="utf-8"))
        quiz_name = plan.get("quiz", "quiz")
        quiz_file = lesson_dir / quiz_name / "quiz.json"
        if quiz_file.exists():
            quiz = json.loads(quiz_file.read_text(encoding="utf-8"))
            here = []
            quiz_runs: set[tuple[str, ...]] = set()
            for question in quiz["questions"]:
                keys = [i for i, o in enumerate(question["options"]) if o["correct"]]
                here += keys
                for option in question["options"]:
                    quiz_runs |= runs(option["text"]) | runs(option.get("says", ""))
            positions.update(here)
            if len(here) > 1 and len(set(here)) == 1:
                findings.append(f"{slug}/{lesson}: every quiz key is option {'abcd'[here[0]]} (check 1)")
            for aspect in plan["aspects"]:
                if aspect.get("exercise") == quiz_name or aspect["id"].startswith("quiz-"):
                    shared = runs(aspect["says"]) & quiz_runs
                    if shared:
                        sample = " ".join(sorted(shared)[0])
                        findings.append(f"{slug}/{lesson}: quiz aspect {aspect['id']!r} repeats the quiz: "
                                        f"'{sample} ...' (check 2)")
        order = [name for name in plan["order"] if name != quiz_name]
        projects = [name for name in order if (lesson_dir / name / PROJECT).exists()]
        depth = depth_of(slug)
        if section_of(slug) == PROJECT_SECTION:
            if len(projects) != 1 or len(order) != 1:
                findings.append(f"{slug}/{lesson}: {len(projects)} project practice(s) and "
                                f"{len(order) - len(projects)} other code practice(s); a section-14 lesson "
                                f"is one project step and needs exactly its one project practice (check 5)")
        else:
            wanted = MIN_CODE.get(depth, 2)
            if len(order) < wanted:
                findings.append(f"{slug}/{lesson}: {len(order)} code practice(s), project practices "
                                f"counted; a {depth} module needs {wanted} (check 5)")
        layout = headings_and_markers(page)
        for number, name in enumerate(order, start=1):
            marks = [i for i, (kind, value) in enumerate(layout) if kind == "marker" and value == str(number)]
            if not marks:
                findings.append(f"{slug}/{lesson}: no <!-- practice {number} --> for {name} (check 3)")
                continue
            below = {value for kind, value in layout[marks[0]:] if kind == "heading"}
            above = [value for kind, value in layout[:marks[0]] if kind == "heading"]
            # A project practice cites its whole lesson, so it declares no heading to compare.
            if above and name not in projects:
                declared = json.loads((lesson_dir / name / "practice.json").read_text(encoding="utf-8")).get("heading")
                if declared != above[-1]:
                    findings.append(f"{slug}/{lesson}: {name} declares heading {declared!r} but its marker sits in "
                                    f"{above[-1]!r} (check 3)")
            for aspect in plan["aspects"]:
                if aspect.get("exercise") != name:
                    continue
                for basis in aspect.get("basis", []):
                    heading = basis.removeprefix("section:")
                    if basis.startswith("section:") and heading in below:
                        findings.append(f"{slug}/{lesson}: {name} sits above '{heading}', which teaches it (check 3)")
            reference = lesson_dir / name / "reference.py"
            if modeling and reference.exists():
                given = Counter(shape(ln) for ln in (lesson_dir / name / "starter.py").read_text(encoding="utf-8")
                                .splitlines() if substantive(ln))
                written = Counter(shape(ln) for ln in reference.read_text(encoding="utf-8").splitlines()
                                  if substantive(ln))
                lines = [ln for ln in (written - given).elements()
                         if not re.fullmatch(r"(for|if|elif|while)[^=]*:|else:", ln)]
                taught = code_lines(page)
                copied = [ln for ln in lines if ln in taught]
                if lines and len(copied) / len(lines) > COPY_SHARE:
                    findings.append(f"{slug}/{lesson}: {name} reference is {len(copied)}/{len(lines)} lines of the "
                                    f"lesson's own code (check 4)")
    total = sum(positions.values())
    if total >= 4:
        position, count = positions.most_common(1)[0]
        if count / total > MAX_SHARE:
            findings.append(f"{slug}: {count} of {total} quiz keys are option {'abcd'[position]} (check 1)")
    return findings


def main(slugs: list[str]) -> int:
    findings = [f for slug in slugs for f in check_module(slug)]
    for finding in findings:
        print(finding)
    print(f"{len(slugs)} module(s), {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
