# EXP-256 — Period-96 sign phase-resolution audit

Status: completed — passed

EXP-256 is the scientifically identical administrative successor to EXP-255.
The only code change converts a NumPy boolean optimizer status to a built-in
JSON-serializable boolean. The immutable EXP-254 nodes, solver profiles,
2,048 phase samples, half-period search interval, `1e-14` bracket-width target,
and unchanged `1e-6` orbit-identity threshold remain fixed.

Manifest:
[`../../experiments/manifests/EXP-256-jones-period96-sign-phase-resolution-audit.json`](../../experiments/manifests/EXP-256-jones-period96-sign-phase-resolution-audit.json).

## Result

Both independent continuous searches pass. DOP853 and Radau locate phase
shifts `0.5000000060319/0.5000000060309` with whole-orbit RMS
`3.45e-10/4.57e-9`; their final phase brackets are `7.88e-15` wide. Segment
endpoint errors remain below `2.92e-12`. The two tangent signs therefore
represent one stable primitive period-96 orbit up to phase.

Raw receipt: `artifacts/EXP-256/receipt.json`, 2,480 bytes, SHA-256
`fab190b9975dbaa47fe5b68016f71fb1bf3e206761fb6c22834b8fc9f96cb892`.
Compact receipt:
[`receipts/EXP-256.json`](receipts/EXP-256.json).
