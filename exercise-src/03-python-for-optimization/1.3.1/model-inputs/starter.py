from __future__ import annotations

import pandas as pd


def model_inputs(projects: pd.DataFrame, npv: pd.DataFrame) -> tuple[dict, dict, dict]:
    """Return (capex, value, parent): three dicts keyed by project id."""
    # TODO: build the three dicts the model indexes (see the statement).
    return {}, {}, {}


if __name__ == "__main__":
    import io
    projects = pd.read_csv(io.StringIO("project_id,cost_profile,earliest_start,parent\nA,100;50,2030,\nB,70,2031,A\n"))
    npv = pd.read_csv(io.StringIO("project_id,start_year,npv\nA,2030,210\nB,2031,95\n"))
    print(model_inputs(projects, npv))
