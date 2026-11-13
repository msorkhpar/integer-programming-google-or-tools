A warehouse-planning service forwards solver messages to a shared log. Some messages name the
machine's user and host, or carry an e-mail address or an access key, and none of that may reach
the log. Write `mask_line(line)`, which returns the line with:

| In the line | Replaced by |
| --- | --- |
| `user ` followed by any characters up to the next `,` or `)` (possibly none) | `user <user>` |
| `host ` followed by any characters up to the next `,` or `)` (possibly none) | `host <host>` |
| an e-mail address: name characters (letters, digits, `.`, `_`, `+`, `-`), `@`, then a domain with at least one dot | `<email>` |
| a key shaped like a UUID: 8, 4, 4, 4 and 12 hexadecimal digits joined by `-` | `<key>` |

Everything else stays as it was, so the message still says what went wrong. "user" and "host" count
only as whole words (`hostid` is not `host`). Python's `re` module does all of it. No Gurobi license
is needed. About ten lines.
