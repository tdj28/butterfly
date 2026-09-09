# EXP-494 post-run shorter-cycle diagnostic

September 9, 2026, after full primary replay passed and outcomes were opened.
Both decreasing-a arms failed at step four because their corrected trace
repeats at half the supplied period. This motivated the new analysis; it was
**not** a frozen primary endpoint and cannot replace either failed verdict.

Retain both failed nodes (`local-a025-c083--aminus--04` and
`local-a027-c083--aminus--04`) and both solvers. Reuse their exact full saved
observations under primary-summary SHA-256
`3a51ec4aaf07d15975c25e9dc47a907b0e43cc6d9a8cee7fddfe1d3f85263e6e`.
Set candidate period to exactly half the stored corrected period, without
new optimization or integration. Apply the same frozen whole-cycle consumer
and thresholds, now at phase windows [0.25,1.25) and [1.25,2.25) of that
shorter period; compare both methods using the existing paired-window rule.
Counts and geometric winding are measured, not fixed to three.

Record all four profiles, repeated windows, failures and paired comparisons.
The circular controls must accept halving a double traversal and reject
halving a genuine single traversal, with both numerical solvers. Source,
tests and this amendment are committed/pushed before the new diagnostic.

A passing result supports a conditional numerical shorter-cycle identity.
It does not locate a flip, establish daughter-to-parent convergence, prove
the two original nominations are primary shrimp centers, or verify a Jones
symbolic insertion. No new target run, paid call, or consumed-attempt reset.
