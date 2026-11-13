"""Draw the budget split with matplotlib: the region, its boundary lines, three level lines and the best vertex."""

import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())
import matplotlib.pyplot as plt  # noqa: E402

from level_lines import LETTER  # noqa: E402
from split_lp import ROWS  # noqa: E402
from vertices import vertices  # noqa: E402

corners = sorted(vertices(), key=lambda p: "ABCDE".index(LETTER[p]))
fig, ax = plt.subplots(figsize=(6, 5))
ax.fill([p[0] for p in corners], [p[1] for p in corners], color="#cfe3f5", label="feasible region")
for label, ((a_d, a_t), b) in ROWS.items():
    if a_t == 0:
        ax.axvline(b / a_d, label=label)
    else:
        ax.plot([0, 32], [b / a_t, (b - a_d * 32) / a_t], label=label)
for level, style in ((60, ":"), (100, ":"), (132, "--")):
    ax.plot([0, 32], [level / 4, (level - 5 * 32) / 4], "k" + style, linewidth=1)
    ax.annotate(f"5d+4t={level}", (0.3, level / 4 + 0.4), fontsize=8)
for p in corners:
    ax.annotate(LETTER[p], p, textcoords="offset points", xytext=(4, 4))
ax.plot([12], [18], "ko")
ax.set(xlim=(0, 32), ylim=(0, 26), xlabel="d: distribution ($100k)", ylabel="t: transmission ($100k)")
ax.legend(loc="upper right", fontsize=8)
out = Path(tempfile.gettempdir()) / "feasible_region.png"
fig.savefig(out, dpi=120)
print(f"saved {out.name} in the temp folder: {len(corners)} vertices, 3 level lines, best vertex C (12, 18)")
