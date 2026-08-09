# EXP-158 period-2 qualification frozen

Date: 2026-08-07

EXP-157 passes its frozen local switch gates from the exact period-1 flip:

- doubled-cover shooting singular value: `5.840844773053272e-15`;
- parent/child tangent dot product: `5.551115123125783e-17`;
- both transverse signs continue for 24 accepted points;
- endpoint half-period closures are `0.2278273` and `0.2041713`;
- endpoint dominant nontrivial moduli are `0.9880594` and `0.9904612`.

These facts establish a local nontrivial branch but do not alone prove that the
two signs are the same invariant period-2 cycle or that the parent-to-child
stability exchange survives an independent integration method.

EXP-158 therefore freezes a common target `c=3.1845` and requires:

- fixed-`c` correction of the parent and both child signs;
- phase-invariant identity of the two child signs;
- primitive period-2 identity by failure of half-period closure, period ratio,
  and two windings around the regular small equilibrium;
- unstable parent and stable child;
- independent Radau agreement with DOP853 in orbit identity and multiplier
  modulus;
- recovery of the stable child after perturbed forward integration.

The manifest is
`experiments/manifests/EXP-158-qualify-period2-c-child.json`. It is hash-bound
to raw EXP-157 receipt
`dbf1bd63fa987be7307557fa094edeec74c0e79afc2acfa6436ec2d6b09b244f`.
