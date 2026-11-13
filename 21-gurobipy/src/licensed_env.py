"""Lesson 5.3.4: one function that opens a Gurobi environment from whatever license the deployment provides.

`env_params` reads the process's environment variables and returns the parameters for `gp.Env`:
a WLS key when all three of WLSACCESSID, WLSSECRET and LICENSEID are set (the names of Gurobi's own
parameters, used here as the variable names too), nothing extra otherwise, in which case Gurobi
finds a license file itself (GRB_LICENSE_FILE, then its default places). `redacted` is the only
form in which the parameters are ever printed or logged. The demo uses placeholder values and
starts no environment, so it sends nothing anywhere.
"""

from __future__ import annotations

import gurobipy as gp

WLS = ("WLSACCESSID", "WLSSECRET", "LICENSEID")


def env_params(environ: dict[str, str]) -> dict:
    """Parameters for gp.Env(params=...): quiet always, plus a complete WLS key if one is given."""
    params: dict = {"OutputFlag": 0}
    present = [name for name in WLS if environ.get(name)]
    if len(present) == len(WLS):
        params.update(WLSACCESSID=environ["WLSACCESSID"], WLSSECRET=environ["WLSSECRET"],
                      LICENSEID=int(environ["LICENSEID"]))
    elif present:
        missing = ", ".join(name for name in WLS if name not in present)
        raise ValueError(f"incomplete WLS key: {missing} not set")
    return params


def redacted(params: dict) -> dict:
    """The parameters with every license value replaced by '<set>'."""
    return {k: ("<set>" if k in WLS else v) for k, v in params.items()}


def open_env(environ: dict[str, str]) -> gp.Env:
    """A started, quiet environment from the deployment's license (raises GurobiError if there is none)."""
    return gp.Env(params=env_params(environ))


if __name__ == "__main__":
    placeholder = {"WLSACCESSID": "00000000-0000-0000-0000-000000000000",
                   "WLSSECRET": "11111111-1111-1111-1111-111111111111", "LICENSEID": "123456"}
    deployments = {
        "course runner, license file mounted": {"GRB_LICENSE_FILE": "/licenses/gurobi.lic"},
        "container with a WLS key           ": placeholder,
        "container with half a WLS key      ": {"WLSACCESSID": placeholder["WLSACCESSID"]},
    }
    for label, environ in deployments.items():
        try:
            print(f"{label}: {redacted(env_params(environ))}")
        except ValueError as error:
            print(f"{label}: refused, {error}")
