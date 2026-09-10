# EXP-509: preserve the failure and recover its scientific evidence

## Audited result

The complete saved predictor **passes raw replay**: 196 original IVPs,
172 inherited archive products plus 24 separately retained guards. Replay
took 186.45 seconds and performed zero new integrations. All original bytes
still authenticate afterward. EXP-508 remains a failed run; the reconstructed
decision is **predictor-unqualified**, with no corrector and no accepted step.

The failure is scientifically informative. All four depth-8 Newton solves
converged to their equation tolerances, but the input-image tangent gain
collapsed to between 1.40e-12 and 2.39e-11, far below the unchanged 1e-4
minimum. Both neighboring scalar slopes are positive (about 0.28447), not
opposite signs. These are invalid input-curve representations, not qualified
folds. At the previous EXP-507 point their gains were about 8.25–11.67.
Convergence of the determinant equations alone is not enough to track the
desired fold branch. The existing scientific gate correctly rejected them;
the new reporting controller then mishandled that legitimate rejection.

| Representation | Both solvers | Outcome |
| --- | --- | --- |
| Depth 4, direction 0 | All numerical gates pass | Fold distance 0.000139565, above 0.0001 |
| Depth 4, direction 1 | All numerical gates pass | Fold distance 0.000139565, above 0.0001 |
| Depth 8, direction 0 | Newton converges; input gain fails | No qualified fold/contact distance |
| Depth 8, direction 1 | Newton converges; input gain fails | No qualified fold/contact distance |

The primitive six-event historical/eight-event Barrio cycle qualifies in both
solvers and both windows. Original, starting and adjacent cycle identity pass.
All eight boundary representations qualify at both Decimal precisions, and
all 384 boundary/cycle comparisons replay. The target boundary distance is
0.0111383074 versus 0.0119426496 at EXP-507: a 6.735% diagnostic reduction,
but still 111.38 times the unchanged contact radius. Only 128 of the required
256 joint vectors exist. Neither the boundary improvement nor the two good
short-history folds can substitute for the missing representations.

## Reproduction and limits

Replay source: `808054ffb8ecda4c216faa655c734f57ef691a23`, preserved on
`codex/exp509-local-replay` and live-verified before replay. The public
[receipt](../experiments/receipts/EXP-509-failed-predictor-replay-result.json)
is byte-identical to artifacts/EXP-509/replay-808054f/result.json, SHA-256
`6857228fe1c4b09692982e5d6481595398552c2e055b6f1620b22c499bcff4e5`.
It includes all four folds, eight boundaries, the original failure/inventory
and the 26-parent ledger, not only the successful subset. The original
280-file directory occupies 1,285,292,122 bytes including failure.json.

```
PYTHONPATH=.:python .venv/bin/python scripts/verify_exp509_public_replay.py \
  --result docs/experiments/receipts/EXP-509-failed-predictor-replay-result.json \
  --expected-sha256 6857228fe1c4b09692982e5d6481595398552c2e055b6f1620b22c499bcff4e5
```

Public compact replay passes, with 15 passing receipt/tamper tests. It does
not reacquire or independently audit the full local raw archive. The raw audit
uses shared numerical code; it is not independent-team replication. The old
EXP-508 public-verifier draft was never used or released and is retained at
artifacts/EXP-508/unreleased-public-verifier-01.py. No paid review was called.

Final local release suite: **2,555 passed, one Linux-only skip**, in 198.01
seconds (artifacts/EXP-509/release-suite-01.xml). Citation/figure availability
and the receipt-generated symbolic table also pass. This counts software
regressions, not 2,555 new scientific verifications.

## Next scientific step

Test a bounded four-substep fold-only continuation from qualified EXP-507 to
the same EXP-508 predictor parameters. Carry all four curve representations
and both solvers; warm-start only from fully qualified predecessors. Require
cross-history full-state agreement as well as the existing input-gain, opposite
slope, event and solver checks. Stop and retain every failure. This tests
whether a smaller parameter step preserves the desired branch, instead of
loosening gain thresholds or accepting a collapsed-curve root. Reuse the
audited cycle/boundary only as fixed endpoint comparisons, not as evidence for
new intermediate cycles. A full-state fold correction remains a separate
requirement even if that branch transport succeeds. No Jones chain is yet
verified or debunked.

## Historical pre-replay checkpoint

EXP-508 completed the predictor's raw production (196 IVPs), then crashed in
the new controller when an unqualified fold left `contact.envelope` null.
The failure is retained: there is no original summary, no comparison record
and no corrector run. All 279 inventory entries authenticate. The original
failure, point, source and consumed marker are unchanged.

The [EXP-509 forensic protocol](../experiments/EXP-509-failed-predictor-replay.md)
adds a null-safe qualification path and replays the complete saved point from
raw data. It licenses no new integrations. Missing/malformed contact evidence
cannot authorize a corrector, even if a caller's point flag says qualified.
The repaired controller uses a copied environment, so no original function or
frozen source is patched. A new receipt will distinguish the original runtime
failure from the reconstructed scientific rejection.

Before raw replay, 55 initial focused controls passed in 4.34 seconds. The
final 57-control set passes in 6.92 seconds, including 16 new regressions,
a clean-interpreter successor startup, hash-before-read rejection and the old
model/quota tests. The full suite passed 2,538 tests with one Linux-only skip
in 183.22 seconds; the last two added tests pass in the focused run. The
original isolated copied-source startup also passes. Receipts are retained in
artifacts/EXP-509/preflight-02.xml, pretarget-suite-01.xml and
original-startup-01.json. Citation/figure and symbolic-table checks pass.
Source freeze and raw replay follow this checkpoint.
This is a local repair and audit: no paid review, new GPU worker,
remote execution or raw upload is needed. Jones's flow chains remain
unverified, not debunked.

The raw replay and diagnosis above supersede this checkpoint. Do not restart
EXP-508 or reuse the EXP-509 replay marker.
