# EXP-048 — Locate the period-5 continuation family jump

Status: executed; failed
Manifest: `experiments/manifests/EXP-048-continuation-family-identity.json`

Classify all 46 stored rows of EXP-023's `period5-fixed-ac` natural
continuation using the original legacy Poincare section, starting directly on
each corrected orbit. The frozen hypothesis is one discrete identity change:
at least ten early rows are period 5, at least ten late rows are period 3, the
first/last rows have those identities, and exactly one transition occurs.

Passing locates a numerical corrector branch jump; it must not be interpreted
as a dynamical period-5-to-period-3 bifurcation. The adjacent rows and
correction diagnostics will define the next root-cause test.

The clean run at `10acddb0c077ff3e20e8cff3f29a6d074ec7cfd4` failed:
it returned 28 period-3, 6 period-5, 11 period-6, and one unresolved row with
eight apparent transitions. This cannot locate a corrector jump because the
multi-period integration lets numerical error leave unstable exact cycles.
Receipt SHA-256:
`62b9a0e02969e29f0ef85738ace7b0b2abc2c04e6edcbdf6d7ab7cc8f6c5cb9d`.
Retain the failure and replace the method with one-traversal section counts.
