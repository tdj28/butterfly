# EXP-356 — Second crossing correction

Status: failed; monotone correction remains above the gate

EXP-355 lowers the fixed-`c` maximum defect to `8.30202e-6`, leaves nine
blocks above the `1e-8` gate, and moves to `a=0.1798386480583239`. Its
optimizer remains actively descending and the nodes are interior.

EXP-356 binds every exact node and repeats the same-`c` correction with the
same physics, tolerances, 128 arcs, node guardrail, 40-evaluation budget, and
scientific threshold. Passing qualifies the curve point; exact fixed `a` is
still a separate successor.

Manifest:
[`../../experiments/manifests/EXP-356-jones-homoclinic-crossing-correction-2.json`](../../experiments/manifests/EXP-356-jones-homoclinic-crossing-correction-2.json).

The run is preserved as failed at maximum defect `4.10058e-6`. It moves to
`a=0.17981905799260353`, retains `0.93883` normalized node margin, and still
has optimizer optimality `4.44e-7`. The exact-node correction remains
monotone but has not reached the scientific gate.

Raw receipt: `artifacts/EXP-356/receipt.json`, 31,855 bytes, SHA-256
`9c7be8271d4f672604c033af37aa1c56138873fb6958e41d98925b0b54a39130`.
