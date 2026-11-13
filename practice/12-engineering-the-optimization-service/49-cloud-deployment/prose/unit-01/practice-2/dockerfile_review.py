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
    # TODO: walk instructions(dockerfile) and add base-not-pinned, runs-as-root, secret-in-env, shell-form-cmd.
    return sorted(findings)
