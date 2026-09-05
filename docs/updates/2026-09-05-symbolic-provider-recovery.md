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

## First recovery result and specific repair

Source `4517f1388924bd4498c5c07787a41ee4a08a5508` passed both CI Python
versions and a fresh CPU reference. Worker `fcz550glgfl8a0` returned the
requested disk, zero volume, SSH ports, secure A40 and `costPerHr=0.49`, but
omitted the `interruptible` field entirely. The contract rejected that omission
before source upload. Direct absence, inventory absence and local watchdog
retirement were verified; the [failure receipt](../experiments/receipts/EXP-477-recovery-4517f13-summary.json)
preserves this closed attempt. The observed rate is not an invoice.

The specific repair uses Runpod's [GraphQL schema](https://graphql-spec.runpod.io/):
when REST omits the field, query only the exact owned pod's `id`, `name`, and
`podType`, require matching ownership and explicit `RESERVED`. Missing, spot,
bid, background, or conflicting status fails. An explicitly true REST value
cannot be overridden. The query was rehearsed read-only against the deleted
owned ID and returned null, confirming both schema acceptance and absence.
Tests cover every enum, missing values, conflicting REST evidence and wrong ID.
The watchdog repeats the same confirmation; teardown does not depend on it.

Authorize one fresh operational successor under the same $3/$0.50/hour/3-hour
bounds after the tested source is pushed and a fresh CPU reference passes.
This is a diagnosed pre-outcome API-schema repair; no scientific review cycle
or numerical change is introduced, and no prior attempt is reused.

## Second recovery: configuration passes; missed SSH call site

Source `8a426cedd5c66f0e2fbaa82f3047c6540a2d6b24` obtained explicit
`RESERVED` evidence for owned worker `kh4grqnntadv2c` and qualified the
provider contract at $0.49/hour. The SSH consumer still called the old raw
validator, however, so it rejected the omitted REST field before connecting
or uploading. This was an executor oversight, not a provider or scientific
failure. Target collection did not start; exact teardown and watchdog retirement
passed. The original local workload and lifecycle records remain unchanged.

The one-line consumer correction uses the same observed-contract function as
provisioning and the watchdog. A regression executes the real `connect_owned`
path with a provider-shaped response and pinned synthetic SSH; all production
contract call sites were searched. Authorize one fresh successor within the
same bounds after pushed source and CPU reference; no old authority or namespace
is reused. Three attempts in this recovery turn are the current maximum.

## Third recovery: ambiguous provider error; CPU fallback

Source `27a9bfd6ba65c12dacd29f99d77e24319754fad0` passed both CI versions
and its fresh CPU reference. The sole create returned HTTP 500 without an ID.
Subsequent inventory checks found no exact task-name match, but a server error
is not authoritative proof that creation was rejected. The local watchdog
continues reconciliation; no duplicate create is permitted and no confirmed
teardown is claimed for this unresolved transaction.

To make progress without another rental, a target-free local benchmark uses
the existing CPU sprinkler reference at 8192 seeds and both frozen steps on
the known qualification anchor. It preserves raw event arrays and timing.
No target candidates or desired words are opened. An extrapolation to 551
cases is explicitly a planning estimate, not a measured campaign duration.
This benchmark does not change or claim execution of EXP-477's CUDA protocol.

## Working solution: CPU collection is running

[EXP-479](../experiments/EXP-479-cpu-symbolic-center-pilot.md) now runs the
unchanged numerical search locally from an isolated frozen checkout. The first
two candidates have completed both profiles with raw checkpoints retained.
The exact adapter/control qualification passed, and a persistent local service
plus 30-minute thread follow-up removes dependence on a continuously open chat
turn. This is actual target collection, not another infrastructure-only test.
No symbolic-dynamics conclusion is claimed before analysis and successor tests.
The ambiguous Runpod transaction remains separately monitored without another
rental; its ambiguity is not hidden by the successful CPU fallback.
