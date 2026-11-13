from __future__ import annotations

import posixpath


def xpress_license(env: dict[str, str], files: set[str]) -> str:
    """The license route an Xpress Python program in this container will take, from XPRESS and the files present."""
    folder = env.get("XPRESS", "")
    if not folder:
        return "community license"
    if folder.endswith("xpauth.xpr"):
        return "XPRESS names the file; set it to the folder that holds xpauth.xpr"
    path = posixpath.join(folder, "xpauth.xpr")
    if path in files:
        return f"license file {path}"
    return f"no xpauth.xpr in {folder}"


if __name__ == "__main__":
    print(xpress_license({"XPRESS": "/licenses/xpress"}, {"/licenses/xpress/xpauth.xpr"}))
    print(xpress_license({}, set()))
