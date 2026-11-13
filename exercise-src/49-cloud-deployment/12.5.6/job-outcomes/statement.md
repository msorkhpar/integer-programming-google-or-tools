Before the trim planner's workflow goes live, the team wants to answer "if this job fails, what
still runs?" for any workflow, without pushing commits to find out. Model GitHub's rule from the
lesson.

In `job_outcomes.py`, write `outcomes(jobs, event, failing=frozenset())`. `jobs` maps each job's
name to its settings: `needs` (one name or a list, maybe missing) and `if` (maybe missing). It returns
each job's outcome for one event: `"success"`, `"failure"` or `"skipped"`. A job that runs ends in
`"failure"` if its name is in `failing`, and in `"success"` otherwise.

- An `if` of the form `github.event_name == 'NAME'` skips the job when the event is not `NAME`.
- A job whose needs did not all succeed (one failed, or one was skipped) is skipped, unless its `if`
  contains `always()`, which runs it whatever its needs did.
- An `if` may hold both, joined by `&&` (`always() && github.event_name == 'push'`). Both parts must
  hold: the event test is applied first, so on another event the job is skipped even with
  `always()`; on the named event, `always()` runs it whatever its needs did.
- The dict may list a job before the jobs it needs; decide each job only after its needs.

You may assume the needs form no cycle and name only jobs in `jobs`. `EVENT` and `needs_of` are
given; about 15 lines remain.
