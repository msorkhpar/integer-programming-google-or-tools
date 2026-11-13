# 12.2. Input Data Quality

What stands between a planning export and the solver: a schema read off the model's sets and
parameters, which refuses unknown keys and guessed types and is published as a versioned contract;
a quality gate of named rules that finds parent cycles, impossible precedence and required spend
above every budget before the solve, and tells errors that block from warnings that report; and a
content hash, computed from the validated snapshot in canonical form, that names each version and
lets every reader check the file it fetched.

## Contents

1. [Schemas for model inputs](README_12.2.1.md)
2. [Data-quality checks that prevent infeasibility](README_12.2.2.md)
3. [Versioned snapshots and content hashes](README_12.2.3.md)
