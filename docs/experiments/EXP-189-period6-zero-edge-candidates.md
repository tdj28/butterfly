# EXP-189 — Period-6 zero-edge candidate preparation

Status: executed; passed

EXP-188's frozen fine grid contains 65 adjacent sign-changing edges. EXP-189
takes all 65 without ranking or symbolic information, linearly interpolates a
zero on each edge, and corrects the corresponding period-6 flow orbit from the
closer endpoint.

Every accepted candidate must retain stable opposite-sign endpoints, six
negative-section returns, flow closure below `1e-8`, a real stable transverse
multiplier of magnitude at most `0.1`, and scaled whole-orbit distance at most
`0.08` from its seed endpoint. At least 60 candidates must pass for the fixed
set to feed the GPU survivor scan.

This stage prepares orbits only. It neither reconstructs a critical point nor
selects a center. Figure 6 words and alphabet labels are absent from the
manifest and runner.

Manifest:
[`../../experiments/manifests/EXP-189-period6-zero-edge-candidates.json`](../../experiments/manifests/EXP-189-period6-zero-edge-candidates.json).

## Result

All 65 interpolated candidates pass from clean commit
`84a9621f5a61efc28ad2f53fecee1213348864cc`. Flow closure is at most
`1.83e-12`, phase residual at most `4.69e-18`, endpoint-scaled orbit change at
most `0.032105`, and neutral-multiplier error at most `2.04e-9`. Every
candidate is stable; corrected transverse moduli range from `8.31e-5` to
`0.047172`. The parameter set spans `a=[0.21514,0.21614]` and
`c=[6.1058881,6.1320503]`.

Candidate artifact SHA-256:
`33ccb7968190d2af7ac775fcbc0418fab76ea1935bd83027db0178f5f379070a`.
Compact receipt: [`receipts/EXP-189.json`](receipts/EXP-189.json).
