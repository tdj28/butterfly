# EXP-200 freezes the lower-c high-support discriminator

EXP-199 does more than miss a center: its first residual crosses zero while the
second remains positive and declines toward the lower-`c` eligibility edge.
EXP-200 targets that edge using 168 already-qualified stable orbits, selected
deterministically from EXP-198 without changing their states or periods.

The new scan quadruples the initial-condition ensemble to 8,192 while retaining
the Barrio section, `z` map, capture rule, oracle matrix, two RK4 steps, and all
three direct-center thresholds. It asks whether the lower-`c` loss of a robust
second critical is merely support-limited and whether the second signed
residual can reach zero before that loss. The 264,429-byte input is prepared
and hash-bound; no new return-map result has been inspected.
