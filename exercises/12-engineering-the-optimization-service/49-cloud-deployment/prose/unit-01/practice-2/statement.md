The roster team builds its own images, and the platform team wants a check in CI that refuses a
Dockerfile breaking the four rules every image on the cluster must follow. Write it.

In `dockerfile_review.py`, write `review(dockerfile)`. It takes a Dockerfile's text and returns the
sorted list of findings, each at most once:

| Finding | When |
| --- | --- |
| `base-not-pinned` | a `FROM` image has no tag, or the tag `latest`, and no `@sha256:` digest. A `FROM` that names an earlier stage (`FROM build`, after `FROM ... AS build`) is not a base image. The colon of a registry port (`host:5000/python`) is not a tag. `FROM scratch` (in any case) names Docker's reserved empty image, which has no tag to pin, so it is never flagged. |
| `runs-as-root` | the **final** stage has no `USER`, or its last `USER` is `root` or `0` (a `user:group` form counts by its user part). Every stage starts as root: a `USER` in an earlier stage does not carry over. |
| `secret-in-env` | an `ENV` or `ARG` sets a variable whose name, in upper case, contains `KEY`, `SECRET`, `TOKEN` or `PASSWORD`. An `ENV` line may set several `NAME=value` pairs. |
| `shell-form-cmd` | a `CMD` or `ENTRYPOINT` is not in exec form (does not start with `[`). |

Instruction words may be written in any case. `instructions(dockerfile)` is given: it drops comments
and blank lines and returns `(WORD, rest)` pairs with the word in upper case. You may assume one
instruction per line. About 25 lines remain.
