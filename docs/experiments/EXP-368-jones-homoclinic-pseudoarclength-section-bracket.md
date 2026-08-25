# EXP-368 — Homoclinic pseudo-arclength section bracket

Status: passed; remains above section

EXP-367 passes only `8.47855e-5` above exact `a=0.1798` with 31% matching-gate
headroom. EXP-368 therefore prospectively returns the 256-arc predictor to
`Delta c=0.0005` using exact EXP-366 and EXP-367 roots. All solver, manifold,
gauge, sensitivity, bound, budget, and acceptance settings remain unchanged.

A pass below `a=0.1798` forms a qualified pseudo-arclength bracket with
EXP-367. It does not itself solve the exact section, establish uniqueness, or
supply computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-368-jones-homoclinic-pseudoarclength-section-bracket.json`](../../experiments/manifests/EXP-368-jones-homoclinic-pseudoarclength-section-bracket.json).

EXP-368 passes all ten gates with normal `gtol` termination in eight
evaluations, but the corrector does not cross the section. It lands at
`(a,c)=(0.1798174978856614,10.317081488741884)`, only `1.74979e-5` above exact
`a=0.1798`. Maximum matching defect is `9.999341431358164e-9`, matching norm
is `2.691424560648336e-8`, and arclength residual is
`-7.702153151378788e-12`. Node margin is `0.62725`.

The latest slope is `-0.3255565529`, projecting the section at
`c=10.3171352363`, only `5.37476e-5` farther in `c`. Because this point uses
`99.993%` of the 256-arc root gate, the next crossing attempt prospectively
doubles segmentation and reduces the requested step; no gate is relaxed.

Raw receipt: `artifacts/EXP-368/receipt.json`, 41,717 bytes, SHA-256
`03daaaa5c08327bb8b9dcf21a68afd5613b4e1f4667481f7eb97be368ceb9481`.
