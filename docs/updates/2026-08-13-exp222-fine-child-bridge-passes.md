# EXP-222 recovers the stable child across the coarse root jump

All 17 fine bridge points pass, including endpoint and midpoint Radau controls.
The child remains primitive and stable, the parent unstable, and section
identity stays `7/8` versus `14/16`.

EXP-223 will generalize the successful strategy by recursively bisecting only
failed or overlong child steps along the full 52-event route to the middle
returning-arm slice.
