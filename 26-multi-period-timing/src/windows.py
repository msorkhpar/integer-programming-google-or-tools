"""How many start variables a timing model needs, with and without timing windows."""

from gridcap import generate

for size in ("tiny", "small", "medium", "large"):
    pf = generate(size)
    windowed = sum(len(p.starts()) for p in pf.projects)
    full = sum(len(pf.years) - p.duration + 1 for p in pf.projects)
    print(f"{size:6} {len(pf.projects):>6} projects  {len(pf.years):>2} years  "
          f"windowed {windowed:>6}  whole horizon {full:>6}")

tiny = generate("tiny")
print("tiny start variables:", ", ".join(f"x[{p.project_id},{t}]" for p in tiny.projects for t in p.starts()))
