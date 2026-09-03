# FND-091 — The returning-arm period-12 flip is locally supercritical

Status: qualified local numerical finding

At fixed `(b,c)=(0.2,7.625815600403827)`, the exact period-12 real-`-1` event
qualified by EXP-232 and represented segmentwise by EXP-237 produces a
primitive period-24 branch. EXP-238 switches both tangent signs with exact
`28/32` section identity, and EXP-239 continues one sign away from the event.

EXP-241 supplies the decisive near-birth stability exchange. At an `a` offset
of `-3.2235e-10`, independent segmented DOP853 and Radau calculations classify
the period-12 parent as unstable (`-1.00112519/-1.00112474`) and the period-24
child as stable (`+0.99549815/+0.99549817`). The child is primitive by
half-period nonclosure and both section counts. This qualifies the sampled
period-12-to-24 flip as locally supercritical.

The result strengthens the Jones-periodicity-hub mechanism by extending the
exact returning-arm cascade one rung deeper. It does not establish a full
period-24 sheet, a TBA or double-critical identification, paired shrimp
boundaries, or global parameter-plane topology. EXP-240 independently finds
the continued child strongly unstable farther away, so a subsequent
period-24 stability loss is now the next orbit-defined target.

Evidence:
[`../experiments/EXP-241-jones-period24-near-event-qualification.md`](../experiments/EXP-241-jones-period24-near-event-qualification.md).
