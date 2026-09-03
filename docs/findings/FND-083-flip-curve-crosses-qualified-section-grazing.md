# FND-083 — The exact flip curve crosses the qualified section grazing

Status: qualified locally by six invariant events and terminal Radau control

EXP-215 continues the period-6 real-`-1` flow-orbit locus from just below the
EXP-214 historical-section grazing to `c=6.83093274`. All six accepted events
retain seven extremum-partitioned historical phases and eight Barrio phases;
the terminal event independently recorrects under Radau.

This is direct evidence that the grazing is not a physical endpoint of the
flip locus. The seventh frozen fixed-step solve is inaccurate and therefore
does not identify any dynamical termination. It instead marks a numerical
continuation limit requiring adaptive arclength steps.

Evidence:
[`../experiments/EXP-215-period6-flip-through-grazing.md`](../experiments/EXP-215-period6-flip-through-grazing.md).
