"""Check an openspec/ folder the way `openspec validate --strict` does, and archive a change.

This is not the OpenSpec CLI, a Node.js program that the course's runner image now carries. It mirrors
the format rules of OpenSpec 2.0.0 (tag v2.0.0 of github.com/Fission-AI/OpenSpec: the validator in
src/core/validation/validator.ts, the readers in src/core/parsers/ and the merge in
src/core/specs-apply.ts) that this project's specs need:

    python3 specs_check.py list                        # active changes and living specs
    python3 specs_check.py validate --strict           # every living spec and active change
    python3 specs_check.py archive <change> --date 2026-11-03
    python3 specs_check.py trace                       # every scenario to a test, every test to a scenario

What it leaves out: proposal.md, design.md and .openspec.yaml (the settings file, schema and date,
that `openspec new change` writes into each change folder) are not read; capability folders are
flat (specs/<capability>/spec.md); there are no stores, schemas or JSON output.
"""

from __future__ import annotations

import ast
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

DELTAS = ("ADDED", "MODIFIED", "REMOVED", "RENAMED")
KEYWORD = re.compile(r"\b(SHALL|MUST)\b")
BOLD_TRIGGER, BARE_TRIGGER = re.compile(r"(?i:(\*\*|__)(WHEN|GIVEN):?(\*\*|__))"), re.compile(r"\b(WHEN|GIVEN)\b")
BOLD_OUTCOME, BARE_OUTCOME = re.compile(r"(?i:(\*\*|__)THEN:?(\*\*|__))"), re.compile(r"\bTHEN\b")
REQUIREMENT = re.compile(r"^###\s*Requirement:\s*(.+?)\s*$")
SCENARIO = re.compile(r"^####\s+(?:Scenario:\s*)?(.+?)\s*$")
PLACEHOLDER = "TBD - created by archiving change {}. Update Purpose after archive."


@dataclass(frozen=True)
class Issue:
    level: str          # "ERROR" or "WARNING"; strict mode fails on either
    where: str          # the file it was found in
    message: str

    def __str__(self) -> str:
        return f"{self.level:7} {self.where}: {self.message}"


@dataclass
class Requirement:
    name: str
    text: str                                           # the body above the first scenario
    scenarios: dict[str, str] = field(default_factory=dict)   # scenario name -> its steps
    raw: str = ""                                       # the block as archive copies it


@dataclass
class Delta:
    sections: list[str] = field(default_factory=list)   # the delta headers present
    added: list[Requirement] = field(default_factory=list)
    modified: list[Requirement] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    renamed: list[tuple[str, str]] = field(default_factory=list)
    unpaired: list[str] = field(default_factory=list)   # FROM: or TO: lines with no partner
    purpose: str = ""

    def count(self) -> int:
        return len(self.added) + len(self.modified) + len(self.removed) + len(self.renamed)


# ---------------------------------------------------------------------------------------------
# Reading


def sections(text: str) -> list[tuple[str, list[str]]]:
    """The text cut at each level-2 header: (title, lines under it); the lines above the first get ''."""
    found: list[tuple[str, list[str]]] = [("", [])]
    for line in text.splitlines():
        header = re.match(r"^##(?!#)\s+(.+?)\s*$", line)
        if header:
            found.append((header.group(1), []))
        else:
            found[-1][1].append(line)
    return found


def requirement(name: str, block: list[str]) -> Requirement:
    """One requirement from its header line and the lines under it."""
    body = block[1:]
    text = []
    for line in body:
        if line.startswith("#"):
            break
        if line.strip():
            text.append(line.strip())
    steps: dict[str, list[str]] = {}
    current = None
    for line in body:
        scenario = SCENARIO.match(line)
        if scenario:
            current = scenario.group(1)
            steps[current] = []
        elif re.match(r"^#{1,3}\s", line):
            current = None
        elif current is not None:
            steps[current].append(line)
    return Requirement(name, "\n".join(text), {k: "\n".join(v).strip() for k, v in steps.items()},
                       "\n".join(block).strip())


