"""Read this source. ⛔ THE ONE MODULE IN THIS PACKAGE YOU WRITE BY HAND.

**What it does.** Turns this repository's material into the two things the archive is made of. ⭐ `containers` and `expected_units` are already written: `corpus.json` declares where the curriculum is recorded and what each group is filed at, and `studyforge.skills.adapter.curriculum` reads it and refuses a tree that disagrees. `documents` is yours.

**How you use it.** Write `documents`. Run the tests beside this package after it: they fail carrying the refusal's own message, and pass when the archive validates. ⛔ Change the filing in `corpus.json`, never here.

**Depends on.** `studyforge.corpus.manifest` for the declaration, `studyforge.skills.adapter.curriculum` for the filing and the name count, and `studyforge.corpus.container` for `Container`. ⭐ `studyforge.archive.markdown` reads Markdown into blocks for `documents`; ⚠️ add whatever else it needs to read this source's material.
"""

from __future__ import annotations


import textwrap
from pathlib import Path

from studyforge.archive.markdown import parse
from studyforge.corpus.container import Container
from studyforge.corpus.manifest import MANIFEST_FILENAME, load
from studyforge.skills.adapter.curriculum import counted, filed

#: What every unwritten step says. ⭐ One sentence of what to return, and
#: one of why a guess would be worse than a refusal.
UNWRITTEN = (
    "ingest.read.{step} is not written yet. {what} "
    "Until it is, this adapter refuses rather than emitting an archive "
    "that validates and holds the wrong material."
)

#: The one variant this corpus declares.
VARIANT = 'prose'


def containers(root: Path) -> list[Container]:
    """Return one `Container` per group `corpus.json` declares, filed by its record.

    ⛔ **The address is recorded, never derived** (§6): the manifest records
    it, and the filing refuses when the record or a declared prefix disagrees.
    ⚠️ `ingested` is replaced by `emit` with the run's own date.
    """
    manifest = load(Path(root) / MANIFEST_FILENAME)
    return [
        Container(
            address=group.address,
            titles=group.titles,
            variant=VARIANT,
            ingested="1970-01-01",
            units=group.units,
            origin=group.origin,
        )
        for group in filed(root, manifest)
    ]


def documents(root: Path, container: Container) -> list[dict]:
    """Return the fields for each document of `container`, in reading order.

    Each dict is the keyword arguments of `studyforge.archive.document.build`
    minus `source` and `ingested`, which `emit` supplies: `address`,
    `variant`, `unit`, `kind`, `ordinal`, `title`, `blocks`.

    ⛔ **Every block comes from the block vocabulary** (`studyforge.archive.blocks`).
    A construct the reader does not recognise is reported, never dropped: a
    dropped block is absent from the digest and from the counts alike, so
    nothing downstream can notice it went missing.

    ⭐ **Markdown material has a reader already**:
    `studyforge.archive.markdown.parse(text)` returns the blocks, and raises
    `MarkdownError` naming what it cannot hold rather than dropping it.

    ⛔ **Return the source's own material only.** Every exercise the
    authoring pass committed under `exercises/`, code and quiz alike, is
    joined to its unit by `emit` (`studyforge.skills.adapter.practices`),
    which also raises the unit's practice count: reading one here as well
    is kept only when it is that exercise's own document.
    """
    return [
        {
            "address": container.address,
            "variant": VARIANT,
            "unit": unit.n,
            "kind": "lesson",
            "ordinal": 1,
            "title": unit.title,
            "blocks": runnable(Path(root), unit.origin, parse((Path(root) / unit.origin).read_text("utf-8"))),
        }
        for unit in container.units
    ]


#: The language every runnable example is written in, as `corpus.json` declares it.
PYTHON = "python"
#: What a runnable example's program imports besides its own folder: the GridCap package.
SUPPORT = "00-base"


def _lines(text: str) -> list[str]:
    return [line.strip() for line in textwrap.dedent(text).splitlines() if line.strip()]


def _lifted_from(snippet: str, programs: dict[str, list[str]]) -> list[str]:
    """The programs whose source holds every line of `snippet`, in order (as verify_lessons reads it)."""
    wanted = _lines(snippet)
    found = []
    for path, source in programs.items():
        rest = iter(source)
        if wanted and all(any(line == s for s in rest) for line in wanted):
            found.append(path)
    return found


def runnable(root: Path, origin: str, blocks: list[dict]) -> list[dict]:
    """Turn each ```python fence lifted from one program of the lesson's module into an example.

    The tab names the program (`code`) and the command that runs it (`run`), so a served page
    offers Run and shows what the program prints. An ```text fence directly under it is its
    output and joins the example; prose between the two keeps them apart. A fence lifted from
    no program, or from more than one, stays a plain code block.
    """
    module = Path(origin).parts[0]
    programs = {f"{module}/src/{f.name}": _lines(f.read_text("utf-8"))
                for f in sorted((root / module / "src").glob("*.py"))}
    # ⭐ Only a program prints something to show; a library a lesson quotes (timing_model) does not.
    runs = {path for path in programs
            if "__main__" in (root / path).read_text("utf-8")
            or any(line.startswith("print(") for line in (root / path).read_text("utf-8").splitlines())}
    out: list[dict] = []
    i = 0
    while i < len(blocks):
        block = blocks[i]
        found = _lifted_from(block.get("text", ""), programs) if (
            block.get("type") == "code" and block.get("lang") == PYTHON) else []
        if len(found) != 1 or found[0] not in runs:
            out.append(block)
            i += 1
            continue
        held = [block]
        while i + len(held) < len(blocks) and blocks[i + len(held)].get("type") == "code" \
                and blocks[i + len(held)].get("lang") == "text":
            held.append(blocks[i + len(held)])
        program = found[0]
        n = sum(1 for b in out if b.get("type") == "example") + 1
        out.append({
            "type": "example",
            "id": f"{Path(program).stem}-{n}",
            "tabs": [{"lang": PYTHON, "span": len(held), "code": program,
                      "run": ["env", f"PYTHONPATH={SUPPORT}", "MPLBACKEND=Agg", "python3", program]}],
            "blocks": held,
            "support": [SUPPORT],
        })
        i += len(held)
    return out


def expected_units(root: Path) -> dict[str, int] | None:
    """Return `{address key: unit count}` counted from the names on disk, or None.

    ⭐ **The second reading**: every included file carrying a declared prefix,
    or under a linked level, every included file in each linked file's
    directory, taken without the record. ⚠️ `None` while a declared group
    has no prefix, and the audit then reports an unchecked claim — count
    that group here.
    """
    return counted(Path(root), load(Path(root) / MANIFEST_FILENAME))
