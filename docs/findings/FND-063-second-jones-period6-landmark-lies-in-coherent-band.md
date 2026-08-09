# FND-063 — The second Jones period-6 landmark lies in a coherent band

Status: qualified discovery-domain result; continuation identity remains open

EXP-191 prospectively samples 40,401 parameter pairs around Jones's exact
period-6 landmark `(a,b,c)=(0.215,0.2,7.6)` using the qualified Float64 GPU
atlas kernel. The target-word-blind classifier places the exact anchor in an
eight-connected 981-pixel period-6 component spanning
`a in [0.2145,0.21555]`. No numerical failures occur.

Unlike the failed first-landmark Floquet-zero neighborhood, this gives a
coherent stable-window domain around the independently observed three-branch
return map. The component reaches both sampled `c` boundaries at `7.4` and
`7.8`, so EXP-191 does not establish its complete extent. Eight-connected
raster adjacency is also not periodic-orbit continuation and cannot show that
the two published period-6 landmarks belong to one flow-orbit family.

The immediate prospective successor expands the atlas through both landmarks.
Only after that raster test may identity-safe cycle correction and direct
two-critical residual solving begin.

Evidence: [`../experiments/EXP-191-jones-second-period6-window-atlas.md`](../experiments/EXP-191-jones-second-period6-window-atlas.md).
