# 6.6. Piecewise-Linear Functions

Costs and values that bend: writing a convex cost (or a concave value) with segment variables and
no binaries, and knowing when that is allowed; the lambda form, whose segment binaries keep the
weights on two neighbouring breakpoints (SOS2) for a curve of any shape; the incremental and
logarithmic forms, compared by size, LP bound and search; and lifecycle value curves for partial
asset renewal, built from GridCap's failure model and checked against Pyomo's `Piecewise`.

## Contents

1. [Convex piecewise costs without binaries](README_6.6.1.md)
2. [The lambda (SOS2-style) formulation built from binaries](README_6.6.2.md)
3. [Incremental and logarithmic formulations](README_6.6.3.md)
4. [Lifecycle value curves for asset renewal](README_6.6.4.md)
