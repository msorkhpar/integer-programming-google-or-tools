A logistics platform logs every solve that MathOpt refuses, and its on-call engineers want one line
per refusal: the status code's name and the solver's message. In OR-Tools 9.15 a refusal reaches you
as `AttributeError: 'StatusNotOk' object has no attribute 'canonical_code'`, and the real error is on
the exception's `__context__`: an object with an integer `code` and a `message`. A later OR-Tools
that fixes the bug raises MathOpt's own exception instead, whose message ends with
` (was C++ INVALID_ARGUMENT)` or another code's name.

Write `refusal(error)` in `refusal.py`, returning `(code_name, message)`:

- When `error.__context__` has a `code` and a `message`, return the code's name from `CODE_NAMES`
  (or `"UNKNOWN"` for a code not in it) and that message as it is.
- Otherwise, when the error's text ends with ` (was C++ NAME)`, return `NAME` and the text before
  that suffix.
- Otherwise return `"UNKNOWN"` and the error's text, `str(error)`.

`CODE_NAMES` is given: it maps the absl status codes MathOpt uses to their names.
