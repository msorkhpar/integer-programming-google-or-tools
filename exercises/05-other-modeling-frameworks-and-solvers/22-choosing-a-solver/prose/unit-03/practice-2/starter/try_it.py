"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from xproute import xpress_license

# A made-up environment and a made-up set of files in the container.
files = {"/srv/keys/xp/xpauth.xpr", "/srv/app/run.py"}
print("XPRESS=/srv/keys/xp:", xpress_license({"XPRESS": "/srv/keys/xp"}, files))
print("XPRESS=/srv/keys/xp/:", xpress_license({"XPRESS": "/srv/keys/xp/"}, files))
print("XPRESS=/srv/keys/xp/xpauth.xpr:", xpress_license({"XPRESS": "/srv/keys/xp/xpauth.xpr"}, files))
print("XPRESS=/srv/other:", xpress_license({"XPRESS": "/srv/other"}, files))
print("XPRESS unset:", xpress_license({"LANG": "C"}, files))
