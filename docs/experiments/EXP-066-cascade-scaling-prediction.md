# EXP-066 — Cascade spacing analysis and prospective prediction

Status: preregistered after EXP-065; pending clean execution

Consume only hash-verified EXP-051, 057, 062, and 065 event receipts. Compute
the three successive `b` spacings and two spacing ratios. Freeze the standard
period-doubling reference constant `4.66920160910299` solely as a prospective
prediction rule for the next event and accumulation parameter.

Pass if event parameters and spacings decrease strictly, both observed ratios
lie in `[4.0,5.2]`, and the later ratio is closer to the frozen reference than
the earlier ratio. Passing indicates internally consistent early convergence,
not asymptotic universality. The predicted period-80-to-160 event must be
tested independently and negative results retained.
