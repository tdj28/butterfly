# EXP-174 blind Figure 6 landmark audit frozen

Date: 2026-08-07

The ten approximate parameter landmarks transcribed from Jones Figure 6 are
now bound into the first post-audit computation without expected labels. Two
initial states, two transient lengths, and DOP853/Radau parity are frozen.
Consistently unresolved coordinates pass the numerical reproducibility gate but
remain scientifically unresolved; no hidden local search is allowed.

This is the first non-circular step toward the symbolic program. It classifies
the printed landmarks only. DEC-014 still requires dense-cloud partition
inference before any corrected periodic orbit can be assigned a Jones word.

## Execution result

The strict gate fails and is preserved. All 20 qualified-profile cases agree
between DOP853 and Radau, yielding eight periodic landmarks with periods
`5,6,8,14,6,5,14,14` and two unresolved landmarks. One initial condition at
the eighth landmark changes from unresolved after 800 transient units to
period 14 after 1600; this sole early/late mismatch fails the experiment and
records delayed capture. No symbol or arrow claim is promoted.
