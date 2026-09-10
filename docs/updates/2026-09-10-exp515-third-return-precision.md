# EXP-515: test the sensitivity loss at its first occurrence

## Why this is the next experiment

EXP-514 is merged through [PR #80](https://github.com/tdj28/butterfly/pull/80)
at `1aaf32e041b02a26bf1804682b1a97fd66cae9ad`, after all four exact-head
Python 3.12/3.13 checks passed. Its five numerically qualified grazing
representations must not be recycled as unexplained smooth-fold brackets.

The remaining issue is the near-collapsed transported curve. The saved data
locate its first tiny event-corrected sensitivity at the third return, well
before the eighth-return rejection. Subtracting the flow-direction component
can be ill-conditioned, but the subtraction formula is mathematically correct;
that observation does not itself establish a bug, a true zero, or the accuracy
of a tiny nonzero result.

The [prospective EXP-515 protocol](../experiments/EXP-515-third-return-precision.md)
therefore keeps all six center/neighbor initial conditions in both directions,
compares the existing two higher-precision Taylor configurations, and retains
both historical solver comparators. It needs twelve target integrations, not
twenty-four duplicated solves. Exact binary64-realized inputs and the existing
binary64 section are carried into Decimal without silently changing the IVPs.

The main measurements are the complete event-corrected tangent, its
root-box sensitivity and paired relative error at each of the first three
returns. A tolerance larger than the tangent cannot label it resolved.
The historical gain threshold is unchanged. The strongest positive outcome is
a precision-consistent small nonzero tangent at these inputs, not a verified
Jones symbol or chain. Agreement of two numerical profiles is not an exact
ODE error enclosure or independent-team replication.

## Target-free validation

The runtime, complete-polynomial census adapter, scalar raw auditor and
analytic controls are implemented. The controls include ordinary sensitivity,
pure phase sensitivity, a tiny transverse remainder, and roots on both sides
of the initial exclusion cutoff. They use the actual compressed archive,
quota-admission and event-analysis paths.

The first test run passed twelve cases and failed four because control input
strings used lowercase scientific notation while Decimal's archive producer
canonicalized them to uppercase. The first retained control run stopped on the
same exact-byte discrepancy after five control IVPs. No target IVP or attempt
marker existed. The control builder now emits canonical Decimal strings;
the strict raw-input comparison was not weakened. Failed XML and partial
control products remain in `artifacts/EXP-515/preflight-tests-01.xml` and
`preflight-controls-01/`.

The corrected **17 focused tests pass**. All **12 actual analytic control
IVPs pass** their known identities, full raw recurrence audit and independent
polynomial-certificate replay, retained in `preflight-controls-02/`.
A fresh **35-file isolated consumer passes** under `python -I -B`, with no
ambient checkout or bytecode; its receipt is `preflight-startup-02.json`.
Full regression passes **2,736 tests with one Linux-only skip** in 538.84
seconds (`preflight-suite-01.xml`). The staged public scan passes on 2,931
files, and manuscript citation/figure checks plus the symbolic control-table
check pass. No target outcome is claimed at this pre-freeze checkpoint.

## Local design audit and limits

The local audit explicitly rejects these shortcuts: changing the section while
claiming only a precision change, treating two old solver labels as distinct
initial conditions, projecting at a float-rounded event time, trusting only
the x component, using a large absolute tolerance to resolve a small tangent,
and dropping a failed return ordinal. The paired profiles differ in precision,
order and step together, so their contrast is not a precision-only causal test.
The separately coded coefficient recurrence and determinant-form projection
supplement, but do not replace, the shared integrator/census limitations.

Raw data remain local. No paid review, new worker or raw upload is used.
The next action is to freeze and live-verify the tested source, execute the
complete twelve-IVP matrix once, audit every retained product and publish the
result whether it resolves the sensitivity or leaves it unresolved.
