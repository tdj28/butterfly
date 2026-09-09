# EXP-499: a higher-precision reference for the saved section crossings

Status: prospective, outcome-informed accuracy pilot. EXP-498 and its
post-outcome phase diagnostic are already known; neither is replaced.

## Question and claim boundary

Do two independently configured decimal Taylor integrations agree on every
previously nominated accepted section crossing of all 32 EXP-498 side inputs,
and how do both original Float64 methods compare to that reference?

The working explanation is amplification of small trajectory errors at nearly
tangent crossings. EXP-498's first-order diagnostic motivates higher arithmetic
precision rather than a looser section-state threshold. Agreement would supply
a converged numerical reference at these exact realized inputs. Disagreement,
missing brackets, failed controls or incomplete execution leaves that reference
unqualified. Agreement of two configurations of one Taylor implementation is
not independent-team replication, a rigorous enclosure or proof of correctness.

This test does **not** re-shoot the grazing boundary, construct a new complete
event census, revalidate winding, repair EXP-498, assign C/D, locate a second
smooth critical point, or verify a Jones symbolic arrow. It refines the saved
accepted-event nominations only; unseen roots outside their boxes remain out
of scope. The original DOP853/Radau disagreement stays in the comparison table.

## Fixed inputs and matrix

- Parent compact result SHA-256:
  `f327a6acb9bb72cd0286ff41090f38e12e3b10a0ff9f476b0a6b2f705e176344`.
- All eight candidates and four side inputs each, ordered as in EXP-498.
  Preserve the 26-parent ledger, the historical EXP-492 failure and both
  EXP-498 failures. No difficult row or representation is dropped.
- Integrate the exact **realized binary64 initial state**, using
  `Decimal.from_float`, and the exact binary64 a, b, c and section constants.
  This deliberately does not substitute a more accurate equilibrium/section
  or re-round the nominal curve displacement. No variational trajectory is
  needed for this state-only reference.
- Each pair of original accepted events nominates one box: the arithmetic
  mean of its two saved times, plus/minus 1e-5. Use all 240 boxes, without
  nearest-event selection. Unequal parent event counts reject preparation.
- Exactly two configurations per input: 40 decimal digits, degree 24,
  maximum step .02; and 50 digits, degree 32, maximum step .01. Fixed steps
  terminate exactly at the saved horizon. No adaptive fallback, third
  configuration, selected precision, or retry is permitted.

## Numerical method and controls

Use Taylor coefficient recurrence for a sparse quadratic vector field. For
`q' = b + A q + sum B[j,k] q_j q_k`, coefficient n+1 is coefficient n of the
right-hand side divided by n+1. Horner evaluation advances each step. Every
step retains its full decimal coefficients, time and step size in compressed
JSON; these are not Float64 mesh surrogates.

The last three retained coefficient terms, scaled by (15,15,.01), must sum
to at most 1e-20 at every step. This is a truncation diagnostic, **not** a bound
on the omitted infinite tail. Reject nonfinite states or absolute state
coordinates above 1e4. Do not shrink steps after a failed guard.

For each nominated root box, require opposite plane signs and a negative
derivative interval throughout the box, evaluated on the piecewise Taylor
polynomial. Bisect to time width at most 1e-25, at most 100 iterations.
The endpoint zero case is retained explicitly. Require the resulting x below
the original half-plane bound and a scaled crossing angle at least 1e-7.
Numerical polynomial monotonicity is not a rigorous flow transversality proof.

Before target execution, test both configurations through the authentic
integration/storage/root consumer on: (1) harmonic rotation with a transverse
crossing, (2) rotation with two near-tangent crossings at y=1-1e-8, and
(3) x'=1, y'=x, z'=xz, whose solution from (0,0,1) is
(t,t²/2,exp(t²/2)). Scalar series/exponential identities check the output
independently of the coefficient builder. Negative controls reject absent
brackets, wrong orientation, nonfinite input and insufficient order/tail
accuracy. Timing and output sizes of these controls inform feasibility before
the freeze, not target thresholds after outcomes.

## Decision matrix

The complete new reference qualifies only if all 64 integrations and all 480
root evaluations complete and each paired root agrees in time to 1e-12 and
scaled full state to 1e-9. Report every root, not just maxima. Original-method
comparisons retain EXP-498's 1e-7 time and 1e-6 scaled-state thresholds, with
scales (15,15,.01), against **both** reference configurations. A failing
reference pair invalidates reference-based interpretation for that input;
there is no favorable-precision rescue or retroactive EXP-498 qualification.

Reproduce the raw coefficient recurrence using separately coded scalar
polynomial arithmetic, check mesh continuity and interval/root diagnostics,
rehash all raw files, and reconstruct the complete decision table before
interpretation. Small Decimal replay roundoff is checked at 10^(-digits+8)
relative/absolute scale; scientific thresholds are unaffected.

## Execution and release

Local CPU only; no API generation, paid Pro review, GPU rental or upload.
Maximum 64 target IVPs, 7,200 seconds, 2 GiB output, 11 GiB initial reserve
and 8 GiB free-space floor. Each input/profile start is persisted; exceptions
preserve partial output and stop without rerun. A clean, live-pushed source
inventory and successful controls precede exclusive creation of
`artifacts/EXP-499/target-once.json`. Existing attempt markers are untouched.

Freeze code, tests, protocol, plan and analysis before targets. Preserve full
coefficient trajectories locally, publish the audited compact all-root table,
and state clearly that full raw replay requires the local files. Existing
raw-publication approval boundaries remain unchanged. No novelty, rigorous
proof or formal manuscript release is claimed by this numerical pilot.
