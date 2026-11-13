A team runs FICO Xpress from Python (`pip install xpress`) inside a container. The package's own
page says how it finds a license: with no setting, it recognizes the free community license by
itself; for a full license, you put the `xpauth.xpr` file in a folder and set the environment
variable `XPRESS` to that **folder's** path, not the file's. The team wants its service to log, at
start-up, which license it will get, so that a forgotten mount shows up in the first line of the log
instead of as a size-limit error hours later.

Write `xpress_license(env, files)` in `xproute.py`. `env` is the container's environment, and
`files` the set of file paths present in the container. Return:

- `"community license"` when `XPRESS` is missing or empty;
- `"XPRESS names the file; set it to the folder that holds xpauth.xpr"` when its value ends with
  `xpauth.xpr`;
- `"license file <path>"` when `<folder>/xpauth.xpr` is in `files`, with the path joined by
  `posixpath.join`, so a trailing slash on the folder does no harm;
- `"no xpauth.xpr in <folder>"` otherwise, with the folder as given.

About eight lines.
