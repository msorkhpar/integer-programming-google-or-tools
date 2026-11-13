A school district (invented for this practice) approves its yearly building-repair program with
the workflow in `TABLE` (in `approval.py`): a draft is edited and submitted, the board approves or
rejects a submission (a rejected program goes back to Draft), and an approved program can only be
archived. An auditor wants three answers from the table itself, never from a second copy of the
rules:

- `allowed(state)`: the sorted list of actions the state accepts.
- `walk(state, actions)`: apply the actions in order and return `(final state, None)`; if an action
  is refused, stop there and return `(the state it was refused in, that action)`.
- `reachable(state)`: the sorted list of every state that some sequence of allowed actions can lead
  to from `state`, `state` itself included. The board's question is whether an approved program can
  ever get back to Draft.

About fifteen lines.
