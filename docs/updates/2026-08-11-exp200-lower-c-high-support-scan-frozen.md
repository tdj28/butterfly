# EXP-200 exposes a smoothing-sensitive lower-c critical

EXP-199 does more than miss a center: its first residual crosses zero while the
second remains positive and declines toward the lower-`c` eligibility edge.
EXP-200 targets that edge using 168 already-qualified stable orbits, selected
deterministically from EXP-198 without changing their states or periods.

The new scan quadruples the initial-condition ensemble to 8,192 while retaining
the Barrio section, `z` map, capture rule, oracle matrix, two RK4 steps, and all
three direct-center thresholds. It asks whether the lower-`c` loss of a robust
second critical is merely support-limited and whether the second signed
residual can reach zero before that loss. The 264,429-byte input is prepared
and hash-bound before execution.

The scan fails its strict recovery gate: only 10 and 9 candidates are eligible
at the two steps, with 8 agreeing across steps against a minimum of 40. The
reason is not inadequate return-pair count. Four baseline variants unanimously
return three branches at both steps for 125 candidates, while the high-
smoothing variant alone reduces 104 of them to two at both steps. The feature
is therefore supported but scale-sensitive, and no topological branch loss is
claimed.

No strict survivor passes a direct-center gate; its second residual remains
positive. The next experiment must measure the smoothing transition itself
under nested support and step changes before the residual search continues.
The secure A4500 result was retrieved with matching hashes for less than
`$0.11`; the worker was terminated and the RunPod account was empty.
