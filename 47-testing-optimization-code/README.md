# 12.3. Testing Optimization Code

How to know the planning model is right, and stays right: unit tests that check one constraint at a
time on hand-made instances, property-based tests with Hypothesis that try hundreds of generated
portfolios (spend within budget, must-dos always funded, children never without parents), golden
datasets that guard reviewed answers within stated tolerances, and determinism tests and back-tests
against GridCap's (invented) planning history.

## Contents

1. [Unit-testing one constraint at a time](README_12.3.1.md)
2. [Property-based tests with Hypothesis](README_12.3.2.md)
3. [Golden datasets and regression tests](README_12.3.3.md)
4. [Determinism tests and back-testing against history](README_12.3.4.md)
