# EXP-054 — Refine the stable child’s legacy gate transition

Status: executed; failed as specified, diagnostic retained

On the stable period-10 flow-orbit branch, refine where the eleventh raw
`y=y_eq` intersection crosses the historical gate boundary `x=x_eq`. Bisect
the ranked gate margin inside the frozen 11/10-count bracket. Require bracket
width `<=1e-9`, gate margin `<=1e-7`, closure `<=1e-9`, stable Floquet modulus,
and endpoint counts exactly 11 and 10.

Passing identifies a section/gate topology transition on a still-stable smooth
periodic orbit. It is directly relevant to Jones-style reinjection and return-
map branch changes, but does not by itself identify the global TBA curve.

The clean run at `20da321430b0c6f21c682aaa2913010d857fafd1`
failed. It narrowed a *numerical event-detection boundary* to
`b=0.18174786983513413`, but the ranked gate margin jumped from `+0.04889`
to `-3.51844` rather than converging to zero. Receipt SHA-256:
`e33566d0da5ad6774a0eaac291461f46d4c9b46b0ee87f6dec0deade357ed1db`.

Post-run diagnosis found two nearby section intersections that can lie inside
one integration step. At the right endpoint, `max_step=0.01` reports 20 raw /10
accepted intersections, whereas `max_step=0.005` reports 22 raw / 11 accepted.
Thus this experiment's estimate is not a dynamical transition and must not be
used as one. The original broad bracket does contain a real section grazing:
the intervening local maximum of `y-y_eq` changes sign while the orbit remains
stable. EXP-055 replaces discrete event count with that continuous extremum
condition.
