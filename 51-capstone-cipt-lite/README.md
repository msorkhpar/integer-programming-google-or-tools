# 13.1. Capstone: CIPT Lite

A small, complete Capital Investment Planning Tool on GridCap medium (a fictional utility's
400-project, ten-year portfolio), built in six milestones that each assemble code from earlier
modules: a snapshot that is validated and named by its content hash; the multi-period model with
every rule the data carries, named rows and an independent rule checker; NPV, risk-reduction and
weighted-value coefficient tables; pre-solve checks, a planner message for an infeasible Budget
Lock scenario and a why-deferred report; a determinism harness, Hypothesis properties, golden
records and a warm start; and a FastAPI service with an S3 store tested against moto, a SQLite job
log and a Pareto frontier endpoint.

## Contents

1. [Data: load, validate and snapshot the portfolio](README_13.1.1.md)
2. [Model: multi-period selection with all section 6 rules](README_13.1.2.md)
3. [Value: NPV by start year, risk reduction from PoF/RUL, weighted value](README_13.1.3.md)
4. [Diagnostics: pre-solve checks, IIS message, why-deferred report](README_13.1.4.md)
5. [Trust: determinism harness, Hypothesis properties, golden test, warm start](README_13.1.5.md)
6. [Service: FastAPI job API, moto-tested S3 store, Pareto frontier endpoint](README_13.1.6.md)