def requirements(lines: list[str]) -> list[Requirement]:
    """Every `### Requirement:` block in the lines, in order."""
    blocks: list[tuple[str, list[str]]] = []
    for line in lines:
        header = REQUIREMENT.match(line)
        if header:
            blocks.append((header.group(1), [line]))
        elif blocks:
            blocks[-1][1].append(line)
    return [requirement(name, block) for name, block in blocks]


def delta_operation(title: str) -> str | None:
    found = re.fullmatch(r"(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements", title, re.I)
    return found.group(1).upper() if found else None


def read_delta(text: str) -> Delta:
    delta = Delta()
    for title, lines in sections(text):
        operation = delta_operation(title)
        if title == "Purpose":
            delta.purpose = "\n".join(lines).strip()
        if operation is None:
            continue
        delta.sections.append(f"## {title}")
        if operation == "ADDED":
            delta.added += requirements(lines)
        elif operation == "MODIFIED":
            delta.modified += requirements(lines)
        elif operation == "REMOVED":
            for line in lines:
                named = REQUIREMENT.match(line) or re.match(r"^\s*[-*+]\s*`?###\s*Requirement:\s*(.+?)`?\s*$", line)
                if named:
                    delta.removed.append(named.group(1))
        else:
            pending = None
            for line in lines:
                side = re.match(r"^\s*[-*+]?\s*(FROM|TO):\s*`?###\s*Requirement:\s*(.+?)`?\s*$", line)
                if not side:
                    continue
                if side.group(1) == "FROM":
                    if pending:
                        delta.unpaired.append(f"FROM: {pending}")
                    pending = side.group(2)
                elif pending is None:
                    delta.unpaired.append(f"TO: {side.group(2)}")
                else:
                    delta.renamed.append((pending, side.group(2)))
                    pending = None
            if pending:
                delta.unpaired.append(f"FROM: {pending}")
    return delta


def has_steps(body: str) -> tuple[bool, bool]:
    """Does a scenario have a trigger (WHEN or GIVEN) and an outcome (THEN)?"""
    trigger = any(BOLD_TRIGGER.search(line) or BARE_TRIGGER.search(line) for line in body.splitlines())
    outcome = any(BOLD_OUTCOME.search(line) or BARE_OUTCOME.search(line) for line in body.splitlines())
    return trigger, outcome


# ---------------------------------------------------------------------------------------------
# Checking


def check_requirement(req: Requirement, where: str) -> list[Issue]:
    """The rules every requirement keeps, in a living spec and in an ADDED or MODIFIED delta."""
    issues = []
    if not req.text:
        issues.append(Issue("ERROR", where, f'requirement "{req.name}" has no text under its header'))
    elif not KEYWORD.search(req.text):
        issues.append(Issue("WARNING", where, f'requirement "{req.name}" should contain SHALL or MUST in its text'))
    scenarios = {name: body for name, body in req.scenarios.items() if body}
    if not scenarios:
        issues.append(Issue("ERROR", where, f'requirement "{req.name}" must include at least one scenario'))
    for name, body in scenarios.items():
        trigger, outcome = has_steps(body)
        missing = [step for step, ok in (("a WHEN or GIVEN step", trigger), ("a THEN step", outcome)) if not ok]
        if missing:
            issues.append(Issue("WARNING", where, f'scenario "{name}" is missing {" and ".join(missing)}'))
    return issues


def check_spec(text: str, where: str) -> list[Issue]:
    """A living spec: a Purpose, a Requirements section, and requirements that keep their rules."""
    found = sections(text)
    titles = [title for title, _ in found]
    issues = [Issue("ERROR", where, f'a living spec contains the delta header "## {title}"')
              for title in titles if delta_operation(title)]
    if "Purpose" not in titles or "Requirements" not in titles:
        return issues + [Issue("ERROR", where, 'missing "## Purpose" or "## Requirements"')]
    purpose = "\n".join(dict(found)["Purpose"]).strip()
    if len(purpose) < 50:
        issues.append(Issue("WARNING", where, "the Purpose is too brief (under 50 characters)"))
    reqs = requirements(dict(found)["Requirements"])
    if not reqs:
        issues.append(Issue("ERROR", where, "a spec must have at least one requirement"))
    names = [r.name for r in reqs]
    issues += [Issue("ERROR", where, f'requirement "{n}" appears twice') for n in sorted(set(names)) if names.count(n) > 1]
    for req in reqs:
        issues += check_requirement(req, where)
    return issues


