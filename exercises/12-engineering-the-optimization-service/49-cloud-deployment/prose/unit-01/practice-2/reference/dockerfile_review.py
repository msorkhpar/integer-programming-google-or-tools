from __future__ import annotations

SECRET_WORDS = ("KEY", "SECRET", "TOKEN", "PASSWORD")


def instructions(dockerfile: str) -> list[tuple[str, str]]:
    """(INSTRUCTION, rest) for every instruction line; comments and blank lines dropped."""
    out = []
    for line in dockerfile.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            word, _, rest = line.partition(" ")
            out.append((word.upper(), rest.strip()))
    return out


def review(dockerfile: str) -> list[str]:
    """The findings for a Dockerfile, sorted, each at most once."""
    findings: set[str] = set()
    stages: set[str] = set()
    user = None
    for word, rest in instructions(dockerfile):
        if word == "FROM":
            parts = rest.split()
            image = parts[0]
            if len(parts) >= 3 and parts[1].upper() == "AS":
                stages.add(parts[2])
            user = None                                   # each stage starts as root
            if image in stages or image.lower() == "scratch":   # an earlier stage, or the empty image
                continue
            name = image.split("@")[0]
            tag = name.rsplit(":", 1)[1] if ":" in name.rsplit("/", 1)[-1] else None
            if "@sha256:" not in image and tag in (None, "latest"):
                findings.add("base-not-pinned")
        elif word == "USER":
            user = rest.split(":")[0]
        elif word in ("ENV", "ARG"):
            for pair in rest.split():
                key = pair.split("=", 1)[0].upper()
                if any(w in key for w in SECRET_WORDS):
                    findings.add("secret-in-env")
        elif word in ("CMD", "ENTRYPOINT") and not rest.startswith("["):
            findings.add("shell-form-cmd")
    if user in (None, "root", "0"):
        findings.add("runs-as-root")
    return sorted(findings)
