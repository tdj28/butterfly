# EXP-049 — One-traversal continuation identity audit

Status: executed; failed

Count accepted legacy-section intersections during exactly one stored closed
traversal for all 46 EXP-023 rows. This avoids asymptotic drift from unstable
cycles. Require a five-crossing first row, six-crossing last row, at least five
of each, and successful integration throughout. The result maps numerical
family identity; any count transition is a corrector/provenance event, not a
dynamical period change.

The clean run at `92e9f0d0a8653f1ed6b56e52385aadf2359281f6` failed
the expected ordering. Counts are 40 six-crossing rows, 5 five-crossing rows,
and 1 four-crossing row. The first row at `b=0.1275` is already six-crossing;
the only period-5 segment is `b=0.175..0.195`, followed by period 4 at `b=0.2`
and period 6 from `b=0.205`. Thus EXP-023's named period-5 trace is not one
continued family. Receipt SHA-256:
`035372b085347bd1b4909f8dc6958351fd4f69d7518f5a4a1edaf109d86350f2`.

Reject EXP-023's period-5-family continuation claim and all downstream claims
that depend on that provenance. Retain the local period-3/6 surface because it
was independently requalified by EXP-039 through EXP-047. Rebuild global
continuation with recurrence identity enforced at every corrector step.