def check_delta(text: str, living: str | None, where: str) -> tuple[list[Issue], int]:
    """A delta spec of a change, against the living spec it would change (None: there is none yet)."""
    delta = read_delta(text)
    issues = [Issue("ERROR", where, f"RENAMED {line} has no partner line") for line in delta.unpaired]
    if not delta.sections:
        issues.append(Issue("ERROR", where, 'no delta sections found; add "## ADDED Requirements" or another'))
    elif delta.count() == 0:
        issues.append(Issue("ERROR", where, "delta sections were found, but no requirement entries"))
    added, modified = [r.name for r in delta.added], [r.name for r in delta.modified]
    renamed_from, renamed_to = [a for a, _ in delta.renamed], [b for _, b in delta.renamed]
    for label, names in (("ADDED", added), ("MODIFIED", modified), ("REMOVED", delta.removed),
                         ("RENAMED FROM", renamed_from), ("RENAMED TO", renamed_to)):
        issues += [Issue("ERROR", where, f'duplicate requirement in {label}: "{n}"')
                   for n in sorted(set(names)) if names.count(n) > 1]
    for a, b, both in (("MODIFIED", "REMOVED", set(modified) & set(delta.removed)),
                       ("MODIFIED", "ADDED", set(modified) & set(added)),
                       ("ADDED", "REMOVED", set(added) & set(delta.removed)),
                       ("RENAMED", "REMOVED", set(renamed_from) & set(delta.removed))):
        issues += [Issue("ERROR", where, f'requirement in both {a} and {b}: "{n}"') for n in sorted(both)]
    issues += [Issue("ERROR", where, f'MODIFIED uses the old name of a RENAMED requirement: "{n}"')
               for n in sorted(set(modified) & set(renamed_from))]
    for req in delta.added + delta.modified:
        issues += check_requirement(req, where)
    if living is not None:
        current = {r.name: r for r in requirements(dict(sections(living)).get("Requirements", []))}
        old_name = {to: frm for frm, to in delta.renamed}
        for req in delta.modified:
            before = current.get(req.name) or current.get(old_name.get(req.name, ""))
            lost = [s for s in before.scenarios if s not in req.scenarios] if before else []
            if lost:
                issues.append(Issue("ERROR", where, f'MODIFIED "{req.name}" drops scenario(s) the living spec has: '
                                    + ", ".join(f'"{s}"' for s in lost)))
    return issues, delta.count()


def check_change(change: Path, specs: Path) -> list[Issue]:
    """Every delta spec of a change, and at least one delta across them."""
    issues, total = [], 0
    for delta in sorted((change / "specs").glob("*/spec.md")):
        living = specs / delta.parent.name / "spec.md"
        found, count = check_delta(delta.read_text(encoding="utf-8"),
                                   living.read_text(encoding="utf-8") if living.exists() else None,
                                   f"{change.name}/specs/{delta.parent.name}/spec.md")
        issues += found
        total += count
    if total == 0:
        issues.append(Issue("ERROR", change.name, "a change must have at least one delta"))
    return issues


def active_changes(root: Path) -> list[Path]:
    changes = root / "openspec" / "changes"
    return sorted(p for p in changes.glob("*") if p.is_dir() and p.name != "archive") if changes.exists() else []


def validate(root: Path) -> dict[str, list[Issue]]:
    """The issues of every living spec and every active change under root/openspec."""
    specs = root / "openspec" / "specs"
    found = {f"spec {p.parent.name}": check_spec(p.read_text(encoding="utf-8"), f"specs/{p.parent.name}/spec.md")
             for p in sorted(specs.glob("*/spec.md"))}
    for change in active_changes(root):
        found[f"change {change.name}"] = check_change(change, specs)
    return found


