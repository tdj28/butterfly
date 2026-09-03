# FND-006 — An attracting return-map transition band is bracketed

Date: 2026-08-07
Status: qualified attracting-set bracket; not a TBA continuation

EXP-109 prospectively scans 21 values on the published path
`b=0.2,c=20`, using the exact Barrio section and a recurrence gate before the
branch oracle. Resolved primary maps are ordered: all two-branch values lie
below all three-branch values. The last resolved two is `a=0.155`; the first
resolved three is `a=0.16`.

This is the first uncertainty-gated numerical bracket of the branch change in
the modern project. It also reproduces the obstruction emphasized by the PRL:
five sampled parameters have stable period-4 attractors, including the paper's
`a=0.118` and `a=0.149` saddle controls, so their attractors contain no chaotic
return map to classify.

The bracket must not be overinterpreted. The `a=0.155` primary decision sits
exactly at the consensus threshold; its `z` cross-check is unresolved and
leans toward three branches. More importantly, the PRL reports a bimodal
nonattracting chaotic saddle already at `a=0.149`. The attracting-set band and
the invariant-saddle TBA are therefore not yet the same computed object.

Next, qualify a saddle-preserving method on the two published regular controls:
it must recover a two-branch chaotic saddle at `a=0.118` and a three-branch
chaotic saddle at `a=0.149` while separately recovering the coexisting stable
period-4 orbit. Only then may the TBA be refined through the regular gap and
continued in `(a,c)`.
