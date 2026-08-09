# EXP-178 identifies a direction but retains the width failure

Date: 2026-08-07

EXP-178 ran from pushed clean commit
`439f0a8b433a32ed5932d385839fc4343541c71c`. The raw receipt is frozen at
SHA-256 `4817dc6d9fd7a027d36560453816140cb05dbae912cf153a8c3eed9ddf2d3133`.

Both `x` and `z` select increasing-coordinate trimodal critical `K1` as the
unique descendant of the unimodal critical, with normalized steps `0.02845`
and `0.02319`. Endpoint, coordinate-agreement, and identity gates pass. The
experiment remains failed because unresolved interior rows leave the resolved
bracket `[0.150,0.160]`, width `0.010`, above the frozen `0.005` maximum.

EXP-179 is the unchanged-threshold power successor: it doubles observation
support, doubles bootstrap support, and samples every `0.0005` inside the
failed bracket. No result threshold is relaxed.