def passes(issues: list[Issue], strict: bool = True) -> bool:
    """Valid: no error, and in strict mode no warning either, as `openspec validate --strict` decides."""
    return not any(i.level == "ERROR" or (strict and i.level == "WARNING") for i in issues)


# ---------------------------------------------------------------------------------------------
# Archiving


def apply_delta(living: str | None, text: str, capability: str, change: str) -> str:
    """The living spec after the delta: RENAMED, then REMOVED, then MODIFIED, then ADDED."""
    delta = read_delta(text)
    if living is None:
        if delta.modified or delta.renamed:
            raise ValueError(f"{capability}: no living spec yet, so only ADDED requirements may apply")
        head = (f"# {capability} Specification\n\n## Purpose\n{delta.purpose or PLACEHOLDER.format(change)}"
                "\n\n## Requirements")
        order, blocks, tail = [], {}, ""
    else:
        lines = living.splitlines()
        start = next(i for i, line in enumerate(lines) if re.match(r"^##\s+Requirements\s*$", line))
        end = next((i for i in range(start + 1, len(lines)) if re.match(r"^##(?!#)\s", lines[i])), len(lines))
        reqs = requirements(lines[start + 1:end])
        head = "\n".join(lines[:start + 1]).rstrip()
        order, blocks = [r.name for r in reqs], {r.name: r.raw for r in reqs}
        tail = "\n".join(lines[end:]).strip()
    for old, new in delta.renamed:
        if old not in blocks or new in blocks:
            raise ValueError(f'{capability}: cannot rename "{old}" to "{new}"')
        blocks[new] = re.sub(r"^###\s*Requirement:.*$", f"### Requirement: {new}", blocks.pop(old), count=1, flags=re.M)
        order[order.index(old)] = new
    for name in delta.removed:
        if name in blocks:
            del blocks[name]
            order.remove(name)
    for req in delta.modified:
        if req.name not in blocks:
            raise ValueError(f'{capability}: MODIFIED "{req.name}" is not in the living spec')
        blocks[req.name] = req.raw
    for req in delta.added:
        if req.name in blocks:
            raise ValueError(f'{capability}: ADDED "{req.name}" is already in the living spec')
        order.append(req.name)
        blocks[req.name] = req.raw
    body = "\n\n".join(blocks[name] for name in order)
    return f"{head}\n\n{body}" + (f"\n\n{tail}" if tail else "") + "\n"


def unchecked_tasks(change: Path) -> int:
    tasks = change / "tasks.md"
    return len(re.findall(r"^\s*- \[ \]", tasks.read_text(encoding="utf-8"), re.M)) if tasks.exists() else 0


def archive(root: Path, name: str, date: str) -> list[str]:
    """Merge a change's deltas into the living specs and move it to changes/archive/<date>-<name>."""
    change, specs = root / "openspec" / "changes" / name, root / "openspec" / "specs"
    issues = check_change(change, specs)
    if not passes(issues, strict=False):
        raise ValueError(f"{name} does not validate:\n" + "\n".join(map(str, issues)))
    notes = []
    if unchecked_tasks(change):
        notes.append(f"{name}: {unchecked_tasks(change)} task(s) not checked off in tasks.md (a warning, not a block)")
    rebuilt = {}
    for delta in sorted((change / "specs").glob("*/spec.md")):
        capability = delta.parent.name
        living = specs / capability / "spec.md"
        text = apply_delta(living.read_text(encoding="utf-8") if living.exists() else None,
                           delta.read_text(encoding="utf-8"), capability, name)
        errors = [i for i in check_spec(text, f"specs/{capability}/spec.md") if i.level == "ERROR"]
        if errors:
            raise ValueError(f"{name}: the rebuilt spec would not validate:\n" + "\n".join(map(str, errors)))
        rebuilt[living] = text
        notes.append(f"specs/{capability}/spec.md: " + ("updated" if living.exists() else "created"))
    for living, text in rebuilt.items():
        living.parent.mkdir(parents=True, exist_ok=True)
        living.write_text(text, encoding="utf-8")
    target = root / "openspec" / "changes" / "archive" / f"{date}-{name}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(change), str(target))
    notes.append(f"moved to changes/archive/{target.name}")
    return notes


