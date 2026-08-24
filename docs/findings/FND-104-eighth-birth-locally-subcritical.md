# FND-104 — The eighth returning-arm birth is locally subcritical

Status: qualified by the combined EXP-316 and EXP-317 evidence

At solver-relative coordinates exactly `5e-13` above each solver's own
period-1536 real-`-1` event bound, DOP853 and Radau independently classify the
period-1536 parent as stable, with moduli `0.9996806831/0.9996553918`, and the
period-3072 daughter as strongly unstable, with moduli
`18.98363348/18.98308374`.

EXP-316 could not promote this classification because its preregistered
22,895-time-unit single-shot half-period nonclosure gate failed. EXP-317 keeps
that failure immutable and independently tests identity in the segmented
representation. Under tighter solver profiles, all-phase half-orbit separation
is at least `8.66424725e-6`, versus `3.34029e-10` cross-solver node RMS: a
separation/error ratio of `25,938.6`. Matching residuals stay below `2.13e-10`,
the two periods agree within `1.22e-7`, and the bound exact `3584/4096` section
identities remain valid.

The combined result qualifies a primitive, strongly unstable period-3072
daughter on the stable-parent side of event eight. The eighth local birth is
therefore subcritical. This is the first securely qualified non-supercritical
birth in the returning-arm ledger.

This finding does not resolve the seventh birth, prove a global period-3072
branch, establish attraction or basin measure, identify a ninth event, prove
universality, locate a TBA curve, or test a homoclinic connection.

FND-107 subsequently proves in the 4,096-step exact map that this event's
period-1536 parent sheet is the immediate daughter born at event seven. That
connection strengthens the eighth-rung interpretation without changing this
finding's local criticality gates.

Tracked receipts: [`../experiments/receipts/EXP-316.json`](../experiments/receipts/EXP-316.json)
and [`../experiments/receipts/EXP-317.json`](../experiments/receipts/EXP-317.json).
