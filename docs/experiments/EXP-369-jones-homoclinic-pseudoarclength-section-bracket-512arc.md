# EXP-369 — 512-arc homoclinic section bracket

Status: failed; wrong-direction root

EXP-368 qualifies a point only `1.74979e-5` above exact `a=0.1798` but uses
`99.993%` of the 256-arc root gate. EXP-369 prospectively subdivides exact
EXP-367 and EXP-368 roots to 512 arcs and reduces the desired predictor to
`Delta c=0.00015`.

Segmentation and predictor size are the only changes. Both free parameters,
the common gauge, solver/manifold settings, sensitivities, bounds,
40-evaluation budget, and both `1e-8` gates remain fixed. Passing below
`a=0.1798` forms a qualified branch bracket; it does not itself solve the
exact section or establish uniqueness or computer-assisted existence.

Manifest:
[`../../experiments/manifests/EXP-369-jones-homoclinic-pseudoarclength-section-bracket-512arc.json`](../../experiments/manifests/EXP-369-jones-homoclinic-pseudoarclength-section-bracket-512arc.json).

EXP-369 finds a numerically strong 512-arc root but fails the frozen direction
gate. The corrected point is
`(a,c)=(0.17984410461079062,10.316999762096582)`, backward in `c` from
EXP-368. Maximum matching defect is `6.47408941890661e-9`, matching norm is
`2.356183206514301e-8`, and arclength residual is
`-5.014034326622507e-12`; normal `gtol` termination occurs in ten evaluations.
Only `forward_c_direction` is false.

This is not evidence that the homoclinic branch ends. It shows that the
high-dimensional secant hyperplane, including nuisance angle/node motion,
admits a corrected root on the wrong local side. The successor makes the
existing forward-direction acceptance requirement an explicit lower bound
during optimization; residual gates remain unchanged.

Raw receipt: `artifacts/EXP-369/receipt.json`, 78,804 bytes, SHA-256
`c41f34f5586f871f6d18b44394c1a777e73264bee8a947ef9182faba678eff69`.
