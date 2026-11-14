"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from license_plan import license_plan

# Made-up environments and a made-up file system; nothing here reads the real ones.
files = {"/opt/gurobi/gurobi.lic", "/srv/learner/gurobi.lic", "/mnt/keys/site.lic"}


def exists(path):
    return path in files


key = {"WLSACCESSID": "0000-demo", "WLSSECRET": "1111-demo", "LICENSEID": "1234"}
print("full WLS key:", license_plan(key, exists))
print("WLS key without secret:", license_plan({"WLSACCESSID": "0000-demo", "LICENSEID": "1234"}, exists))
print("GRB_LICENSE_FILE /mnt/keys/site.lic:", license_plan({"GRB_LICENSE_FILE": "/mnt/keys/site.lic"}, exists))
print("GRB_LICENSE_FILE /mnt/keys/gone.lic:", license_plan({"GRB_LICENSE_FILE": "/mnt/keys/gone.lic"}, exists))
print("HOME /srv/learner:", license_plan({"HOME": "/srv/learner"}, exists))
print("HOME /srv/learner, no /opt file:", license_plan({"HOME": "/srv/learner"}, lambda p: p == "/srv/learner/gurobi.lic"))
