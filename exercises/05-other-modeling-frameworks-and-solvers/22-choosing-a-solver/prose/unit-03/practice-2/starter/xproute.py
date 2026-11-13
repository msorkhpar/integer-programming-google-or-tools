from __future__ import annotations

import posixpath


def xpress_license(env: dict[str, str], files: set[str]) -> str:
    """The license route an Xpress Python program in this container will take, from XPRESS and the files present."""
    # TODO: unset or empty, the file named instead of its folder, the file found, or the file missing.
    return ""


if __name__ == "__main__":
    print(xpress_license({"XPRESS": "/licenses/xpress"}, {"/licenses/xpress/xpauth.xpr"}))
    print(xpress_license({}, set()))
