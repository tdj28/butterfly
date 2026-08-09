# Landmark-0 diagnostic retained; EXP-186 held-out word test frozen

Date: 2026-08-07

A non-preregistered sizing diagnostic at the first Figure 6 coordinate used a
2,048-seed, 200-unit sprinkler. It retained 717 final survivors and 6,824
return pairs. The x projection robustly resolved two branches with critical
interval `[-5.66269,-5.62704]`, but z resolved as monotone. Independent flow
shooting closed the period-5 orbit to `1.14e-13`; its nearest x return missed
the critical interval by `0.04046`, leaving the branch-only cyclic sequence
`00101` rather than a `C/D` word.

This is a retrospective diagnostic, not a Figure 6 experiment. It shows that
an exact gray-box coordinate need not be a doubly superstable word center and
that cross-coordinate scalar invariance cannot be assumed.

EXP-186 therefore freezes the untouched second landmark. It reconstructs the
survivor partition at two RK4 steps, corrects the period-6 orbit in DOP853 and
Radau, requires x/z topology agreement, applies the already qualified
historical alphabet, and compares with the hash-bound period-6 targets only
after the word is computed.
