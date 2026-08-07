# EXP-054 — Refine the stable child’s legacy gate transition

Status: preregistered after EXP-053; pending clean execution

On the stable period-10 flow-orbit branch, refine where the eleventh raw
`y=y_eq` intersection crosses the historical gate boundary `x=x_eq`. Bisect
the ranked gate margin inside the frozen 11/10-count bracket. Require bracket
width `<=1e-9`, gate margin `<=1e-7`, closure `<=1e-9`, stable Floquet modulus,
and endpoint counts exactly 11 and 10.

Passing identifies a section/gate topology transition on a still-stable smooth
periodic orbit. It is directly relevant to Jones-style reinjection and return-
map branch changes, but does not by itself identify the global TBA curve.
