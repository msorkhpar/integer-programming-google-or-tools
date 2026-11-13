"""A start-up check for a containerized solver service: which Gurobi license route is configured (lesson 5.4.3).

It decides from configuration alone and never opens, prints or logs a credential: the service's log
says which route it will use and which names are set, never their values. Every value below is a
placeholder; no real license or credential exists in this course.

Routes, from Gurobi's container documentation (pages opened 2026-11-11):
- WLS: the three parameters WLSACCESSID, WLSSECRET and LICENSEID, given to the program (in a
  license file or through the API); the container then needs outbound internet access.
- a license file mounted read-only at run time, named by GRB_LICENSE_FILE (never baked into the image);
- neither: only the size-limited license that ships with the pip package.
"""

from __future__ import annotations

WLS_KEYS = ("WLSACCESSID", "WLSSECRET", "LICENSEID")


def route(settings: dict[str, str], mounted: set[str]) -> str:
    """The license route `settings` (environment and parameters) and `mounted` files configure."""
    present = [k for k in WLS_KEYS if settings.get(k)]
    if present and len(present) < len(WLS_KEYS):
        missing = ", ".join(k for k in WLS_KEYS if k not in present)
        return f"broken WLS setup: missing {missing}"
    if present:
        return "WLS (needs outbound internet)"
    path = settings.get("GRB_LICENSE_FILE")
    if path:
        return f"mounted license file at {path}" if path in mounted else f"GRB_LICENSE_FILE set, but nothing mounted at {path}"
    return "size-limited pip license only"


def log_line(settings: dict[str, str], mounted: set[str]) -> str:
    """What the service writes at start-up: the route and the names that are set, never a value."""
    names = sorted(k for k in settings if k in WLS_KEYS + ("GRB_LICENSE_FILE",) and settings[k])
    return f"license route: {route(settings, mounted)}; set: {', '.join(names) or 'nothing'}"


if __name__ == "__main__":
    examples = {
        "WLS in a Fargate task": ({"WLSACCESSID": "example-access-id", "WLSSECRET": "example-secret",
                                   "LICENSEID": "123456"}, set()),
        "WLS with the secret missing": ({"WLSACCESSID": "example-access-id", "LICENSEID": "123456"}, set()),
        "file mounted read-only": ({"GRB_LICENSE_FILE": "/licenses/gurobi.lic"}, {"/licenses/gurobi.lic"}),
        "file named, mount forgotten": ({"GRB_LICENSE_FILE": "/licenses/gurobi.lic"}, set()),
        "nothing configured": ({}, set()),
    }
    for label, (settings, mounted) in examples.items():
        line = log_line(settings, mounted)
        assert not any(v in line for k, v in settings.items() if k in ("WLSSECRET", "WLSACCESSID"))
        print(f"{label:<28} {line}")
