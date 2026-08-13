# EXP-228 broad second-flip continuation is frozen

The 21-point distinct local curve now seeds 80 fixed-step pseudo-arclength
events in both directions. Explicit separation from the known returning arm is
retained as a per-point gate, preventing an unnoticed correction back onto the
old event locus.

Correction (EXP-229): this interpolation-based gate did not prevent source-arm
identity. Its apparent separation was source interpolation error; exact
same-coordinate correction is now mandatory.
