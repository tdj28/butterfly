# Update — EXP-144 phase-resolved capture refinement preregistered

EXP-143 qualified the full endpoint lobe atlas but found strongly overlapping
occupancy. Its four selected branches differ more in finite-horizon stable-cycle
capture than in occupied support. EXP-144 therefore tests that signal directly
before any connection residual is invented around it.

The frozen run contains 408 exact-return traces: four automatically selected
branches, two endpoints, three transported orbit phases, and 17 nested seed
amplitudes. It retains the original capture definition, adds a 96-return
horizon, validates each transported Floquet direction, and requires nested-grid
mean capture times to agree within two returns. A candidate qualifies only if
the endpoint difference is at least five returns and has the same direction at
all phases and both administrative horizons.

This is deliberately a discriminator. Passing would identify branches worth a
direct connection boundary-value solve; failure would show that the EXP-143
capture contrast is seed-phase dependent and should not carry a mechanism
claim.

## Result

The prospective gate fails cleanly. All 408 trajectories and all 24
transported-direction checks pass numerically, but only 13 of 24 nested-grid
summaries qualify and no candidate clears the five-return effect floor at all
three phases. Two candidates reverse their 64/96-return direction at one
phase. The EXP-143 capture contrast is therefore retired as a mechanism proxy;
the persistent UPO library remains available for a direct geometric
intersection or symbolic-pruning residual.
