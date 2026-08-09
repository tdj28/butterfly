# FND-065 — Historical period-6 flow orbits have eight Barrio-section phases

Status: qualified systematic representation result

EXP-194 selects 65 pixels from the isolated second-landmark component without
using symbols or criticals. Fifty-eight independently reproduce period 6 on
the recovered historical half-plane, shoot to stable flow orbits, and pass all
closure and Floquet gates. Every one of those 58 orbits intersects Barrio's
published small-equilibrium x-plane with positive `dx/dt` exactly eight times
per flow period.

Consequently, “period 6” is not a section-independent count of return-map
phases. It is the fundamental recurrence count on the historical section used
by the atlas and Jones reconstruction. The same flow orbit is an eight-phase
cycle on the Barrio section. A direct Barrio z-return-map test must therefore
compare both critical points against all eight phases, not truncate the cycle
to the last six crossings.

This explains the sole common EXP-194 failure and exposes a flaw in the
earlier exploratory second-landmark diagnostic, which retained only six
Barrio crossings. None of the corrected orbit data or Floquet conclusions is
altered. EXP-195 prospectively changes only the expected Barrio-section count
to eight and passes all 58 otherwise-qualified candidates.

Evidence: [`../experiments/EXP-194-local-corrected-second-component-cycles.md`](../experiments/EXP-194-local-corrected-second-component-cycles.md).
