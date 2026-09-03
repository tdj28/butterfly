# EXP-211 freezes identity-constrained recovery after EXP-210

EXP-210's 16 failed cells are exact double-covered-parent roots, often isolated
between valid stable children. EXP-211 therefore changes root selection, not
the scientific surface grid or acceptance thresholds.

Each cell receives an independent seed interpolated first across the seven
EXP-209 physical offsets and then across its three qualified `c` anchors.
Half-period nonclosure is mandatory before a root can be accepted. Only if the
independent seed collapses are the failed-surface cell and passing-neighbor
interpolation tried; the root with greatest nonclosure is selected. The full
124-point, 31-fit, six-Radau surface gate remains intact.
