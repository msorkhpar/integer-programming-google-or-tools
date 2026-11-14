"""Author, prove and ship the course's practices and quizzes with StudyForge's exercises skill.

    python3 scripts/exercises.py prove 01-optimization-mindset            # gate every draft, write nothing
    python3 scripts/exercises.py prove 01-optimization-mindset 1.1.1
    python3 scripts/exercises.py readings 01-optimization-mindset          # what the quiz readers must answer
    python3 scripts/exercises.py record Q2.json,... Q13.json,... '<page-free reader>' '<page reader>'
    python3 scripts/exercises.py ship 01-optimization-mindset 26-multi-period-timing
    python3 scripts/exercises.py regate 01-optimization-mindset            # re-gate shipped practices in place

Each practice is written once, as files, under `exercise-src/<module>/<lesson>/`:

    plan.json                 tier, order, quiz name, and the page's aspects (each ends in an exercise or a reason)
    <name>/practice.json      title, main_file, test_file, cases [[id, "main"|"edge", sentence]], assertions_only
    <name>/statement.md       the ask: a situation and a goal, never the page's rules restated
    <name>/starter.py         what the reader starts from; every test fails on it, on an assertion
    <name>/reference.py       the worked solution
    <name>/tests.py           the tests (copied to the workspace as `test_file`)
    <name>/plants.json        {case id: [[old, new], ...]}: each edge's wrong solution, as edits of the reference
    <name>/try_it.py          what Run executes beside the reader's file: a call on a fresh example and its prints
    quiz/quiz.json            {"title", "questions": [{id, stem, heading, options: [{id, text, correct, says}]}]}
    quiz/readings.json        the independent readers' answers (Q1 key picked, Q2 page-free pick, Q3 refutations)

A project practice (section 14) is instead a folder with two files, and the snapshots it names
(its Run is the step's own entry point, so that file is its try-it file):

    <name>/project.json       StudyForge's project manifest: the before/after snapshots (steps/NN-1, steps/NN),
                              the entry point and expected report, the blueprint, the step's cases and plants
    <name>/statement.md       the planners' request and what to build

The driver is the only code that turns those files into drafts, and every run it makes is a
`docker run --network none` in the course's pinned runner image, over a copy staged under
`.scratch/stage/` (some Docker engines cannot mount the host's temporary directory).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from dataclasses import replace
from pathlib import Path

from studyforge.address import Address
from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.exercise.gates.quiz import Q1, Q3, WHOLE_QUESTION, Judgement, page_free, question_digest
from studyforge.exercise.quiz import Option, Question
from studyforge.skills.exercises import (
    Aspect, Brief, CodeDraft, EditedFile, Page, PlantSpec, QuizDraft, Ran, Replacement, author_corpus, author_page,
    take,
)
from studyforge.skills.exercises import tryit

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "exercise-src"
STAGE = ROOT / ".scratch" / "stage"
SOURCE = "integer-programming-python-or-tools"
CURRICULUM = json.loads((ROOT / "docs/plan/curriculum.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------
# Pages and their plans


def section_address(module: dict) -> str:
    # A module agent's worktree has no corpus.json (a second one under the served root stops the
    # site from starting), so a missing manifest means "derive the address" too.
    manifest_file = ROOT / "corpus.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}
    name = CURRICULUM["sections"][str(module["section"])]
    for group in manifest.get("curriculum", {}).get("containers", []):
        if group["label"] == name:
            return group["address"]
    # Not onboarded yet (a section enters corpus.json once its modules exist). `prove` writes
    # nothing, so it can gate drafts at the address onboarding will give: number and slugged label.
    return f"{int(module['section']):02d}-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def module_of(slug: str) -> dict:
    for m in CURRICULUM["modules"]:
        if m["slug"] == slug:
            return m
    raise SystemExit(f"no module {slug!r} in the curriculum")


def pages_of(slug: str) -> list[Page]:
    module = module_of(slug)
    address = Address([section_address(module), slug])
    pages = []
    for unit, lesson in enumerate(module["lessons"], start=1):
        plan_file = SRC / slug / lesson["number"] / "plan.json"
        if not plan_file.exists():
            continue
        plan = json.loads(plan_file.read_text(encoding="utf-8"))
        aspects = tuple(Aspect(a["id"], a["says"], tuple(a["basis"]), a.get("exercise"), a.get("reason"))
                        for a in plan["aspects"])
        pages.append(Page(
            path=f"{slug}/README_{lesson['number']}.md", address=address, variant="prose", unit=unit,
            kind=plan.get("kind", "code"), aspects=aspects, tier=plan.get("tier", "core"),
            order=tuple(plan.get("order", ())), quiz=plan.get("quiz"),
            nothing_checkable=plan.get("nothing_checkable")))
    return pages


def lesson_dir(page: Page) -> Path:
    slug = page.path.split("/")[0]
    number = page.path.split("README_")[1][:-3]
    return SRC / slug / number


# ---------------------------------------------------------------------------------------------
# The author: drafts read from files


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def code_draft(brief: Brief) -> CodeDraft:
    folder = lesson_dir(brief.page) / brief.name
    if (folder / "project.json").exists():
        return project_practice(folder / "project.json", brief)
    meta = json.loads(text(folder / "practice.json"))
    ws = brief.places.workspace
    main, test_file = meta["main_file"], meta["test_file"]
    cases = tuple(Case(cid, MAIN if kind == "main" else EDGE, says) for cid, kind, says in meta["cases"])
    plants = {}
    for cid, edits in json.loads(text(folder / "plants.json")).items():
        plants[cid] = PlantSpec(tuple(Replacement(main, old, new) for old, new in edits))
    try_name = tryit.TRYIT_FILE["python"]
    tried = text(folder / try_name)
    return CodeDraft(
        title=meta["title"], lang="python", main_file=main, test_file=test_file,
        run_command=tryit.run_command("python", ws),
        files={try_name: EditedFile(tried, tried)}, try_file=try_name,
        test_command=("python3", "-m", "pytest", "-q", "-p", "no:cacheprovider",
                      f"--junitxml={ws}/target/report.xml", f"{ws}/{test_file}"),
        cases=cases, report="target/report.xml",
        origin=Origin(brief.page.path, meta.get("heading")),
        statement=text(folder / "statement.md"), starter=text(folder / "starter.py"),
        reference=text(folder / "reference.py"), tests=text(folder / "tests.py"), plants=plants,
        assertions_only=meta.get("assertions_only", True),
    )


def project_practice(manifest: Path, brief: Brief) -> CodeDraft:
    """A project practice: StudyForge builds the draft from the manifest and its two snapshots."""
    # Imported here so a StudyForge without project practices still drives every other practice.
    from studyforge.skills.exercises.project import project_draft
    draft = project_draft(manifest, brief.places.workspace, origin=Origin(brief.page.path, None))
    # Run executes the step's entry point, a reader-edited file that prints the planner's report
    # with no tests: that file is the step's try-it file.
    entry = draft.run_command[-1].removeprefix(f"{brief.places.workspace}/")
    if entry not in draft.files:
        raise SystemExit(f"{manifest}: the entry point {entry!r} is not one of the step's files")
    return replace(draft, try_file=entry)


def questions_of(page: Page, name: str) -> tuple[Question, ...]:
    data = json.loads(text(lesson_dir(page) / name / "quiz.json"))
    return tuple(
        Question(id=q["id"], stem=q["stem"], origin=Origin(page.path, q["heading"]),
                 options=tuple(Option(o["id"], o["text"], o["correct"], o["says"]) for o in q["options"]))
        for q in data["questions"])


def quiz_draft(brief: Brief) -> QuizDraft:
    data = json.loads(text(lesson_dir(brief.page) / brief.name / "quiz.json"))
    return QuizDraft(title=data["title"], questions=questions_of(brief.page, brief.name))


class Author:
    def draft(self, brief: Brief):
        return quiz_draft(brief) if brief.page.kind == "quiz" or brief.name == brief.page.quiz else code_draft(brief)

    def excuse(self, entry) -> str:
        return ("a lesson example: its program runs in the module's own tests, and the lesson's practices "
                "check the idea it shows with inputs of their own")


# ---------------------------------------------------------------------------------------------
# The judge: the readers' answers, recorded in readings.json


def judge(brief: Brief, questions) -> tuple[Judgement, ...]:
    readings_file = lesson_dir(brief.page) / brief.name / "readings.json"
    readings = json.loads(text(readings_file)) if readings_file.exists() else {}
    taken = []
    for q in questions:
        over = question_digest(q)
        r = readings.get(q.id)
        if r is None or r.get("over") != over:
            # No reading for this wording: record it as not held, so the gate refuses honestly.
            taken.append(Judgement(Q1, q.id, WHOLE_QUESTION, "page reader", "none", "no reading for this wording",
                                   False, over))
            continue
        free = r["q2"]
        taken.append(page_free(q, free["picked"], free["because"], free["taken_by"]))
        key = next(o.id for o in q.options if o.correct)
        q1 = r["q1"]
        taken.append(Judgement(Q1, q.id, WHOLE_QUESTION, q1["prompt"], q1["taken_by"], q1["outcome"],
                               q1["picked"] == key, over))
        for o in q.options:
            if o.correct:
                continue
            q3 = r["q3"][o.id]
            taken.append(Judgement(Q3, q.id, o.id, q3["prompt"], q3["taken_by"], q3["outcome"], q3["refuted"], over))
    return tuple(taken)


def readings_brief(slug: str) -> dict:
    """Every quiz question of a module, with its digest, for the reader agents."""
    out = {}
    for page in pages_of(slug):
        if not page.quiz:
            continue
        for q in questions_of(page, page.quiz):
            out[f"{page.path}#{q.id}"] = {
                "over": question_digest(q), "heading": q.origin.section, "stem": q.stem,
                "options": [{"id": o.id, "text": o.text} for o in q.options]}
    return out


# ---------------------------------------------------------------------------------------------
# The runner: each command in the pinned runner image, with no network


def runner_image() -> str:
    if os.environ.get("RUNNER_IMAGE"):
        return os.environ["RUNNER_IMAGE"]
    toolchain = Path(os.environ.get("TOOLCHAIN", ROOT.parent / "code-server-toolchain"))
    return subprocess.run(
        [sys.executable, str(toolchain / "docker/profile_packages/package_build.py"), "--root", str(toolchain),
         "--profile", "optimization", "--image", "runner", "--runtimes", "node,python", "--print-tag"],
        check=True, capture_output=True, text=True).stdout.strip()


class InRunner:
    def __init__(self) -> None:
        self.image = runner_image()

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        STAGE.mkdir(parents=True, exist_ok=True)
        work = STAGE / uuid.uuid4().hex
        shutil.copytree(root, work)
        try:
            argv = ["docker", "run", "--rm", "--network", "none", "--user", f"{os.getuid()}:{os.getgid()}",
                    "-e", "HOME=/tmp", "-e", "PYTHONDONTWRITEBYTECODE=1", "-e", "MPLBACKEND=Agg",
                    "-v", f"{work}:/w", "-w", "/w", self.image, *command]
            done = subprocess.run(argv, capture_output=True, text=True, check=False,
                                  stdin=subprocess.DEVNULL, timeout=900)
            for produced in work.rglob("target"):
                shutil.copytree(produced, root / produced.relative_to(work), dirs_exist_ok=True)
            return Ran(done.returncode, done.stdout + done.stderr)
        finally:
            shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------------------------------------
# Commands


def material_and_graders(slugs: list[str]) -> tuple[list[str], list[str]]:
    material = [f"{s}/README_{l['number']}.md" for s in slugs for l in module_of(s)["lessons"]
                if (ROOT / s / f"README_{l['number']}.md").exists()]
    return material, []


def prove(slug: str, lesson: str | None = None) -> int:
    """Gate every planned exercise of a module's pages (or one lesson's) and write nothing."""
    pages = [p for p in pages_of(slug) if lesson is None or p.path.endswith(f"README_{lesson}.md")]
    material, graders = material_and_graders([slug])
    ledger = take(ROOT, material, graders, "the course ledger")
    run = InRunner()
    failed = 0
    for page in pages:
        outcome = author_page(page, ledger, Author(), judge, run, source=SOURCE, where=page.path, carried=())
        print(page.path, outcome_summary(outcome))
        failed += bool(outcome.shortfalls)
    return 1 if failed else 0


def outcome_summary(outcome) -> str:
    shipped, shortfalls = outcome.shipped, outcome.shortfalls
    lines = [f"{len(shipped)} cleared, {len(shortfalls)} refused"]
    for s in shortfalls:
        lines.append(f"  REFUSED slot {s.slot} {s.gate}: {s.says}")
        out = s.output
        if out:
            lines.append("    " + "\n    ".join(out.strip().splitlines()[-25:]))
    return "\n".join(lines)


def ship(slugs: list[str]) -> int:
    pages = [p for s in slugs for p in pages_of(s)]
    material, graders = material_and_graders(slugs)
    authored = author_corpus(ROOT, source=SOURCE, material=material, graders=graders, pages=pages,
                             author=Author(), judge=judge, runner=InRunner())
    for where, missed in authored.shortfalls:
        print("SHORTFALL", where, missed.slot, missed.gate, missed.says)
    print("pages with nothing shipped:", authored.bare)
    return 1 if authored.shortfalls else 0


def regate(slugs: list[str]) -> int:
    """Gate every shipped page again and write its code practices' bundles back in place.

    `ship` is additive: a page it already shipped is reused, never re-gated. After a change to the
    practices' sources (a try-it file added to each), this gates each page once more and writes
    the files of each code practice that clears over the bundle it replaces. A page whose gated
    practices are not exactly the bundles it shipped is refused and nothing of it is written.
    """
    from studyforge.skills.exercises.corpus import carried_practices
    material, graders = material_and_graders(slugs)
    ledger = take(ROOT, material, graders, "the course ledger")
    run = InRunner()
    failed = 0
    for page in (p for s in slugs for p in pages_of(s)):
        where = f"the page '{page.path}'"
        outcome = author_page(page, ledger, Author(), judge, run, source=SOURCE, where=where,
                              carried=carried_practices(ROOT, page, where))
        code = [g for g in outcome.shipped if (ROOT / g.places.bundle / "bundle.json").exists()
                and json.loads(text(ROOT / g.places.bundle / "bundle.json")).get("main_file")]
        on_disk = sorted(str(b.parent.relative_to(ROOT)) for b in ROOT.glob(f"exercises/**/{page.path.split('/')[0]}/"
                         f"{page.variant}/unit-{page.unit:02d}/practice-*/bundle.json")
                         if json.loads(text(b)).get("main_file"))
        if outcome.shortfalls or sorted(str(g.places.bundle) for g in code) != on_disk:
            failed += 1
            print(page.path, "NOT WRITTEN", outcome_summary(outcome), "on disk:", on_disk, flush=True)
            continue
        for gated in code:
            for path, data in gated.files:
                target = ROOT / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        print(page.path, f"rewrote {len(code)}", flush=True)
    return 1 if failed else 0


Q1_PROMPT = ("Read the whole lesson page, then this question. Using only what the page states, which option "
             "does the page decide is correct? Quote or cite the deciding passage.")
Q3_PROMPT = ("Using only what the lesson page states, does a passage of the page rule this option out? "
             "Cite the passage, or say none does or that the option is partly true. Be strict.")


def record_readings(q2_files: list[str], q13_files: list[str], q2_by: str, q13_by: str) -> int:
    """Merge the readers' answers into each lesson's quiz/readings.json, over the current wording.

    A page-free answer is taken from the newest file that holds the question's key; a page reading
    likewise. Each reading is stamped with the question's current digest, so a later rewording
    makes it stale and the judge refuses it.
    """
    q2: dict = {}
    for f in q2_files:
        q2.update(json.loads(Path(f).read_text(encoding="utf-8")))
    q13: dict = {}
    for f in q13_files:
        q13.update(json.loads(Path(f).read_text(encoding="utf-8")))
    written = 0
    for slug in sorted({k.split("/")[0] for k in q13}):
        for page in pages_of(slug):
            if not page.quiz:
                continue
            target = lesson_dir(page) / page.quiz / "readings.json"
            # Merge over what is stored: a batch that covers some of a lesson's questions keeps the others.
            out = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
            before = dict(out)
            for q in questions_of(page, page.quiz):
                key = f"{page.path}#{q.id}"
                if key not in q2 or key not in q13:
                    continue
                page_read = q13[key]
                out[q.id] = {
                    "over": question_digest(q),
                    "q2": {"picked": q2[key]["picked"], "because": q2[key]["because"], "taken_by": q2_by},
                    "q1": {"picked": page_read["picked"], "outcome": page_read["outcome"], "prompt": Q1_PROMPT,
                           "taken_by": q13_by},
                    "q3": {o.id: {"refuted": page_read["q3"][o.id]["refuted"], "outcome": page_read["q3"][o.id]["outcome"],
                                  "prompt": Q3_PROMPT, "taken_by": q13_by}
                           for o in q.options if not o.correct},
                }
            if out != before:
                target.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            written += sum(1 for k in out if out[k] != before.get(k))
    print(f"recorded {written} question readings")
    return 0


def main(argv: list[str]) -> int:
    verb, *args = argv
    if verb == "prove":
        return prove(*args)
    if verb == "readings":
        print(json.dumps({k: v for s in args for k, v in readings_brief(s).items()}, indent=1, ensure_ascii=False))
        return 0
    if verb == "ship":
        return ship(args)
    if verb == "regate":
        return regate(args)
    if verb == "record":
        # record <q2 files,comma> <q13 files,comma> <q2 reader label> <page reader label>
        return record_readings(args[0].split(","), args[1].split(","), args[2], args[3])
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
