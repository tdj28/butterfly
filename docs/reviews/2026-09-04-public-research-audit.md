# Public research audit — 2026-09-04

Base revision: `30c6cfc`, following EXP-473. Review branch:
`codex/public-research-audit`. This audit covers core numerical acceptance,
scientific interpretation, public-source reproducibility, credential handling,
and manuscript presentation. It does not replay every historical experiment
or certify every claim in the repository.

The project contains useful numerical work and unusually detailed negative
results. The main weaknesses are a mistaken full-flow superstability
interpretation, incomplete conditioning/error analysis, missing public raw
data, and a growing gap between the execution log and the original scientific
questions. The [next-step queue](../next-steps.md) puts those issues first.

## Confirmed errors and fixes

| Issue | What changed | Evidence and historical scope |
|---|---|---|
| Failed basin integrations could be labeled periodic from partial returns | `evaluate_initial_condition` now overrides any recurrence label with numerical failure when integration failed | Regressions cover recurring partial returns and no returns. EXP-017 records all 441 integrations successful; this bug was not demonstrated in that result. |
| Escaping trajectories could count as a second attractor | Mixed escape/bounded outcomes are unresolved; unanimous escape remains escape | Regression tests exercise both cases. EXP-010/014 label counts contain no escapes, so this does not explain their former multistability candidates. |
| Shooting acceptance omitted phase and/or arclength constraints | Success now requires every equation in the corrector residual to pass | Tests simulate optimizer stagnation with excellent closure but bad constraints. EXP-157/160/162/164 spot checks still pass; additional callers require audit. |
| Full-flow Floquet zeros were interpreted as superstability centers | Retracted the interpretation in the paper, claim ledger, FND-060/061, and historical script descriptions | Liouville's formula makes exact finite-time monodromy invertible. The corrected periodic-orbit samples remain evidence; alleged zero curves do not. |
| A three-branch scalar map was called trimodal | Current manuscript uses bimodal for two critical points/three monotone branches | Historical experiment field names remain unchanged for reproducibility. |
| Period terminology conflated time, winding label, and section count | Paper defines flow period `T` separately from integer labels and return counts | A historically labeled period-6 orbit can have eight returns on another section. |
| Tests depended on a local Git checkout | Tile tests now supply controlled provenance; runtime provenance requirements remain enforced | Original source archive: 398 passed, three failed. Isolated corrected archive: 411 passed before the other audit changes were added. |
| Citation checks accepted commented or unincluded citations | Checker follows included TeX sources, ignores comments, and rejects duplicate keys and missing source/figure files | New regression cases; all 31 manuscript images are available in Git. |
| RunPod cost limits accepted nonfinite values; errors could echo credentials | Reject invalid ceilings before requests; invalid returned prices trigger task-owned cleanup attempts; redact current credentials from errors | Mocked request/response and failure tests only; no live provider behavior was revalidated. |
| Public setup was underdocumented | Explicit Pillow dependency, CPU CI for Python 3.12/3.13, broader secret-file ignores and a tracked-file credential check | Clean-source CPU verification needs no API key, raw artifact directory, or local reference PDFs. |

## Scientific corrections and remaining uncertainty

### Full-flow Floquet zeros

For a regular periodic Rössler orbit,
`det M(T) = exp(integral_0^T [a+x(t)-c] dt) > 0`. The neutral multiplier is
one, so neither transverse multiplier can be exactly zero. A scalar map's
derivative can vanish at a critical point, but that formula cannot be applied
to the full-flow monodromy. See [Teschl, equation (3.122)](https://www.mat.univie.ac.at/~gerald/ftp/book-ode/ode.pdf).

The old center heuristic selected the largest-modulus transverse eigenvalue
and used a signed diagnostic derived from it. For example, the pair
`0.01 exp(±i theta)` has real parts that change sign while its product remains
`1e-4`. Mode selection and lost precision introduce additional ambiguity.
The 65 EXP-189 samples remain corrected orbits, but are not a complete set of
physically defined center candidates. This was a mistake in our modern
interpretation; it is not a refutation of the original scalar-map claim.

### Homoclinic continuation

The fixed-c candidate near `a=0.182643608174` has useful checks from independent
integrators, shooting meshes, and matching radii. Subsequent continuation has
81 accepted points through EXP-473; the figure is an 80-point snapshot.
These points belong to one correlated continuation chain.

At its latest points the reported maximum block defect is about `3.2e-9`
and the smallest singular value about `8e-10`. Neither the defect threshold
nor that singular-value floor bounds error in `a` or `c`. A generic inverse
Jacobian estimate can be loose; the residual direction and parameter
sensitivities matter. This does not prove the turn is wrong, but does prevent
claiming its fine physical location from the current diagnostics alone.

The revised paper calls it a sampled numerical turn pending an independent
boundary-value and parameter-error study. Finding a nearby connection at a
different coordinate does not exclude a different connection at Jones's
printed point. Uniqueness and global nonintersection remain unestablished.

### Other method boundaries

`correct_unit_multiplier_orbit` assumes an independent transverse unit
eigenvector. A generic cycle fold can instead have a defective double unit
multiplier. For `M=[[1,1,0],[0,1,0],[0,0,0.2]]` and flow direction `e1`, the
transverse vector `e2` satisfies the projected return-map condition but not
the current full-monodromy condition. This API limitation is documented;
failure of that corrector cannot exclude a fold. No generic fold solver was
silently substituted into the archived protocol.

The eighth-birth criticality interpretation also deserves a stronger local
test. A sampled stable parent and unstable child, with child multiplier near
19, is not by itself a convergent near-birth normal-form calculation. Shrink
the daughter amplitude toward the event and check convergence of the relevant
multiplier toward `+1` before emphasizing this as new physics.

## Public repository and presentation

The remote was verified public with `main` as its default branch. A read-only
scan covered all objects reachable from the fetched local Git refs: 726
commits, 5,242 trees, and 5,309 file blobs. It compared the five currently
configured local credential values and checked common provider-token,
private-key, and AWS-access-ID patterns. No matches were found. `.env` was
not tracked and had no path history in those refs. This is a bounded scan,
not a guarantee against all possible secret formats or previously deleted
remote refs. No credentials or credential values appear in the report.

The public source includes finished figures, manifests and compact receipts,
but most raw `artifacts/` inputs remain local. The README now says explicitly
that figure regeneration is incomplete without a released data archive.
This is a reproducibility gap even when every missing input has a checksum.

The abstract and conclusion were reduced from chronological experiment logs
to an argument with stated limits. The manuscript defines numerical "exact"
as direct root correction, not exact arithmetic or proof. The front-page
atlas now states its bounded domain and finite-time, single-initial-condition
scope. The figure count was corrected from 30 to 31. Negative experiments and
frozen receipts were preserved.

The pre-audit bibliography contained ten references, all dated 2012 or earlier.
The promised post-2012 literature synthesis has not been done. A checked
foundational reference for the mathematical correction has now been added;
it does not fill that larger literature gap.

## Verification and follow-through

The unchanged starting suite passed 401 tests; the audit found uncovered
failure cases despite that result. The dated [update](../updates/2026-09-04-public-research-audit.md)
records final combined checks, manuscript rendering, and commits.

No research data, failed receipts, branches, or historical Git commits were
deleted or rewritten. No paid compute or external messages were sent for this
audit. RunPod changes are unit-tested only; the hourly ceiling is a
post-provisioning guard and does not enforce a cumulative spending budget.
