# EXP-086 — Update the cascade prediction after period 320

Status: preregistered after EXP-085; pending clean execution

Consume only the hash-bound final event receipts for the verified 5→10,
10→20, 20→40, 40→80, 80→160, and 160→320 events. Recompute all five
successive spacings and four observed spacing ratios. Use the frozen reference
`4.66920160910299` only to predict the next 320→640 event and the limiting
parameter from the last verified spacing.

Pass if event parameters and spacings decrease strictly, every finite ratio is
in `[4.0,5.2]`, and the final ratio is closer to the frozen reference than the
first. This is a prospective search contract for the next segmented
continuation, not an asymptotic universality claim.
