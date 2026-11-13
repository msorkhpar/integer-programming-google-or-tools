# 12.1. The Scenario Workflow

The first module of section 12 turns the planning cycle that lesson 7.1.3 described into working
code. A scenario becomes a record of inputs that can be created, copied and optimized. A planner's
override becomes bounds on start variables, with an append-only audit trail of who changed what,
when and why. The planning stages become a transition table, with version checks against stale
writes and a lock on the plan of record. Last, scenarios, trails and runs are stored in SQLite. The rest of section 12 builds on this module: input checks
and snapshots (lessons 12.2.1 to 12.2.3), tests (lessons 12.3.1 to 12.3.4), a REST API (lessons
12.4.1 to 12.4.3) and deployment (lessons 12.5.1 to 12.5.6).

## Contents

1. [Scenarios as data: create, copy, optimize](README_12.1.1.md)
2. [Manual overrides as bounds, with an audit trail](README_12.1.2.md)
3. [Planning-cycle states and locking](README_12.1.3.md)
4. [Storing scenarios and results in SQLite](README_12.1.4.md)
