The vegetation crew-roster optimizer (a CP-SAT model of section 4) is moving into a container, and
operations will start it as a Batch job with its settings in environment variables. Last season a
roster job ran with a mistyped season for six hours before anyone noticed, and once with an access key
pasted into its environment.

In `roster_settings.py`, write `read_settings(env)`. It returns `(settings, [])` when the
environment is usable, and `(None, problems)` otherwise, with **every** problem found, not only the
first. The variables:

| Variable | Rule | Default |
| --- | --- | --- |
| `ROSTER_BUCKET` | required, non-empty | none |
| `SEASON` | required; a whole number from 2025 to 2040 | none |
| `CREWS` | a whole number from 1 to 50 | `4` |
| `DRY_RUN` | `true` or `false`, in any letter case | `false` |

`settings` is `{"bucket": str, "season": int, "crews": int, "dry_run": bool}`. In addition, any
variable whose name contains `SECRET`, `PASSWORD` or `ACCESS_KEY` is a problem: credentials come from
the job role, never from the environment.

The problem texts, exactly: `ROSTER_BUCKET is not set`, `SEASON is not set`, `NAME='text' is not a
whole number`, `NAME value is outside low-high` (for example `CREWS 0 is outside 1-50`),
`DRY_RUN='text' is not true or false` (with the text as given), and `NAME must not be set: use the job
role`. A whole number is what `int()` accepts: `"4.5"` is not one. The default applies only when a
variable is absent: `CREWS` set to the empty text is present, and `int("")` refuses it, so it gives
`CREWS='' is not a whole number`. (For the two required variables, empty counts as not set.) The helper `whole` is declared for
you; about 25 lines remain.
