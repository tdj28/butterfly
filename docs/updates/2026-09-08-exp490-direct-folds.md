# EXP-490: testing every original fold candidate directly

Execution in progress. The complete prospective matrix is frozen at
`892ab8f4719fbf4463bf9b4943314c9d4c8eda5e` and was matched against the live
remote before launch. No paid review, cloud compute or upload is involved.
This file will be completed with the audited result; it is not a result receipt.

## What this calculation changes

EXP-489 established two local section-grazing boundaries. Those are places
where the list of counted crossings changes, even though the underlying flow
is smooth. A slope-sign change across that boundary is not automatically a
smooth maximum or minimum of the return map.

EXP-490 therefore solves the projected-fold equations directly. It integrates
the flow plus first and second sensitivities, locates a candidate stationary
return, and then independently recounts the section events. A solution must
be the specified return, remain transverse to the section, have nonzero
curvature, and pass opposite-side, finite-difference and two-solver checks.
Newton is the root corrector; DOP853 and Radau still integrate the ODE.

The complete test retains all **26 original candidate intervals across 16
curve families**: both parameter cases, both observed regions, both history
depths and both initial directions. There are 52 solver profiles. Each has a
fixed search box and a maximum of eight Newton trajectories. Leaving that
box is unresolved, not evidence that the interval contains no fold.

Before targets, 15 focused tests and all 12 analytic controls passed. The full
suite passed 1,933 tests with one existing Linux-only skip. Both remote Python
3.12/3.13 checks passed on the exact freeze. The preflight record discloses
development failures and their corrections; no target threshold was loosened.

## Scientific boundary

The already-qualified right-hand EXP-486 fold is a comparison, not an
independent discovery. A newly qualified fold is still a feature of a finite-
return image curve, not automatically an invariant quotient or a critical
symbol. The complete source-derived Jones word/arrow list remains withheld
from the root objective. No C/D label or symbolic chain is assigned by this
experiment. Earlier failed experiments keep their original verdicts.

The original paper does not publish the full section equation and numerical
partition used to generate every word. Our chosen historical-section
implementation is a modern reconstruction, not recovered original code.
Correcting this implementation cannot, by itself, establish that Jones made
the same event-selection mistake.

## Reproduction anchors

- [Protocol](../experiments/EXP-490-direct-folds.md).
- [Preflight](../experiments/receipts/EXP-490-preflight.json).
- Public executable input: `experiments/manifests/EXP-490-candidates.json`,
  SHA-256 `f7ef9d69bad22cd0ce8ca3c112e4c4d2c420ac247c0d3187359a33cc71329fea`.
  The successor can run from this table without access to the old raw archive.
- Sole raw attempt: `artifacts/EXP-490/target-892ab8f`. The exclusive
  `artifacts/EXP-490/target-once.json` marker must not be reset or reused.
- Auditing is local and same-agent, not independent peer review.
