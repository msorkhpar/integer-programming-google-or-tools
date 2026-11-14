"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from converged import converged_at, table_rows

head = " iter# kkt_pass   time | rel_prim_res rel_dual_res      rel_gap |   prim_resid   dual_resid      obj_gap"


def row(iteration, prim, dual, gap):
    return (f"{iteration:6d} {iteration + 1:8.1f}    0.0 | {prim:12.5e} {dual:12.5e} {gap:12.5e} "
            f"|      1.00000      2.00000      3.00000")


log = ["Solving with PDLP", head,
       row(0, 5.0e-2, 0.7, 0.1), row(40, 2.0e-4, 9.0e-5, -3.0e-4), row(80, 4.0e-7, 6.0e-7, 2.0e-7)]
print("rows read:", table_rows(log))
print("converged at tol 1e-3:", converged_at(log, 1e-3))
print("converged at tol 1e-6:", converged_at(log, 1e-6))
print("converged at tol 1e-9:", converged_at(log, 1e-9))
