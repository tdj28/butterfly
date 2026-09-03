# EXP-071 — Test the predicted period-80 flip

Status: executed; failed residual gate, prediction retained

Refine the independently qualified period-80 child's `-1` event inside the
observed EXP-069 bracket. The manifest embeds, before refinement, EXP-066's
hash-identified prospective prediction `b=0.1797205086405365`.

Require bracket width `<=2e-12`, multiplier residual `<=1e-8`, real
multiplier, closure `<=1e-9`, and half-period closure `>=0.001`. Report the
signed and absolute prediction error and the new spacing ratio after the event
is located. Passing validates the event, not universality; closeness of the
prediction is evaluated quantitatively after the unchanged solve.

The clean run at `ccc19d3e0cfd152c5712af56cd76d88c67c5a5d8` failed one
numerical gate. It locates the event near `b=0.1797203688504` in an
`8.05e-13` bracket, with closure `2.79e-12` and half-period closure `0.006964`,
but the best multiplier residual `2.08e-8` exceeds the frozen `1e-8` cutoff.
Receipt SHA-256:
`d776c0f1c75878a9db8b16bef4baef9aa033f907a33979123a5cd46d5b69fc4b`.

The frozen EXP-066 prediction misses this unresolved estimate by only
`1.398e-7` in `b`. Retain EXP-071 as failed and do not yet promote the implied
spacing ratio. EXP-072 reuses only its final bracket with tighter tolerances
and a stricter residual gate.
