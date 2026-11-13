A logistics company runs Gurobi jobs in containers. Before a job starts Gurobi, it must decide
which license it will use and log that decision, without logging any secret. Write
`license_plan(environ, exists)`: `environ` is a dict of the job's environment variables, and
`exists(path)` returns whether a file is there (passed in, so the tests need no files). Return a
pair `(kind, detail)`, following these rules in order:

1. If all three of `WLSACCESSID`, `WLSSECRET` and `LICENSEID` are set (non-empty), return
   `("wls", {"WLSACCESSID": ..., "WLSSECRET": ..., "LICENSEID": <int>})`: Gurobi's `LICENSEID`
   parameter is a number.
2. If one or two of them are set, return `("error", "incomplete WLS key: <missing names> not set")`,
   naming the missing variables in the order above, joined by `", "`. Never put a value in the message.
3. If `GRB_LICENSE_FILE` is set, return `("file", <that path>)` if the file exists, otherwise
   `("error", "license file not found: <that path>")`. Gurobi does not look elsewhere when the
   variable names a missing file, so neither does this function.
4. Otherwise try Gurobi's default places on Linux, in this order: `/opt/gurobi/gurobi.lic`, then
   `<HOME>/gurobi.lic` with `HOME` from `environ` (skip it if `HOME` is not set). Return
   `("file", path)` for the first that exists.
5. If none does, return `("error", "no license")`.

No Gurobi license is needed. About twenty lines.
