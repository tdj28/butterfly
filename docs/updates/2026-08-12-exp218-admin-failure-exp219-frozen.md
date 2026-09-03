# EXP-218 fails administratively; EXP-219 preserves the child prediction

EXP-218 never reaches child evaluation because its inherited symmetric
auxiliary parent correction fails on the higher-`a` side. A post-failure audit
shows that the event and both lower-`a` parent offsets correct at all three
frozen slices.

EXP-219 freezes that one-sided tangent estimate. The predicted child side,
three held-out events, signed nullspace probes, primitivity, section identity,
stability exchange, and DOP853/Radau gates remain unchanged.
