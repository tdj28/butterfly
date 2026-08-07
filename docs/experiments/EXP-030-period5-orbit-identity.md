# EXP-030 — Phase-invariant identity of the switched period-5 orbit

Status: executed; passed
Manifest: `experiments/manifests/EXP-030-period5-orbit-identity.json`
Claim target: invariant-cycle identity after EXP-029 branch switching

## Hypothesis and method

At the previously uninspected `b=0.2730`, the two EXP-029 coordinate arms are
phase-shifted representations of one secondary geometric orbit, while that
orbit is distinct from the primary EXP-027 family. The primary orbit is
unstable and the secondary orbit stable immediately above the event.

Interpolate each receipt to the frozen `b`, independently correct all three
periodic orbits at fixed parameters, and sample each corrected flow over one
period. Minimize cyclic phase-aligned trajectory RMS over 512 phase samples and
512 coarse shift seeds followed by bounded scalar refinement. This comparison
uses entire trajectories, not a phase-dependent initial-state distance.

## Acceptance and limits

All closures must be at most `1e-8`. The two secondary arms must align below
RMS `1e-5`; each primary-secondary RMS must exceed `1e-2`; and their flow
periods must differ by at least `1e-4`. The primary significant transverse
multiplier must exceed one while both secondary representations remain stable.

Passing establishes two distinct invariant cycles above the event: one primary
and one secondary, with the two switched signs identified as phase copies. It
supports but does not prove a supercritical pitchfork-like normal form. A
classification still requires continuation below/above the event, symmetry
analysis, and scaling of branch separation and stability versus `b-b*`.

## Result

The clean run at commit `1f7d88679d7ab73d2bf42f0b78dbb1a4ca66acde`
passed every gate at the prospectively frozen `b=0.2730`. The secondary-arm
phase-aligned RMS was `5.43e-7`, while the two primary-secondary comparisons
were both `0.200268`. The primary-secondary period gap was `0.0107849`.

All three corrected closures were below `1.3e-13`. The primary orbit had
maximum transverse multiplier modulus `1.062085` and was unstable. Both
secondary representations had modulus `0.878698` and were stable. The complete
receipt SHA-256 is
`924f9211ad5f98a6fb2a2ddb066e45dac199128e90fdf5040a271f1da3942be5`.

## Decision

Accept two distinct invariant period-5 cycles immediately above the EXP-028
event: an unstable primary family and a stable secondary family. The two signs
of the EXP-029 switch are phase copies of the secondary cycle, not two distinct
cycles. This is a phase-invariant stability-exchange result. “Supercritical
pitchfork-like” remains a hypothesis until EXP-031 tests the local square-root
branch-separation and multiplier scaling prospectively.
