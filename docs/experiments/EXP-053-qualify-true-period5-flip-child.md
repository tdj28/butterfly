# EXP-053 — Qualify the true period-5→10 flip child

Status: executed; passed

At frozen `b=0.1825`, independently correct the period-5 parent and both
ten-crossing switched arms. Require the arms to identify one geometric child
below phase-aligned RMS `1e-5`, parent/child separation above `1e-2`, closures
below `1e-8`, parent identity/stability 5 and unstable, and child
identity/stability 10 and stable. Passing confirms a local supercritical
period-5-to-period-10 flip independently of the later section-topology change.

The clean run at `abf62464da3263cc9c85b9c1a85124642c4dde21` passed.
At `b=0.1825`, the period-5 parent has modulus `1.16299`; both period-10
children have modulus `0.362719`. The two switched arms align after phase shift
to RMS `6.71e-7`, while parent/child RMS is `5.6453`. Closures are below
`2.57e-13`. Receipt SHA-256:
`3c937890d18ada3c22b3859bc8824061e9a28e6ec9cf91126a5db4bb876f6f16`.

Accept a supercritical period-5-to-period-10 flip. Refine the separate legacy
section-count change observed farther along the stable child.
