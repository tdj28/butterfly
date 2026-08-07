# EXP-056 — Extend the true period-10 child beyond the section grazing

Status: preregistered after EXP-055; pending clean execution

Continue the verified period-10 child from the farther EXP-052 endpoint using
pseudo-arclength shooting. Do not use historical section-intersection count as
an identity gate: EXP-055 proves that count can change at a smooth grazing and
EXP-054 shows it can also be numerically undercounted. Instead require full
closure and a half-period closure bounded away from zero, which excludes a
double-covered period-5 parent.

Request up to 70 adaptive steps over `b in [0.12,0.184]`. Pass with at least 40
points spanning at least `0.02` in `b`, closure `<=1e-8`, and half-period
closure `>=0.1`. Record stability throughout and prospectively report real
multiplier crossings of `-1` or `+1`; any candidates require separate coupled
refinement.
