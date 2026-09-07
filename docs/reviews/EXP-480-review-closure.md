# EXP-480: pre-outcome review closure

This note accompanies the design brief and protocol. It reports a local source
inspection, not an external source audit. No nominated trajectory was run.

## Decision details supplementing the protocol

The machine plan uses `correct_periodic_orbit(max_evaluations=40,
tolerance=1e-11)` independently for each profile from the same old seed.
The two sections are `y=y_small`, downward, gated by `x<x_small`, and
`x=x_small`, upward, ungated. Equilibrium coordinates come from the same
Rössler parameters as the integrated field. The state metric is the Euclidean
norm after componentwise division by `[15,15,0.01]`; crossing angle uses the
unscaled physical coordinates. These choices are proposed diagnostics, not
coordinate-invariant certificates. Event phase is elapsed time divided by
that profile's corrected period, relative to the fixed window start.

All unordered pairs within each accepted window enter the distinct-state
test. All four profiles are compared against the first DOP853 profile, using
their first windows without rotation search. All relevant extrema across the
entire 2.5-period horizon enter the near-plane test. Absence of detected extrema
does not independently fail it. Raw roots rejected by orientation or half-plane
gate are retained, but there is currently no explicit half-plane-edge margin
or merged cross-section chronology separation test. Please assess whether
these omissions matter for the strictly limited event-feasibility claim.

## Local verification and claim-to-source closure

At pushed commit `8a415b9f7834188638498269d1b7348f1f9026b7`:

| Claim | Local evidence |
| --- | --- |
| Both old nominations and input hashes are fixed | Real CLI `--mode preflight` passed; `prepare` validates both input hashes and the ordered nomination list |
| Draft cannot execute | Actual CLI entry-point test rejects before reading target inputs |
| Oriented/gated events follow raw collection | `collect_events` retains plane roots, extrema and masks; analytic circle tests exercise DOP853 and Radau |
| Fixed order, windows and failure retention | `summarize_events`, `compare_windows`, `execute`; synthetic rotation, boundary, extrema, solver, interruption and source/raw-corruption tests |
| No historical word outcome | Runner calls no partition fitter or word encoder |

Focused tests: 16 passed on Python 3.13, rerun before this review. The previously
reported full suite was 1,327 passed and one Linux-only skip; this review step
does not claim a new full-suite run or a target-host numerical qualification.
Source and design hashes are in the brief; the canonical design remains
`c7915accbf4dc63d5fba84434ad98aa95163a466d4119390aa21d350daca9fe4`.

## Review handling and reserved paths

The first API attempt is reserved at `artifacts/EXP-480/review-01`; its exact
request, response and usage will be retained. Public promotion, if completed,
will use `docs/reviews/EXP-480-review-01/`. Adjudication will use
`docs/reviews/EXP-480-adjudication.json`, schema
`butterfly.design-review-adjudication.v1`. Required fields are `design_sha256`,
`approved_for_execution`, nonempty `adjudication`, hash-bound `review_receipt`
and `runtime_files`. The manifest remains unauthorized until material findings
are resolved, the actual response is validated and the source is pushed.
Review does not certify omitted source or raw observations, and is not
independent scientific replication.

The canonical review helper is reused from the sibling skills repository at
commit `2950bcc6104b090bc46731a45aed7f92a431b6ad`, script SHA-256
`7ebe3185868e0f4ebe07c162a95c7c2195669e02ce5dde088aad0456859b6dff`.
The initial local dry run rejected a direct machine-manifest attachment before
creating a request or making any API call. This Markdown note supplies the
remaining compact decision details; the original machine plan is unchanged.

[Official model guidance](https://developers.openai.com/api/docs/guides/latest-model)
and [pricing](https://developers.openai.com/api/docs/pricing), checked September
6, 2026, identify GPT-6 Astra and standard short-context rates of $10 input,
$12.50 cache writes and $50 output per million tokens. The proposed request
uses Pro/medium, 6,000 requested output tokens and a $1.50 authorization guard
within the user's standing research authority. The reserve is not a provider
billing hard stop. No new Runpod worker or background API storage is requested.
The default $1.25 dry-run guard rejected the complete compact packet; a $1.50
guard accommodates the $1.445 reserve at current flagship rates. No paid call
occurred during either dry run. This is not a request to increase the user's
overall budget.
