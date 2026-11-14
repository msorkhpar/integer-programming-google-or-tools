"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import io

import pandas as pd

from inputs import model_inputs

projects = pd.read_csv(io.StringIO("""project_id,cost_profile,earliest_start,parent
M1,100;60,2034,
M2,75,2035,M1
M3,40;40;20,2034,
"""))
npv = pd.read_csv(io.StringIO("""project_id,start_year,npv
M1,2034,280
M1,2035,250
M2,2035,110
M3,2034,95
M3,2035,70
"""))
capex, value, parent = model_inputs(projects, npv)
print("capex:", capex)
print("value:", value)
print("parent:", parent)
