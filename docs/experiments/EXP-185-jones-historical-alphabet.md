# EXP-185 — Repaired source-derived Jones historical alphabet

Status: executed; passed

## Administrative change only

EXP-184 stopped before integration because its evidence validator looked only
for top-level `passed`; the hashed EXP-183 compact receipt stores the pass at
`gates.passed`. EXP-185 changes only that receipt-field selector and the
experiment identifier. The source semantics, parent hashes, two solver
profiles and initial states, trajectories, sections, segment boundaries,
frozen x/z partitions, historical mapping, and every scientific acceptance
threshold are byte-for-byte identical in value to EXP-184.

The repaired validator has a unit test for nested receipt fields. The same
target-word-blind mapping remains frozen:

- `K0 -> D`, `K1 -> C`;
- `B0 -> 2`, `B1 -> 1`, `B2 -> 0`.

Manifest:
[`../../experiments/manifests/EXP-185-jones-historical-alphabet.json`](../../experiments/manifests/EXP-185-jones-historical-alphabet.json).

## Result

The clean run at source commit
`ecd64f41f2c7d0cb0604fd797f1691d18104524e` passes every gate in `231.64`
seconds. DOP853 and Radau collect 2,434 and 2,436 crossings. Across all eight
solver/segment/coordinate rows, 928--956 of 1,000 pairs remain fully resolved,
all three target intervals exceed the 100-point support gate, and the physical
distance order is always `B2, B1, B0` from nearest to farthest.

The smallest normalized inner-median gap is `0.335762`, above the frozen `0.2`
gate. The strict closest-branch distance margin ranges from `0.351409` to
`0.459174`; thus even the farthest `B2` return is closer to the small
equilibrium than the nearest return from either alternative interval. Each row
contains 96--112 `B0 -> B2` transitions, while the observed `B0 -> B0`
fraction is zero throughout. All four solver/segment x/z pair comparisons
agree exactly on every jointly resolved source and target label (910--932
pairs each).

Therefore the source-derived operational mapping passes:

- `K0 -> D`, `K1 -> C`;
- `B0 -> 2`, `B1 -> 1`, `B2 -> 0`.

Raw receipt SHA-256:
`ce6439ba9b196c4ca4d535c825969882e48d5f6852c2d8e9dbd39fa75783c877`.
Compact receipt:
[`receipts/EXP-185.json`](receipts/EXP-185.json).

## Claim boundary

The pass qualifies only an operational historical mapping on the recovered
Jones section. Figure 6 word/arrow tests, generating-partition uniqueness,
template/conjugacy, the global TBA curve, and its manifold mechanism remain
separate gates.
