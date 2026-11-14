"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from book import checked, copy, create, edit, lock, optimized

book = {}
print("create 'lean':", create(book, "lean", {"budget": 750}))
print("optimize before checks:", optimized(book, "lean", {"P4": 2030}))
print("checked, optimized:", checked(book, "lean"), optimized(book, "lean", {"P4": 2030}))
print("edit after optimizing:", edit(book, "lean", {"budget": 700}), book["lean"]["stage"], book["lean"]["plan"])
checked(book, "lean")
optimized(book, "lean", {"P4": 2031})
print("lock 'lean':", lock(book, "lean"), book["lean"]["stage"])
print("copy to 'lean-b':", copy(book, "lean", "lean-b"), book["lean-b"])
print("edit locked 'lean':", edit(book, "lean", {"budget": 650}))
