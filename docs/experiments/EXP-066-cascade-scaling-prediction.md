# EXP-066 — Cascade spacing analysis and prospective prediction

Status: executed; passed after a non-scientific serialization fix

Consume only hash-verified EXP-051, 057, 062, and 065 event receipts. Compute
the three successive `b` spacings and two spacing ratios. Freeze the standard
period-doubling reference constant `4.66920160910299` solely as a prospective
prediction rule for the next event and accumulation parameter.

Pass if event parameters and spacings decrease strictly, both observed ratios
lie in `[4.0,5.2]`, and the later ratio is closer to the frozen reference than
the earlier ratio. Passing indicates internally consistent early convergence,
not asymptotic universality. The predicted period-80-to-160 event must be
tested independently and negative results retained.

The clean receipt run at `830ace0bc9d439b2875c0fb43f5f9ce04e5c8e38`
passed. The successive spacings are `0.002930382569`, `0.000645984441`, and
`0.000140602394`, giving ratios `4.536305` and `4.594406`. The later ratio is
closer to the frozen reference. Receipt SHA-256:
`0b0e5f7fe44d21b10c12b5f0cc20eee943dbe3f2c88d31a8b70161c088a40c2e`.

The frozen prospective prediction is period 80→160 near
`b=0.1797205086405`, with accumulation estimate `b=0.1797123017524`. These
numbers guide the next search but do not count as verified events. The first
execution completed its arithmetic but wrote no receipt because a NumPy
boolean was not JSON serializable; commit `830ace0` made the one-line scalar
conversion and reran the unchanged manifest.
