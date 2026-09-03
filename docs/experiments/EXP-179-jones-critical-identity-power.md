# EXP-179 — Powered Jones critical-identity path

Status: executed; failed unchanged identity gates

## Question

Does doubled trajectory and bootstrap support plus `0.0005` path spacing close
EXP-178's attracting-set critical-identity bracket without relaxing its branch
or identity thresholds?

## Frozen design

EXP-179 was committed and pushed before execution. It retained EXP-178's
seven oracle variants, unanimous variant requirement, critical-span gate,
normalized-step gate, runner-up margin, cross-coordinate identity requirement,
and maximum bracket width. It sampled 21 points over `a in [0.150,0.160]`,
doubled the observation horizon to `16000`, required at least 2000 crossings,
and used 100 bootstraps per variant.

Manifest:
[`../../experiments/manifests/EXP-179-jones-critical-identity-power.json`](../../experiments/manifests/EXP-179-jones-critical-identity-power.json).

## Result

The clean run at source commit
`6c68f1b75db33c617bd921c91baac6342ed5edb7` preserved a failure. The primary
`x` coordinate resolves two branches through `a=0.1525` and three branches
from `a=0.159`; its bracket width is `0.0065`, above the unchanged `0.005`
gate. Moreover, `z` is unresolved at both selected primary-coordinate bracket
endpoints, so cross-coordinate identity fails. Requiring both coordinates to
resolve at the endpoints yields the still-wider bracket `[0.152,0.1595]`.

The detailed transition is structured rather than noisy:

- both coordinates unanimously resolve two branches through `a=0.152`;
- global oracle variants disagree through most of `0.153–0.158`;
- `z` first unanimously resolves three branches at `a=0.1585`;
- `x` first unanimously resolves three branches at `a=0.159`; and
- both coordinates unanimously resolve three branches from `a=0.1595`.

At the primary x bracket, the operational identity rule again selects
higher-coordinate critical `K1`: normalized step `0.018205`, runner-up margin
`0.392034`. That assignment is not promoted because z is unresolved at the
same bracket.

## Interpretation

Doubling support resolves more of the lower two-branch interval but does not
make the global branch-count oracle well-conditioned in the shallow-extremum
transition band. Further brute-force power is therefore not the next test.
The per-variant records show that the pre-existing higher-coordinate critical
point remains localized even when variants disagree about whether the new
lower-coordinate extremum is detectable. A prospective successor may track
that persistent critical locally while keeping global branch birth as a
separate observable. It must use new trajectories and frozen local matching
rules, retain gaps where too few variants resolve, and never infer historical
symbols from target words.

Raw receipt SHA-256:
`744c218b2cf71cc92d5accb361c2172eef333e1144e56666618813d1e49e296a`.
Compact receipt:
[`receipts/EXP-179.json`](receipts/EXP-179.json).
