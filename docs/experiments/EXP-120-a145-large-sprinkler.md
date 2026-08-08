# EXP-120 — Eightfold-support saddle qualification at `a=0.145`

Status: executed; failed full coordinate gate after closing support

## Diagnosis under test

EXP-117 left `a=0.145` unresolved because rapid capture reduced the seven
ensembles to 33--231 final survivors and 284--1872 pairs. Every one of the 72
resolved oracle variants returned two branches; none returned three. The
missing variants were concentrated at the finest bins and failed support,
coverage, or bootstrap stability.

## Frozen successor

Repeat the complete EXP-112 physics, conditioning, and acceptance thresholds
at `a=0.145,b=0.2,c=20`, changing only support and independent Sobol scrambles:

- baseline, half-step, and later-conditioning ensembles use `2^16=65536`
  section seeds with scramble 120;
- independent scrambles 121 and 122 also use `2^16` seeds;
- the nested ladder is `2^15,2^16,2^17` seeds;
- all 15 oracle variants, both `y` and `z`, must return two branches with full
  variant consensus and the unchanged critical-drift gates;
- the stable period-4 cycle, survivor-fraction convergence, minimum 100 final
  survivors, minimum 1000 pairs, and five-trajectory DOP853/Hermite audit
  remain unchanged.

This is roughly eight times EXP-117's support at every corresponding run. No
resolution group is relaxed: unlike `a=0.150`, no adequate-resolution variant
has ever returned three here.

## Claim boundary

Passing closes the sampled `a=0.145` regular-window hole as two-branch and
narrows the resolved topology-change bracket to `[0.145,0.149]`. It does not
locate the crossing inside that interval or prove a continuous global TBA.

Immutable manifest:
`experiments/manifests/EXP-120-a145-large-sprinkler.json`.

## Result

The clean run at `89caeb3` completed in `358.51 s` and failed. Support now
passes comfortably: the minimum final-survivor and pair counts are 323 and
2726, all survivor curves converge within `0.001282`, and no integration or
short-horizon audit fails.

All 105 `y` oracle cells resolve as two branches. In `z`, 84 cells resolve as
two and the remaining 21--the three 80-bin variants in every run--fail only
fixed-width domain coverage at `0.675` or `0.6875` versus `0.7`. Every censored
variant has one nominal critical point in the resolved interval; none returns
three or fails graph-likeness. EXP-120 remains failed and does not narrow the
formal bracket. Raw receipt SHA-256:
`e00d40ab509b1f3cffeb1c20497686a451aa4300986e6d171a9e83226083e3a4`.
