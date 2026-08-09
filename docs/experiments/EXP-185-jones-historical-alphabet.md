# EXP-185 — Repaired source-derived Jones historical alphabet

Status: preregistered; not yet executed

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

## Claim boundary

A pass qualifies only an operational historical mapping on the recovered
Jones section. Figure 6 word/arrow tests, generating-partition uniqueness,
template/conjugacy, the global TBA curve, and its manifold mechanism remain
separate gates.
