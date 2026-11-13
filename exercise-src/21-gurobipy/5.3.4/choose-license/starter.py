from __future__ import annotations

from typing import Callable

WLS = ("WLSACCESSID", "WLSSECRET", "LICENSEID")


def license_plan(environ: dict[str, str], exists: Callable[[str], bool]) -> tuple[str, object]:
    """('wls', params), ('file', path) or ('error', message), by the rules of the statement."""
    # TODO: the WLS key first (whole or partial), then GRB_LICENSE_FILE, then the default places.
    return ("error", "no license")


if __name__ == "__main__":
    print(license_plan({"GRB_LICENSE_FILE": "/licenses/gurobi.lic"}, lambda path: True))
