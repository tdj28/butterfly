# EXP-056 — Extend the true period-10 child beyond the section grazing

Status: executed; failed identity gate, diagnostic branch retained

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

The clean run at `1a567b459972dd25609aa153b78ae2ca1901006d` produced
72 accurately closed shooting solutions over `b=0.144696..0.183455`, but
failed because one corrected point has half-period closure `8.50e-12`, below
the frozen `0.1` identity gate. Receipt SHA-256:
`b76811777617c10efbd25ae77713ff613ae682ec534d074f9d9d7050a82935eb`.

The failure is localized rather than a gradual identity collapse. Rows 0–19
remain distinct period-doubled flow orbits with half-period closure
`0.209..1.230`; row 20 jumps to a double-covered parent; row 21 returns to the
distinct child sheet. The contaminated trace is not accepted as one branch and
its later unit-multiplier candidates are quarantined. Before contamination,
the verified child multiplier crosses `-1` inside the independently available
EXP-052 bracket `b=[0.180320828520,0.180788459850]`. EXP-057 refines that first
candidate using closure and half-period identity rather than section count.
