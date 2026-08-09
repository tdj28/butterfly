# EXP-186 rejects the exact-landmark word-center assumption

EXP-186 executes from clean source commit
`877ee75e77bbbd874bbd4311ebd38f8f14e1ed95` and fails scientifically. The
negative result is localized: the exact second gray-box coordinate cannot be
reproduced as a Figure 6 period-6 word center under the preregistered method.

The periodic orbit itself is not in doubt. DOP853 and Radau independently
close it below `2.14e-13`, recover six section returns and period
`34.465148489`, and agree over the complete orbit to scaled error `1.23e-9`.
The two fixed-step survivor runs have no failures, nearly identical survivor
counts, 7,335/7,299 usable pairs, and a maximum survivor-fraction difference
of `0.001465`.

Both steps resolve x as two-branch with normalized critical-midpoint
difference `8.41e-5`; both resolve z as one-branch and monotone. The mandatory
coordinate-parity gate therefore fails. The x words are solver-stable within
each profile but not step-stable: `010011` at `dt=0.01` and `C10011` at
`dt=0.005`. Neither matches a frozen period-6 source word, even under reversal
and cyclic rotation.

This preserves rather than weakens the research program's non-circularity. We
will not fit a box, boundary, alphabet, or orbit to recover an expected word.
The next experiment will freeze a target-word-blind search for an actual
superstable period-6 center, using orbit stability and criticality as the
objective; word encoding comes only afterward.

Raw receipt SHA-256:
`efae1b0cbee8edf74bf11b6bf3de38c56418c5f8acb454ea3297722d7a836903`.
