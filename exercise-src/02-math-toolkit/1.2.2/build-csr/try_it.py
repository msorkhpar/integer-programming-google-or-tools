"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from csr import to_csr

# Rows are depots, columns are trucks; one entry is given twice, row 1 is empty.
triplets = [(2, 1, 5), (0, 3, 2), (0, 0, 7), (2, 1, 1), (3, 2, 4)]
indptr, indices, data = to_csr(4, triplets)
print("indptr:", indptr)
print("indices:", indices)
print("data:", data)
