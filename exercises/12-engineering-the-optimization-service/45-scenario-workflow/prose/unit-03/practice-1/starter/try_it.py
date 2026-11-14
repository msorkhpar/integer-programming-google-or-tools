"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from approval import allowed, reachable, walk

print("Draft: submit, reject, submit:", walk("Draft", ["submit", "reject", "submit"]))
print("Submitted: approve, edit, archive:", walk("Submitted", ["approve", "edit", "archive"]))
print("actions from Draft:", allowed("Draft"))
print("actions from Approved:", allowed("Approved"))
print("reachable from Submitted:", reachable("Submitted"))
print("reachable from Archived:", reachable("Archived"))
