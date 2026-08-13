# EXP-258 — Segmented period-96 flip scan

Status: frozen — not yet executed

EXP-257 supplies nine exact primitive period-96 rows from stable birth to a
strongly unstable endpoint. EXP-258 computes four cyclic block-Floquet
products at every row and selects the uniquely larger-modulus non-neutral
eigenvalue under the same eight-orders separation rule that repaired EXP-242.

A pass requires a real `-1` bracket between the stable first row and negative
unstable terminal row, with all matching, reality, point-count, separation,
and cyclic calculations retained. It nominates an exact period-96-to-192 event
solve; it does not establish the event or a period-192 child.

Manifest:
[`../../experiments/manifests/EXP-258-jones-period96-segmented-flip-scan.json`](../../experiments/manifests/EXP-258-jones-period96-segmented-flip-scan.json).
