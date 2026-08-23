# EXP-318 freezes a high-precision seventh-birth decision

The eighth-birth methodology exposed a representation-scale problem that also
explains why EXP-299 stopped short: DOP853 and Radau agree that the primitive
period-1536 daughter is strongly stable, but disagree about which side of
`-1` contains the nearly neutral period-768 parent at one shared Float64
coordinate.

EXP-318 avoids classifying that `3e-5` solver split. It binds the passed
8,192-step RK4 3/8 augmented event and the failed-but-qualified EXP-299 source,
then recomputes the parent spectrum using two independent fourth-order
tableaux in 50-digit arithmetic with three resolution levels. The event-side,
convergence, cross-tableau, signal/error, orbit, neutral, cyclic, and
characteristic gates are frozen before execution. Either stability-exchange
direction may pass; a same-side or unresolved result fails.

This is the shortest decisive successor for the only unresolved birth among
the eight exact returning-arm flip events. It uses local CPU arithmetic and
incurs no RunPod cost.
