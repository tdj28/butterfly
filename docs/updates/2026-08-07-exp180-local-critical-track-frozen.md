# EXP-180 local Jones critical track frozen

Date: 2026-08-07

EXP-180 replaces the failed global-count identity bracket with a prospective
local observable. Its x/z anchors are the normalized critical midpoints from
independently qualified EXP-177, not values chosen from EXP-178/179 or Figure 6
words. Each spline variant selects the nearest prominent critical, requires an
anchor step no larger than `0.12` and runner-up margin at least `0.15`, and
bootstraps local identity independently of total critical count.

The experiment uses a fresh initial state, a 21-point DOP853 path, and five
independent Radau controls. Every local row and all seven variants must pass;
adjacent DOP853 locations may move by at most `0.03`, solver locations may
differ by at most `0.02`, and both endpoint global controls must still resolve
two then three branches. At the three-branch endpoint, both solvers and both
coordinates must identify increasing-coordinate critical index 1 with margin
at least `0.15`.

This can qualify local operational identity only. Global shallow-critical
birth, historical alphabet mapping, Figure 6 words, and a TBA curve remain
separate tests.
