# EXP-114 — Independent PIM-triple saddle controls

Status: preregistered; serial launch interrupted before any line result

## Hypothesis

A strict Nusse-Yorke PIM-straddle construction, using adaptive DOP853 rather
than the sprinkler's fixed-step RK4 ensemble, recovers a two-branch saddle at
`(a,b,c)=(0.118,0.2,20)` and a three-branch saddle at
`(0.149,0.2,20)` on the declared Barrio section.

## Frozen method

The experiment reconstructs the stable period-4 cycle first. Escape time is
the adaptive flow time until eight consecutive section returns lie inside the
same scaled cycle neighborhood used by EXP-112. Five line segments span
`y=[-38,-8]` at `z=0.0090,0.0093,0.0096,0.0099,0.0102`.

Each line is sampled at 33 points. The strict interior local maximum with the
largest escape time is retained, with the lowest index as the deterministic
tie break. Refinement continues to normalized width `1e-7`. The resulting
triple is mapped for 1200 returns and re-refined whenever its endpoint bracket
expands beyond `1e-7`; the first 200 middle points are discarded. At most 256
returns are allowed for each escape-time evaluation. Censoring is not silently
accepted.

The retained middle-point pairs are pooled only after preserving the line ID.
Both `y` and `z` use the unchanged 15-variant robust branch oracle. The raw
straddle states are written to a separate hashed NPZ artifact.

## Acceptance criteria

Each case passes only if:

- the attracting control is independently classified as period 4;
- at least three of five frozen line segments produce complete straddles;
- no lifetime evaluation is censored or fails numerically;
- at least 2000 consecutive return pairs are retained per coordinate;
- all 15 oracle variants agree on the expected two/three count;
- within-PIM normalized critical-location span is at most `0.03`; and
- the combined EXP-112/PIM normalized critical-location span is at most `0.05`.

The complete experiment passes only if both controls pass. A pass is
independent local saddle corroboration, not continuation of the TBA and not a
topological-template equivalence proof.

## Execution amendment before observable output

The first serial launch saturated one CPU core for about ten minutes and was
interrupted before the script emitted any line result or wrote an artifact.
The frozen numerical method and every scientific gate remain unchanged.
Escape-time evaluations at the 33 independent points of each refinement level
now use an ordered eight-process pool; results are consumed in input order, so
the longest-lifetime/lowest-index decision remains deterministic. PIM triple
mapping itself remains serial. This amendment is committed before relaunch.

The multiprocessing launch was itself interrupted before a line result after
all eight workers spent several minutes inside one escape-time batch. Because
one censored or failed evaluation already violates the frozen zero-censor gate,
the runner now cancels still-pending candidates as soon as either terminal
condition returns. If every candidate captures, all values are collected and
the deterministic original-order PIM decision is unchanged. This is fail-fast
evaluation of the existing gate, not a new or relaxed criterion.

## Frozen execution

```sh
PYTHONPATH=python ./.venv/bin/python scripts/qualify_pim_saddle_controls.py \
  --manifest experiments/manifests/EXP-114-pim-saddle-controls.json \
  --output artifacts/EXP-114/receipt.json \
  --states-output artifacts/EXP-114/pim-straddles.npz
```
