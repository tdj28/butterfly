# EXP-410 — Conditioned post-turn half-step

Status: executed; passed every prospective gate

EXP-409 finds a clean outgoing root but misses the prospective conditioning
floor by `7.76e-11`. EXP-410 retains the exact passed EXP-407/408 sources and
all gates while halving normalized arclength to `0.009197361472878517`.

A pass adds an eighteenth qualified point and establishes a safe conditioned
step into this harder segment. It does not establish global nonintersection,
uniqueness, proof, or topology.

## Result

EXP-410 passes every gate in two evaluations:

```text
(a, c) = (0.17981770507985761, 10.317080894073841)
Delta a = +1.0192423230415137e-7
Delta c = -2.709285293889252e-7
signed arclength = 0.009197361472818471
maximum block defect = 3.2004812199537124e-9
minimum singular value = 1.2492595092156195e-9
node-boundary margin = 0.9813415061342994
```

The half-step restores comfortable conditioning without weakening a threshold
and adds the eighteenth qualified root.  The branch continues toward larger
`a`, leaving a gap of `1.77051e-5` above Jones's historical fixed-`a` section.
This strengthens the resolved first-local-minimum result but does not rule out
a later turn or another branch.

Raw receipt: `artifacts/EXP-410/receipt.json`, 78,514 bytes,
SHA-256 `d0574608a922c599f44483885e9636ca646754d67bf191f9a7834674e1b481b3`.
Compact receipt: [`receipts/EXP-410.json`](receipts/EXP-410.json).

Manifest:
[`../../experiments/manifests/EXP-410-jones-homoclinic-conditioned-halfstep.json`](../../experiments/manifests/EXP-410-jones-homoclinic-conditioned-halfstep.json).
