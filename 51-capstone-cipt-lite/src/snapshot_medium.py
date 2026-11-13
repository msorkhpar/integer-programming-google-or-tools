"""Lesson 13.1.1: GridCap medium read, validated and snapshotted, and the content hash put to the test.

The same content is exported three ways (as written, with every CSV's rows reversed, with the
discount rate written as 0.0700000001), and hashed in two fresh processes with different hash
salts. One real change, a single cost $10k higher, must give a new digest. GridCap is fictional.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from cipt_data import Corrupted, SnapshotStore, snapshot
from gridcap import generate, save_csv

CHILD = "import sys; from cipt_data import snapshot; print(snapshot(sys.argv[1])[1][:12])"


def reverse_rows(folder: Path) -> None:
    for path in folder.glob("*.csv"):
        head, *rows = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join([head, *reversed(rows)]) + "\n", encoding="utf-8")


def in_child(folder: Path, seed: str) -> str:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    return subprocess.run([sys.executable, "-c", CHILD, str(folder)], env=env, capture_output=True,
                          text=True, check=True).stdout.strip()


if __name__ == "__main__":
    medium = generate("medium")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        first = save_csv(medium, tmp / "first")
        pf, key, warnings = snapshot(first)
        print(f"{pf.name}: {len(pf.projects)} projects, {len(pf.assets)} assets, {len(pf.years)} years, "
              f"{sum(p.must_do for p in pf.projects)} must-do")
        print(f"accepted with {len(warnings)} warning(s); digest {key[:12]}")
        for w in warnings[:3]:
            print(f"   warning {w.rule:<16} {w.subject:<6} {w.detail}")

        second = save_csv(medium, tmp / "second")
        reverse_rows(second)
        third = save_csv(medium, tmp / "third")
        scalars = json.loads((third / "portfolio.json").read_text(encoding="utf-8"))
        scalars["discount_rate"] = 0.0700000001
        (third / "portfolio.json").write_text(json.dumps(scalars), encoding="utf-8")
        changed = save_csv(medium, tmp / "changed")
        text = (changed / "projects.csv").read_text(encoding="utf-8")
        p = medium.project("P101")
        old = ";".join(map(str, p.cost_profile))
        new = ";".join(map(str, (p.cost_profile[0] + 10,) + p.cost_profile[1:]))
        (changed / "projects.csv").write_text(text.replace(f",{old},", f",{new},", 1), encoding="utf-8")

        print()
        print(f"{'export':<34} digest")
        print(f"{'as written':<34} {key[:12]}")
        print(f"{'every CSV in reverse row order':<34} {snapshot(second)[1][:12]}")
        print(f"{'discount rate 0.0700000001':<34} {snapshot(third)[1][:12]}")
        print(f"{'P101 first-year cost $10k higher':<34} {snapshot(changed)[1][:12]}")
        print(f"{'as written, PYTHONHASHSEED=1':<34} {in_child(first, '1')}")
        print(f"{'as written, PYTHONHASHSEED=2':<34} {in_child(first, '2')}")

        store = SnapshotStore(tmp / "store")
        a, b = store.put(pf), store.put(snapshot(second)[0])
        print()
        print(f"store: put twice -> same key {a == b}, files {len(list(store.root.iterdir()))}")
        print(f"read back equals the original: {store.get(a) == pf}")
        path = store.root / f"{a}.json"
        path.write_bytes(path.read_bytes().replace(b'"2029":39190', b'"2029":39990'))
        try:
            store.get(a)
        except Corrupted as error:
            print(f"after an edit in place: refused, {error}")
