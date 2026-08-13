# EXP-201 — Jones critical smoothing-scale audit

Status: completed; passed 94/104 against the frozen 70/104 gate

## Question

Is EXP-200's shallow second critical a reproducible finite-data object with a
stable smoothing-transition scale, or does its identity drift under step size
and nested trajectory support?

## Frozen design

The candidate selector retains the complete 104-point set for which all four
EXP-200 baseline variants return three branches and the high-smoothing variant
returns two at both RK4 steps. It changes no orbit data. EXP-201 then integrates
the same 8,192 initial conditions at `dt=0.01` and `dt=0.005`. Each run yields
two nested rectangular supports: the full grid and a deterministic every-other
grid containing 2,048 initial conditions.

At each candidate, step, and support, a fixed 25-bin oracle is evaluated at
seven logarithmically spaced smoothing values from `1e-6` through `1e-4` with
unchanged prominence, spread, coverage, and bootstrap gates. A candidate
qualifies only if all four step/support combinations contain a monotone
resolved three-to-two transition, their transition indices span at most two
ladder steps, their normalized second-critical locations span at most `0.03`,
and all nested return-pair gates pass. At least 70 of 104 candidates must
qualify.

Selection manifest:
[`../../experiments/manifests/EXP-201-smoothing-sensitive-candidate-selection.json`](../../experiments/manifests/EXP-201-smoothing-sensitive-candidate-selection.json).
Audit manifest:
[`../../experiments/manifests/EXP-201-jones-critical-smoothing-scale-audit.json`](../../experiments/manifests/EXP-201-jones-critical-smoothing-scale-audit.json).

## Claim boundary

A pass qualifies a finite-data scale transition and critical identity. It does
not decide which smoothing limit represents invariant topology, prove that the
critical survives infinite data at zero smoothing, or nominate a superstable
center. A failure prevents further signed-residual continuation under this
scalar oracle until the critical is reconstructed by a different representation
or regularization model.

Prepared artifact: `artifacts/EXP-201/candidates.json`, 164,041 bytes, SHA-256
`79065c539cd6c3ae16ea2ed6b5dc627e8a2322d6de950295f56f43d42b747ed0`.

## Administrative attempt

The frozen implementation and manifests were archived at clean pushed commit
`63d9ec2`. A secure RTX A4500 worker (`c00dukcvwhq2um`) was provisioned at
`$0.25/hour`, but the controller distinguished the owner's standing compute-
cost authorization from authorization to transfer this new derived artifact.
No file was transferred and no integration ran. The worker was terminated,
the account was verified empty, and the conservative cost bound is `<$0.02`.

After exact artifact authorization, the unchanged archive and candidate input
were hash-verified on secure RTX A5000 worker `d0gj1ov2cojzfb`. Both RK4
profiles completed without integration failure. The raw 1,261,031-byte receipt
was retrieved with matching SHA-256
`537699301785f34ad4e28c5ef682660851ea5e23af4ed7094b0164ac9078097c`.
The worker was terminated, the account was verified empty, and the conservative
total cost bound for this worker is `<$0.12`.

## Result

EXP-201 passes: 94 of 104 candidates qualify, exceeding the frozen minimum of
70. All 104 pass the nested return-pair gates. The ten failures arise solely
because at least one step/support reconstruction lacks a monotone resolved
three-to-two transition.

Of the 94 qualified candidates, 86 have identical transition indices across
all four reconstructions and eight span one ladder step. Their normalized
second-critical location spans have median `0.01031` and maximum `0.01679`,
below the `0.03` gate. Across 376 qualified reconstructions, the last-three to
first-two brackets are `4.6416e-5 -> 1e-4` in 344 cases,
`2.1544e-5 -> 1e-4` in 25, and `2.1544e-5 -> 4.6416e-5` in seven.

The shallow critical is therefore a qualified reproducible finite-data scale
object across the tested support and step limits. The result neither chooses
the invariant zero-smoothing topology nor establishes double superstability.
The next admissible step is a scale-ensemble reconstruction of the signed
critical-membership residual, retaining explicit representation and
regularization controls.

Compact receipt:
[`receipts/EXP-201.json`](receipts/EXP-201.json).
