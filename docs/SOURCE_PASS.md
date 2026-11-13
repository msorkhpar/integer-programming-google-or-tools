# Source Pass Brief

A source pass brings already-written modules up to the sources rule (docs/AUTHORING.md section 2):
the OR-Tools documentation is the primary source, its examples are adapted where they teach, and
every lesson ends its Reference section with a **Further reading** line.

You are given a few modules and a worktree. Read docs/AGENT_BRIEF.md first; its environment, limits,
checks and personal-data rules apply to you. You edit only the modules you were given:
`<module>/README*.md`, `<module>/src/`, `<module>/tests/`. Don't touch exercise-src (practices
and quizzes have passed their readers) unless a lesson change makes a practice statement wrong;
if so, report it rather than editing.

## For each lesson

1. **Open the sources.**
   - The OR-Tools pages for every OR-Tools topic the lesson touches
     (https://developers.google.com/optimization: MathOpt, LP/GLOP/PDLP, MIP, CP-SAT, assignment,
     packing, scheduling, flows, routing) and the matching samples in github.com/google/or-tools
     (`ortools/math_opt/samples/python`, `ortools/sat/samples`, `ortools/linear_solver/samples`,
     `ortools/graph/samples`, `ortools/algorithms/samples`, `ortools/constraint_solver/samples`).
   - The blueprint's resource library row for the section (docs/plan/blueprint.md).
   - The entries of docs/plan/resource-links.md that match the lesson's topic.
2. **Check the lesson against them.** Where an API claim, a definition or a statement disagrees with
   the OR-Tools pages or the sources, correct the lesson. A correction about solver behaviour needs a
   program that shows it, run in the runner.
3. **Place OR-Tools examples where they teach.** Where an OR-Tools sample illustrates the lesson's
   point (the LP and MIP examples, the Stigler diet, knapsack, assignment, bin packing, the CP-SAT
   examples), adapt it into a program in `src/` with the comment
   `# Adapted from the OR-Tools example <name>, <URL>`, show it inline with the output it printed,
   say in the prose where it came from, and list it in The Full Programs. One well-chosen example per
   lesson that touches OR-Tools is the aim; don't force one into a lesson about pandas or convexity.
   Never copy the documentation's prose.
4. **Add the Further reading line** as the last line of the Reference section:
   `**Further reading:** [Title](URL) (what it adds); [Title](URL) (what it adds).`
   OR-Tools pages first, then the others. Cite only what you opened.

## Checks, once at the end, only on what you changed

`check_math` on each changed page, `verify_lessons` and the module tests for each changed module (in
the runner), and `check_exercises` on your modules; check 7 must pass for every lesson.

## Report

Per lesson: the sources opened, what you corrected (with the program that shows it), the OR-Tools
example placed (if any), and the last result of each check. Commit once, ending the message with
the attribution line you are given.