# ---------------------------------------------------------------------------------------------
# Tracing scenarios to tests


@dataclass
class Trace:
    pairs: int = 0                                         # scenarios with their test
    untested: list[str] = field(default_factory=list)      # "capability: scenario" with no test
    untraced: list[str] = field(default_factory=list)      # "tests/file.py::test" with no scenario


def test_name(scenario: str) -> str:
    """The test a scenario is traced to: its name in lower case, each run of other characters one '_'."""
    return "test_" + re.sub(r"[^a-z0-9]+", "_", scenario.lower()).strip("_")


def trace(root: Path) -> Trace:
    """Match every scenario of the living specs to its test, and every test of a capability's file to its scenario.

    A capability's tests live in tests/test_<capability, with '-' as '_'>.py. Test files named after no
    capability (helpers, the course's expected-output check) are outside the trace.
    """
    wanted: dict[tuple[str, str], str] = {}          # (test file, test name) -> "capability: scenario"
    files = set()
    for spec in sorted((root / "openspec" / "specs").glob("*/spec.md")):
        capability = spec.parent.name
        files.add(f"test_{capability.replace('-', '_')}.py")
        for req in requirements(dict(sections(spec.read_text(encoding="utf-8"))).get("Requirements", [])):
            for scenario in req.scenarios:
                wanted[f"test_{capability.replace('-', '_')}.py", test_name(scenario)] = f"{capability}: {scenario}"
    found = set()
    for name in sorted(files):
        path = root / "tests" / name
        if path.exists():
            found |= {(name, node.name) for node in ast.parse(path.read_text(encoding="utf-8")).body
                      if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}
    keys = set(found)
    return Trace(pairs=sum(1 for key in wanted if key in keys),
                 untested=sorted(label for key, label in wanted.items() if key not in keys),
                 untraced=sorted(f"tests/{f}::{t}" for f, t in found if (f, t) not in wanted))


# ---------------------------------------------------------------------------------------------
# The command line


def listing(root: Path) -> list[str]:
    out = ["Changes:"]
    for change in active_changes(root):
        tasks = change / "tasks.md"
        total = len(re.findall(r"^\s*- \[[ x]\]", tasks.read_text(encoding="utf-8"), re.M)) if tasks.exists() else 0
        out.append(f"  {change.name:28} {total - unchecked_tasks(change)}/{total} tasks")
    out.append("Specs:")
    for spec in sorted((root / "openspec" / "specs").glob("*/spec.md")):
        reqs = requirements(dict(sections(spec.read_text(encoding="utf-8"))).get("Requirements", []))
        out.append(f"  {spec.parent.name:28} requirements {len(reqs)}")
    return out


def main(argv: list[str], root: Path = Path(__file__).resolve().parent) -> int:
    print("(specs_check.py mirrors OpenSpec 2.0.0's format rules; it is not the openspec CLI)")
    if argv[:1] == ["list"]:
        print("\n".join(listing(root)))
        return 0
    if argv[:1] == ["validate"]:
        strict = "--strict" in argv
        failed = 0
        for item, issues in validate(root).items():
            ok = passes(issues, strict)
            failed += not ok
            print(f"{'valid  ' if ok else 'INVALID'} {item}")
            for issue in issues:
                print(f"  {issue}")
        print(f"{'strict' if strict else 'plain'}: {failed} item(s) failed")
        return 1 if failed else 0
    if argv[:1] == ["trace"]:
        found = trace(root)
        print(f"{found.pairs} scenarios with their tests")
        for label in found.untested:
            print(f"  no test: {label}")
        for test in found.untraced:
            print(f"  no scenario: {test}")
        return 1 if found.untested or found.untraced else 0
    if argv[:1] == ["archive"] and len(argv) == 4 and argv[2] == "--date":
        for note in archive(root, argv[1], argv[3]):
            print(note)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
