# EXP-189 — Period-6 zero-edge candidate preparation

Status: preregistered; not yet executed

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
