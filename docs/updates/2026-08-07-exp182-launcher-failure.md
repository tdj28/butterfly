# EXP-182 administrative launcher failure retained

Date: 2026-08-07

EXP-182 exited before reading its manifest or running a trajectory because the
direct script entry point imported a sibling helper through a package path
available to pytest but not to direct execution. No receipt or scientific data
was produced. The failure is administrative and does not vote on any
scientific gate.

The launcher is made self-contained, its focused and full tests are rerun, and
EXP-183 copies every EXP-182 scientific parameter and acceptance threshold.
Only the experiment identifier and administrative predecessor record change.
