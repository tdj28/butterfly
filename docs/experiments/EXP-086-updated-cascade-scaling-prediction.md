# EXP-086 — Update the cascade prediction after period 320

Status: executed; passed

Consume only the hash-bound final event receipts for the verified 5→10,
10→20, 20→40, 40→80, 80→160, and 160→320 events. Recompute all five
successive spacings and four observed spacing ratios. Use the frozen reference
`4.66920160910299` only to predict the next 320→640 event and the limiting
parameter from the last verified spacing.

Pass if event parameters and spacings decrease strictly, every finite ratio is
in `[4.0,5.2]`, and the final ratio is closer to the frozen reference than the
first. This is a prospective search contract for the next segmented
continuation, not an asymptotic universality claim.

The clean run at `63ed4ae0e4f3bb9543b474df30099ec30b3ee0bf` passed. The
successive ratios are `4.536305`, `4.594406`, `4.647627`, and `4.664603`;
their absolute errors from the frozen reference fall to `0.004599`. The
prospectively frozen 320→640 prediction is `b=0.1797124942943`, and the
finite-sequence accumulation estimate is `b=0.1797121157362`. Full receipt
SHA-256:
`8f663320835e57174b5f70dfca125662867cc9b9c87b1aa95a9a136bb0635bdb`.

EXP-087 binds this receipt and scans signed block-Floquet multipliers across
the predicted value. The prediction counts as successful only if a later
independent event solve agrees; the present arithmetic does not verify it.
