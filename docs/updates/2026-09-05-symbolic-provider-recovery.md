# Symbolic verification: provider recovery

The owner requested continued recovery on 2026-09-05. This is an operational
successor, not a reinterpretation of the closed EXP-477 b53bfab attempt.
That attempt reached neither worker setup nor scientific inputs/outcomes.

## Diagnosis and correction

The old combined contract error does not identify its failing field. Its
provider response was not retained; we cannot reconstruct it retrospectively.
Separately, code inspection identified an API mismatch: direct lookup did not
request machine information, although qualification requires secure-cloud and
GPU-type evidence. Runpod's [GET Pod documentation](https://docs.runpod.io/api-reference/pods/GET/pods/podId)
states that `includeMachine` and `includeNetworkVolume` default to false.
The recovery explicitly requests both. This is not claimed to explain the
earlier combined disk/volume/port error.

The controller now retains allowlisted configuration observations before
validation and names each failing disk/volume/port field. Environment variables,
keys, unrelated resources, and full provider responses are excluded. Tests force
each failed field and verify that observations survive exact-owned teardown.
No safety threshold, numerical input, solver, endpoint, or analysis changes.

## Prospective recovery authority

Under the owner's standing sub-$30 authority and explicit request to find a
solution, authorize one fresh attempt from the pushed recovery source, using a
new output and private lifecycle namespace. Maximum spend remains $3, hourly
rate $0.50, lifetime 10,800 seconds, one secure A40, SSH-only, and no persistent
volume. The existing independent watchdog and verified teardown are mandatory.
These are local-controller limits, not a provider-enforced catastrophic cap.
There is no automatic second create. Preserve the old attempt and all tags.

Generate a fresh source-matched CPU control before execution. Qualification
and throughput must pass before the unchanged EXP-477 exploratory collection.
If a provider contract fails, retain observations and terminate; diagnose that
specific boundary before any successor. This attempt cannot license a claim
that Jones' flow itineraries or chain arrows have been independently verified.

## Remaining scientific goal

EXP-478 checked quadratic-map words, not Rössler itineraries. EXP-477 is an
exploratory search for usable centers, not the final symbolic test. Actual flow
cycles, a defensible partition, and continued chain connections remain the
required evidence. Infrastructure progress is not counted as scientific success.
