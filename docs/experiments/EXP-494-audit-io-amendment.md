# EXP-494: read-only audit caching amendment

September 9, 2026, after the 806-IVP target run completed. No numerical target
was rerun or overwritten. The complete summary remains SHA-256
`3a51ec4aaf07d15975c25e9dc47a907b0e43cc6d9a8cee7fddfe1d3f85263e6e`.

The first frozen audit was interrupted, exit 130, during NumPy's repeated
decompression of `dense_coefficients`. `dense_value` requests the same NPZ
arrays for each interpolation query; an NpzFile does not cache those reads.
The small dictionary-based controls did not expose this full-size I/O cost.
The interruption stack is preserved in the task tool output. No `audit-01`
success receipt was produced, and no success is inferred from that attempt.
Raw geometry had been recomputed by the audit, but no target scientific
metrics or final verdict had been inspected by the coordinating agent.

The new adapter `scripts/audit_exp494_cached.py` loads each NPZ member once,
retains the exact dtype/shape/values, and supplies read-only arrays through a
context-manager mapping. It calls the **unchanged frozen auditor**; all
source, input, grid, event, geometry, period and failure checks remain intact.
Cache guards bound each archive to 64 members/128 MiB expanded arrays.
The adapter's hash is separately recorded in the returned audit receipt.
The release builder and fresh-data replay use this explicitly labeled path.

This is an operational post-run amendment, not a new numerical result or a
replacement for a failed scientific threshold. The original audit and all
bound EXP-494 source files remain byte-identical. Both lazy and cached paths
are checked on exact-circle NPZ fixtures before the new adapter is pushed and
executed against the full data. No paid review is requested or required.
