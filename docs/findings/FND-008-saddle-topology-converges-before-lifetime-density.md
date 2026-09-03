# FND-008 — Saddle topology converges before lattice-sampled lifetime density

Status: qualified component result inside a retained prospective failure

## Result

EXP-111 executes five independently declared saddle ensembles at each
published regular control: baseline, half-step, later conditioning, shifted
grid, and coarser shifted grid. It evaluates both section coordinates with 15
binning/smoothing variants and 50 bootstraps per variant.

All 300 topology cells recover the expected result:

- every `a=0.118` cell is two-branch;
- every `a=0.149` cell is three-branch;
- every within-run variant consensus is `1.0`;
- across-run normalized critical-location drift is at most `0.01666` in `y`
  and `0.01199` in `z`, well below the frozen `0.04` gate;
- all runs retain thousands of within-trajectory pairs and no numerical
  failure.

This comprises 15,000 deterministic bootstrap refits. Step halving changes
survivor fractions by at most `0.00538` at `a=0.118` and `0.01746` at
`a=0.149`; the topology and critical locations are stable. Later conditioning
to time 360 also retains the same counts.

## Why the experiment still fails

EXP-111 is retained as failed because two non-topology gates miss:

1. Shifting a regular grid changes the maximum checkpoint survivor fraction by
   `0.05896` and `0.06458`; the coarser shifted grid reaches `0.07962` at the
   unimodal control. These exceed the frozen `0.05` limit.
2. One of ten short-horizon audit seeds has maximum crossing-time error
   `3.4639e-5`, above `2e-5`. Its scaled section-state error is only
   `4.5493e-4` and passes the `0.001` state gate. The other nine time audits
   pass.

The first failure is consistent with regular-lattice aliasing of a finely
structured survivor set. It means raw lifetime density is not yet grid-
converged; it does not erase the observed topology stability. The replacement
must use independent scrambled low-discrepancy ensembles and convergence bands
across scrambles and powers-of-two sample sizes.

The second failure isolates the linear within-step crossing interpolation,
not the RK4 flow step. Replace it with cubic Hermite interpolation using the
endpoint vector fields, then repeat the same independent DOP853 audit.

## Implication for Jones and Barrio

This is the strongest direct modern evidence so far for the regular-window
saddle part of the 2012 topology story. The extra branch at `a=0.149` is not a
visual impression or a single tuned spline: it survives two coordinates, five
complete ensembles, 15 oracle perturbations, and every bootstrap. The
`a=0.118` control simultaneously remains two-branch.

The result strongly supports the existence of the published local two/three
saddle distinction. It does not yet establish a continued TBA curve or Jones's
reinjection mechanism. Overall saddle qualification remains open until the
scrambled-ensemble density and crossing-interpolation gates pass, followed by
an independent PIM/stagger-and-step construction.
