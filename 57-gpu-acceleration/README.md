# 11.4. GPU Acceleration

When a graphics card helps an LP or MILP solve, and when it does not: why first-order LP methods
(PDHG and PDLP) suit a GPU, how a program finds out whether it has one and falls back to the CPU
with the same answer, a measured comparison of HiGHS's GPU PDLP (cuPDLP-C), NVIDIA cuOpt and
OR-Tools' CPU PDLP, what repeats on a GPU and what a run manifest must record, which parts of a MIP
solve cuOpt moves to the GPU, and one run policy for threads, workers and devices.

The GPU is optional. Every program, test and practice of this module runs on the course's CPU
image and passes there. A learner with an NVIDIA GPU and the toolchain's optional GPU image gets
extra checks that run on the card; everyone else gets the CPU half and the numbers this course
measured on its build machine, marked as such. GridCap is a fictional utility.

## Contents

1. [Why first-order LP methods suit a GPU: PDHG and PDLP](README_11.4.1.md)
2. [Detecting a GPU, with a CPU fallback that gives the same answer](README_11.4.2.md)
3. [PDLP on CPU vs. GPU: a measured comparison with HiGHS (cuPDLP-C) and OR-Tools](README_11.4.3.md)
4. [Determinism on a GPU: what repeats, what doesn't, and what the manifest records](README_11.4.4.md)
5. [MIP on a GPU: what cuOpt accelerates and why branch-and-bound stays on the CPU](README_11.4.5.md)
6. [One run policy for threads, workers and the GPU](README_11.4.6.md)
