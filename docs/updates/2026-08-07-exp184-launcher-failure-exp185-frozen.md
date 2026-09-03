# EXP-184 launcher failure preserved; EXP-185 frozen

Date: 2026-08-07

EXP-184 stopped before integration because the parent validator did not follow
EXP-183's nested `gates.passed` field. No trajectory, mapping decision, or raw
scientific receipt was produced. The administrative failure is retained in
the experiment record.

The validator now supports tested dot-delimited evidence fields. EXP-185 is
scientifically unchanged: it freezes the same source semantics, hashes,
solvers, initial states, partitions, mapping, segments, and acceptance gates.
Only the experiment identifier and receipt-field selectors differ.
