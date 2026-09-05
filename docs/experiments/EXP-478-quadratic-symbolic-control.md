# EXP-478 — Independent finite quadratic-map symbolic control

Status: completed locally after public source/protocol freeze; all six scalar
periods and the separate conditional source comparison pass.

## Question and separation from Jones's flow claim

Independently enumerate every primitive superstable cycle of
`f_mu(x) = 1 - mu*x*x`, for `mu in [0,2]` and periods 2–7. The critical point
is zero. Record its time-ordered itinerary as `C` at zero, `1` at positive
states, and `0` at negative states. Neither the historical word list nor
its arrows enter root finding, sign encoding, root selection, or ordering.

This is a finite algebraic control, **not an independent replication of
Jones's Rössler chains**. A quadratic-map critical point is not a second
critical point of a bimodal flow projection. No conjugacy, quotient,
generating partition, Rössler parameter center, or connecting path follows
from this computation.

## Frozen construction

The [machine manifest](../../experiments/manifests/EXP-478-quadratic-symbolic-control.json)
fixes the domain, periods, interval widths, refinement limits, and work caps.
The operation cap is 200 million, selected before target execution to allow
repeated evaluation of degree-63 Sturm chains during 80-bit isolation;
the separate five-minute wall and coefficient-size caps remain in force.
The [runner](../../scripts/verify_quadratic_symbolic_control.py) constructs
the integer polynomials `P_0=0`, `P_(n+1)=1-mu*P_n^2`. Exact polynomial GCDs
remove recurrence roots of proper-divisor periods. Sign-preserving Sturm
sequences isolate all remaining real roots on the closed parameter interval;
rational interval iteration must certify every intermediate state's nonzero
sign. An unresolved sign, repeated root, failed arithmetic check, or work-cap
exhaustion is a failed/incomplete control, never permission to drop that root.

The only pre-freeze scientific fixture is the elementary period-2 cycle at
`mu=1`, with word `C1`. Other pre-freeze tests use unrelated polynomials.
There is no period-3–7 pilot or target-word tuning. The program requires clean
committed source, records its commit, manifest and script hashes, and writes
an exclusive receipt. Verify the commit is public before the first full run.

## Separate, predeclared comparison

After enumeration, compare **all** resulting words with the already known
[Figure 6 transcription](../../experiments/source-transcriptions/jones2012-figures-2-and-6.json),
SHA-256 `6a5aba797473d40db9197d7a2ebe51195193f888613800584f406742376581da`.
This comparison is deliberately separate from enumeration:

- For periods at least 3, the proposed notational dictionary is `C1s -> CDs`.
  Compare set membership and within-period order by increasing `mu` with the
  source's drawn column order; report any mismatch, missing word, or extra word.
  The declared direction is increasing `mu` versus the original Figure 6's
  **top-to-bottom** order, not the JSON node-array order. The separate
  [comparison script](../../scripts/compare_quadratic_source_words.py) freezes
  that source-only geometric transcription before enumeration.
- For period 2, retain native `C1`. Do not invent a `CD` source node.
- Source nodes `C2` and `C21` belong to the third branch and are outside this
  unimodal model; report their exclusion explicitly.
- Do not reverse time, rotate away from `C`, reorder roots to match the
  picture, search dictionaries, or treat a set match as an arrow test.

The dictionary is a **conditional comparison convention**, not a proved
coordinate transformation or a demonstration that the first positive visit
becomes a second critical visit. The source-specific known word counts are
prior context, not an outcome discovered by the enumerator. A match would
check finite combinatorial consistency under that convention; it would leave
every Rössler node and parameter-plane arrow unverified.

## Execution and evidence

```sh
.venv/bin/python scripts/verify_quadratic_symbolic_control.py \
  --manifest experiments/manifests/EXP-478-quadratic-symbolic-control.json \
  --output artifacts/EXP-478/quadratic-control.json
```

This uses only the existing Python standard library and no paid compute.
Preserve failed receipts. Publish the exact certificates and a separately
derived comparison receipt before adding any result to the manuscript.
These certificates assume the implementation and Python exact arithmetic are
correct; they are not proof-assistant-checked.

## Result and interpretation

The full run used the clean, detached published commit
`f4b2ea13c60395713911240b0fbf0ce469850cc4`; the before/after source records
are identical. It completed in 14.12 seconds on the local CPU, with
13,755,598 counted exact-arithmetic operations and no paid compute. For
periods 2 through 7, respectively, complete closed-domain isolation returned
`1, 1, 2, 3, 5, 9` primitive critical cycles: **21 total**. Every retained
root has an exact recurrence-factor certificate, a disjoint rational
enclosure (or exact rational value), and strictly nonzero certified signs
for all intervening iterates. No period, root, or unresolved sign was dropped.

The separately run, predeclared dictionary gives exact within-period word
multiset and order matches for all **21 comparable source nodes**. It retains
all 23 historical nodes in its output, explicitly marking `C2` and `C21` as
outside this unimodal model. There are no missing comparable words, extra
scalar words, duplicate mapped words, or order mismatches. Increasing `mu`
matches the original Figure 6 top-to-bottom order without reversing time,
reordering roots, or selecting another dictionary after enumeration.

Here, **independent** means that the polynomial construction, root isolation,
and sign encoding do not consume Jones's word list. The historical list was
already known when this scalar family and conditional comparison were
specified; this was not a blinded test against unknown targets. The result
establishes finite combinatorial consistency with a fully specified scalar
model, not that a positive scalar iterate becomes a second critical visit in
a Rössler return map. It verifies no Rössler node, center, branch transport,
or connecting arrow. EXP-477 and its independently qualified successors are
still needed for the flow-level claim.

The complete, byte-preserved public evidence is:

- [Exact scalar receipt](receipts/EXP-478-quadratic-control.json), SHA-256
  `6d46529e6ae6b53f6796848855f1c01d6cf936399da6455fe6ef12e6140b925e`.
- [Separate source comparison](receipts/EXP-478-source-comparison.json), SHA-256
  `90031254a6f0ede05f77ff6d5cc2f617046b159b118dcc9fcba1889d2ecf31ae`.
- Frozen manifest SHA-256
  `afc851204f68b3e248bb9eb980332e42252e46a4991ac308340ce80ce5b75781`;
  the exact receipt additionally records the enumerator, dependency-lock,
  source-commit and source-tree hashes.

The [manuscript table](../../paper/tables/quadratic-symbolic-control.tex) and
its [provenance](../../paper/tables/quadratic-symbolic-control.provenance.json)
are derived from these public receipts and the frozen source transcription.
The [complete 21-row word and root export](../../paper/tables/quadratic-symbolic-words.csv)
lists every native word, its proposed source word, and both exact rational
parameter bounds in increasing-`mu` order within each period. Its zero-based
root index restarts each period. `mu_midpoint_decimal_approx` is only the
enclosure midpoint rounded to 16 decimal places for display; it can lie
outside the much narrower certified interval and must not replace the exact
bounds. The CSV's match field records conditional source membership, not
Rössler-orbit verification. Its hash and all formatting conventions are
included in the same provenance file.
The renderer replays the comparison and derives every displayed count; it
does not rerun root enumeration or independently replay the Sturm proof.
Verify the deterministic table, CSV and provenance without changing them:

```sh
.venv/bin/python scripts/render_quadratic_control_table.py --verify
.venv/bin/python -m pytest -q tests/test_quadratic_control_table.py
```
