from __future__ import annotations

from typing import Callable

WLS = ("WLSACCESSID", "WLSSECRET", "LICENSEID")


def license_plan(environ: dict[str, str], exists: Callable[[str], bool]) -> tuple[str, object]:
    """('wls', params), ('file', path) or ('error', message), by the rules of the statement."""
    present = [name for name in WLS if environ.get(name)]
    if len(present) == len(WLS):
        return ("wls", {"WLSACCESSID": environ["WLSACCESSID"], "WLSSECRET": environ["WLSSECRET"],
                        "LICENSEID": int(environ["LICENSEID"])})
    if present:
        missing = ", ".join(name for name in WLS if name not in present)
        return ("error", f"incomplete WLS key: {missing} not set")
    if environ.get("GRB_LICENSE_FILE"):
        path = environ["GRB_LICENSE_FILE"]
        return ("file", path) if exists(path) else ("error", f"license file not found: {path}")
    places = ["/opt/gurobi/gurobi.lic"]
    if environ.get("HOME"):
        places.append(environ["HOME"].rstrip("/") + "/gurobi.lic")
    for path in places:
        if exists(path):
            return ("file", path)
    return ("error", "no license")


if __name__ == "__main__":
    print(license_plan({"GRB_LICENSE_FILE": "/licenses/gurobi.lic"}, lambda path: True))
