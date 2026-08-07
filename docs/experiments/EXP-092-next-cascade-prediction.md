# EXP-092 — Predict the period-640 flip

Status: executed; passed

Bind all seven verified flip-event receipts from 5→10 through 320→640. Compute
the six spacings and five finite ratios, then use the unchanged frozen
reference `4.66920160910299` to predict the 640→1280 event and updated
accumulation parameter.

Pass if event parameters and spacings decrease strictly, every ratio lies in
`[4.0,5.2]`, and the final ratio is closer to the frozen reference than the
first. The result freezes the next search target; it is not itself evidence
that period 1280 exists.

The clean run at `bce8d802e6639ea039207d50e2ac7b75ea0f16da` passed. The
five observed spacing ratios are `4.536305`, `4.594406`, `4.647627`,
`4.664603`, and `4.668192`; the last differs from the frozen reference by only
`0.0010096`. The prospectively frozen 640→1280 prediction is
`b=0.1797121964470`, and the updated accumulation estimate is
`b=0.1797121153539`. Full receipt SHA-256:
`3d3bd7a0e72320f14d078a3895f81291e20b82d8cdf5fb0655df53f1ae9cea08`.

These values define the next segmented scan. They remain finite-sequence
predictions until an independently corrected period-640 `-1` event is found.
