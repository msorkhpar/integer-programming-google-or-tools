"""The course's curriculum, read from the blueprint, and the files written from it.

    python3 scripts/curriculum.py json        # docs/plan/curriculum.json (the blueprint as data)
    python3 scripts/curriculum.py progress    # PROGRESS.md, keeping each module's recorded status
    python3 scripts/curriculum.py record      # the README's curriculum list, for authored modules only
    python3 scripts/curriculum.py map         # docs/COURSE_MAP.md, the whole table of contents, written or not
    python3 scripts/curriculum.py check       # exit 1 if any written file is out of date

The blueprint (`docs/plan/blueprint.md`) is the source of truth for numbering, titles and scope.
Module titles are not in the blueprint (it gives slugs), so they are set once here, in `TITLES`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / "docs" / "plan" / "blueprint.md"
CURRICULUM = ROOT / "docs" / "plan" / "curriculum.json"
PROGRESS = ROOT / "PROGRESS.md"
README = ROOT / "README.md"
MAP = ROOT / "docs" / "COURSE_MAP.md"
RECORD_START, RECORD_END = "<!-- curriculum:start -->", "<!-- curriculum:end -->"

TITLES = {
    "01": "The optimization mindset", "02": "The math toolkit", "03": "Python for optimization",
    "04": "Modeling linear programs", "05": "LP geometry and the simplex method", "06": "Duality and sensitivity",
    "07": "LP solvers in practice", "08": "Why integers", "09": "Branch and bound",
    "10": "Cuts, presolve and heuristics", "11": "MIP gap and termination", "12": "The OR-Tools landscape",
    "13": "MathOpt core", "14": "MathOpt advanced", "15": "CP-SAT core", "16": "CP-SAT scheduling",
    "17": "CP-SAT tuning and diagnostics", "18": "The linear solver wrapper and special-purpose solvers", "19": "Pyomo", "20": "PuLP",
    "21": "gurobipy", "22": "Choosing a solver", "23": "Binary logic", "24": "Big-M and indicators",
    "25": "Knapsack and assignment", "26": "Multi-period timing", "27": "Dependencies and groups",
    "28": "Piecewise-linear functions", "29": "Strong formulations", "30": "Utility capital planning",
    "31": "Financial evaluation", "32": "Asset risk", "33": "Value functions", "34": "Weighted sums",
    "35": "Lexicographic objectives", "36": "The epsilon-constraint method", "37": "Infeasibility",
    "38": "Sensitivity for MIP", "39": "Explaining decisions", "40": "Numerics",
    "41": "Determinism and reproducibility", "42": "Model building at scale", "43": "Warm starts and tuning",
    "44": "Decomposition and heuristics", "45": "The scenario workflow", "46": "Input data quality",
    "47": "Testing optimization code", "48": "The optimization API", "49": "Cloud deployment",
    "51": "Capstone: CIPT Lite", "52": "OR-Tools routing",
    "53": "Mock interviews",
    "54": "Project: vegetation crew planner", "55": "Project: CIPT planner",
    "56": "Project: transformer fleet renewal",
    "57": "GPU acceleration",
    "58": "Project: spec-driven development with OpenSpec",
}


def parse() -> dict:
    text = BLUEPRINT.read_text(encoding="utf-8")
    sections = {int(n): name for n, name in re.findall(r"^### Section (\d+)\. (.+)$", text, re.M)}
    sections[13] = "Capstone"
    modules = []
    section = 0
    for line in text.splitlines():
        heading = re.match(r"^### Section (\d+)\.", line)
        if heading:
            section = int(heading[1])
        row = re.match(r"^\| (\d\d-[a-z0-9-]+) \| (.+?) \| (.+?) \| (\w+) · (\d+) min \|$", line)
        if not row:
            continue
        slug, lessons, examples, depth, minutes = row.groups()
        found = re.findall(r"(\d+\.\d+\.\d+) (.+?)(?= · \d+\.\d+\.\d+ |$)", lessons)
        modules.append({
            "number": slug[:2], "slug": slug, "section": section, "title": TITLES[slug[:2]],
            "depth": depth, "minutes": int(minutes), "examples_and_practices": examples,
            "lessons": [{"number": n, "title": title.replace("\\[", "[").replace("\\]", "]")} for n, title in found],
        })
    capstone = re.findall(r"^\| (13\.1\.\d) \| (.+?) \| (.+?) \|$", text, re.M)
    modules.append({
        "number": "51", "slug": "51-capstone-cipt-lite", "section": 13, "title": TITLES["51"], "depth": "Core",
        "minutes": 300, "examples_and_practices": "six milestones, each a graded practice",
        "lessons": [{"number": n, "title": title, "graded_by": graded} for n, title, graded in capstone],
    })
    lesson_count = sum(len(m["lessons"]) for m in modules)
    if len(modules) != 57 or lesson_count != 237:
        raise SystemExit(f"blueprint parse gave {len(modules)} modules and {lesson_count} lessons, not 57 and 237")
    return {"sections": {str(k): v for k, v in sorted(sections.items())}, "modules": modules}


def statuses() -> dict[str, str]:
    if not PROGRESS.exists():
        return {}
    return dict(re.findall(r"^\| (\d\d) \| `[^`]+` \|[^|]+\|[^|]+\|[^|]+\| (pending|in-progress|done) \|$",
                           PROGRESS.read_text(encoding="utf-8"), re.M))


def progress_text(data: dict) -> str:
    status = statuses()
    rows = {m["number"]: status.get(m["number"], "pending") for m in data["modules"]}
    counts = {s: sum(1 for v in rows.values() if v == s) for s in ("done", "in-progress", "pending")}
    out = ["# Progress", "", "One row per module: `pending`, `in-progress` or `done`. A module is done when it meets the",
           "blueprint's definition of done. Regenerate the table with `python3 scripts/curriculum.py progress`;",
           "change a status by editing its row.", "",
           f"**Done:** {counts['done']} / {len(rows)} · **In progress:** {counts['in-progress']} · **Pending:** {counts['pending']}", ""]
    for number, name in data["sections"].items():
        out += [f"## {number}. {name}", "", "| Module | Directory | Title | Lessons | Depth · time | Status |",
                "| --- | --- | --- | --- | --- | --- |"]
        for m in (m for m in data["modules"] if m["section"] == int(number)):
            out.append(f"| {m['number']} | `{m['slug']}` | {m['title']} | {len(m['lessons'])} | "
                       f"{m['depth']} · {m['minutes']} min | {rows[m['number']]} |")
        out.append("")
    return "\n".join(out)


def authored(module: dict) -> bool:
    return all((ROOT / module["slug"] / f"README_{l['number']}.md").exists() for l in module["lessons"]) and \
        (ROOT / module["slug"] / "README.md").exists()


def record_text(data: dict) -> str:
    out = [RECORD_START, ""]
    for number, name in data["sections"].items():
        modules = [m for m in data["modules"] if m["section"] == int(number) and authored(m)]
        if not modules:
            continue
        out += [f"{number}. {name}", ""]
        for m in modules:
            section_module = m["lessons"][0]["number"].rsplit(".", 1)[0]
            out.append(f"- [{section_module}. {m['title']}]({m['slug']}/README.md)")
            for lesson in m["lessons"]:
                # The record's link pattern allows no "]" in a title, escaped or not (finding F10).
                title = lesson["title"].replace("[", "(").replace("]", ")")
                out.append(f"    - [{lesson['number']}. {title}]({m['slug']}/README_{lesson['number']}.md)")
        out.append("")
    out.append(RECORD_END)
    return "\n".join(out)


def map_text(data: dict) -> str:
    """Every section, module and lesson, with each module's status, so the whole course reads at once."""
    status = statuses()
    out = ["# Course Map", "",
           "The whole table of contents, generated from `docs/plan/blueprint.md` by",
           "`python3 scripts/curriculum.py map`. A module links to its page once it is written; the README's",
           "curriculum lists only written modules, because StudyForge reads that list.", ""]
    total = sum(len(m["lessons"]) for m in data["modules"])
    out += [f"{len(data['sections'])} sections, {len(data['modules'])} modules, {total} lessons.", ""]
    for number, name in data["sections"].items():
        out += [f"## {number}. {name}", ""]
        for m in (m for m in data["modules"] if m["section"] == int(number)):
            head = m["lessons"][0]["number"].rsplit(".", 1)[0]
            title = f"[{m['title']}]({'../' + m['slug']}/README.md)" if authored(m) else m["title"]
            out.append(f"- **{head}. {title}** ({m['depth']}, module {m['number']}, "
                       f"{status.get(m['number'], 'pending')})")
            out += [f"    - {lesson['number']} {lesson['title']}" for lesson in m["lessons"]]
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def readme_with_record(data: dict) -> str:
    text = README.read_text(encoding="utf-8")
    start, end = text.index(RECORD_START), text.index(RECORD_END) + len(RECORD_END)
    return text[:start] + record_text(data) + text[end:]


def main(argv: list[str]) -> int:
    verb = argv[1] if len(argv) > 1 else "check"
    data = parse()
    wanted = {CURRICULUM: json.dumps(data, indent=2, ensure_ascii=False) + "\n",
              PROGRESS: progress_text(data) + "\n", README: readme_with_record(data), MAP: map_text(data)}
    if verb == "check":
        stale = [p.name for p, text in wanted.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        print("up to date" if not stale else "out of date: " + ", ".join(stale))
        return 1 if stale else 0
    target = {"json": CURRICULUM, "progress": PROGRESS, "record": README, "map": MAP}[verb]
    target.write_text(wanted[target], encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
