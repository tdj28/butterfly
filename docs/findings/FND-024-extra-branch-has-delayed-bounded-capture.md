# FND-024 — The transient extra branch has delayed but bounded capture

Status: prospectively rejected mechanism with qualified replacement pattern

## Finding

EXP-127 rejects the proposed faster-capture explanation for the disappearing
extra branch at `(a,b,c)=(0.148,0.2,20)`. The experiment passes every support
and numerical-quality gate, but fails its scientific gate in the opposite
direction: the extra branch has a longer restricted mean residual lifetime
than the pooled two-branch core.

## Evidence

- The three untouched evidence ensembles contain 505, 555, and 545 certain
  extra-branch assignments and more than 22,000 assigned trajectories each.
- Extra-minus-core restricted mean survival time is `+30.50`, `+30.86`, and
  `+29.98` time units. The corresponding 99% trajectory-bootstrap intervals
  are `[27.39,33.55]`, `[27.89,34.01]`, and `[27.25,32.66]`.
- Two-sided log-rank `p` values range from `1.57e-18` to `3.55e-17`. Because
  the survival curves cross, these values establish distributional separation,
  not a proportional-hazard direction.
- The matched half-step run returns `+30.90`; its change from the baseline is
  only `0.40` time units, and the extra-branch assignment fraction changes by
  `0.00042`. Every integration and frozen numerical gate passes.
- Every extra-branch trajectory survives the first 60 residual time units, but
  none survives 180. The two core branches begin capturing almost immediately,
  yet retain approximately 1--2% survival at 270.

The qualified pattern is therefore **delayed but bounded capture**, not faster
capture in mean lifetime. It directly explains the earlier conditioning split:
an extra branch can remain visible among trajectories selected through time
300 and still vanish from a population selected through time 360, while a
small core tail persists longer.

## Implication for Jones and the topology bracket

This rejects a mechanism proposed during the modern replication, not the
Jones/Barrio two-to-three transition itself. Independent PIM still selects two
branches at `a=0.148` and three at `a=0.1485` under the identical method, so the
finite invariant-set classifier bracket remains `[0.148,0.1485]`.
EXP-128 subsequently qualifies `a=0.14825` as three and narrows that bracket to
`[0.148,0.14825]`; the lifetime conclusion remains unchanged.

It does impose a sharper limit on Jones-style reinjection evidence. The
finite-time extra branch at `a=0.148` cannot be treated as a branch of the
PIM-resolved saddle or as evidence that a third invariant branch organizes a
hub. At this parameter it is a reproducible preasymptotic return-map domain
with a bounded residual-lifetime band. The genuinely three-branch saddle at
`a=0.1485`, followed under continuation, is the appropriate substrate on which
to test reinjection and neighboring-window predictions.

## Limit

The result uses the historical oriented-section `y` projection, a time-150
landmark, and the branch envelopes frozen from EXP-123. It identifies a robust
conditional lifetime pattern but does not establish its phase-space cause,
continue the TBA curve, or show that reinjection predicts any shrimp or hub.

Raw receipt SHA-256:
`3df1dd7a362e81f072dc6f1e308dbefb2a8af43c0692fb143498144dcea1679a`.
