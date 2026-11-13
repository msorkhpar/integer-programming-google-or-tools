"""The settled onboarding draft for this course: reconnaissance's proposal plus the settled answers.

    python3 scripts/onboard_draft.py plan     # print what onboarding would write
    python3 scripts/onboard_draft.py write    # write it (first onboarding only)

Every answer here was settled by a person (the course's blueprint and its decisions); nothing
is guessed. Later changes go through `reonboard`, never by editing corpus.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = json.loads((ROOT / "docs/plan/curriculum.json").read_text(encoding="utf-8"))


def containers() -> list[dict]:
    """One container per section that has an authored module, as the README record lists them."""
    record = (ROOT / "README.md").read_text(encoding="utf-8")
    out = []
    for number, name in CURRICULUM["sections"].items():
        if f"\n{number}. {name}\n" in record:
            slug = name.lower().replace(" ", "-").replace(",", "").replace(":", "")
            out.append({"label": name, "address": f"{int(number):02d}-{slug}"})
    return out


NOT_MATERIAL = {
    "*/README.md": "each module's contents page: a list of links to its lessons that repeats the curriculum record; the site's own contents replace it",
    "*/src/**": "each module's example programs; the lessons quote and link them, and the runner runs them, but they are code, not reading pages",
    "*/tests/**": "each module's tests of its example programs; they prove the examples, they are not reading pages",
    "00-base/**": "the GridCap dataset generator and its tests, shared by every module's examples; a library, not a lesson",
    "docs/**": "the course's build documents: blueprint, resource list, authoring rules, findings and reports; how the course was made, not course material",
    "scripts/**": "the course's own build tools (curriculum record, lesson verifier, runner wrapper, onboarding draft); tooling, not lesson prose",
    "PROGRESS.md": "the author's module-completion tracker; project status, not lesson prose",
    "README.md": "the repository's overview and the curriculum record the adapter files units from; the generated site carries its own contents",
    "pytest.ini": "the test runner's configuration for the examples' tests; it configures tooling and teaches nothing",
    ".gitignore": "the repository's git ignore rules; version-control configuration, not lesson prose",
    ".idea/**": "the IDE's project settings; editor configuration, not lesson prose",
    "exercise-src/**": "the source files each practice and quiz is authored from (statement, starter, reference, tests, plants, quiz and its readings); scripts/exercises.py turns them into the bundles under exercises/, which are what the site reads",
    "integer-programming-google-or-tools.iml": "the IDE's module file; editor configuration, not lesson prose",
    "exercises/**": "authored exercise bundles and their gate records",
    "practice/**": "the reader's workspace, from each bundle's starter",
}


def draft() -> dict:
    return {
        "corpus_api": 8,
        "source": "integer-programming-python-or-tools",
        "title": "Integer Programming with Python and Google OR-Tools",
        "levels": ["section", "module"],
        "variants": ["prose"],
        "curriculum": {"record": "README.md", "containers": containers(), "linked": "module"},
        "exercises": True,
        "runtimes": ["node", "python"],
        "profile": "optimization",
        "narration": False,
        "placement": "tree",
        "content": {"include": ["*/README_*.md"], "exclude": [],
                    "not_material": [{"glob": g, "why": None} for g in NOT_MATERIAL]},
    }


def main(argv: list[str]) -> int:
    from studyforge.skills.onboarding import onboard
    made = onboard(draft(), reasons=NOT_MATERIAL)
    print("\n".join(made.lines()))
    if argv[1:] == ["write"]:
        made.write(str(ROOT))
        print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
