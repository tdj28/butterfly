# EXP-523 is executing on prax

Operational checkpoint, 2026-09-10 22:22 UTC. **No new scientific result yet.**

The two-step refreshed contact-path calculation is running on the existing
prax host. Its worker was observed alive after launch, the one-shot marker
is consumed, and new raw files are being retained. Do not launch it again.
The same frozen worker will run the complete raw-data audit after target
collection. Scientific outcomes have not been inspected at this checkpoint.

- Source commit: `eae6745d124c2fa59efc4eff337929e9ff71607d`.
- Immutable execution ref: `refs/heads/codex/exp523-prax-execution`.
- Manifest SHA-256: `e4c5b399f77dc8a23d069419866ff4a9787c9c7970b1e5336d6a19e3510ce4aa`.
- Review branch: `codex/exp523-refreshed-contact-path`, [PR 89](https://github.com/tdj28/butterfly/pull/89).
- Remote task directory: `/home/ubuntu/butterfly-research/exp523-refreshed-eae6745d124c`.
- Frozen checkout: that directory's `source/` subdirectory.
- Raw run: `source/artifacts/EXP-523/target-eae6745d124c/`.
- Marker: `source/artifacts/EXP-523/target-once.json` — consumed.
- Expected successful audit: `source/artifacts/EXP-523/primary-audit-01.json`.
- Worker PID at launch: `132437`; identify it by its exact command/task path
  before future process operations. Do not assume a stale PID remains owned.
- Operational log: `operational.log` in the remote task directory.

Both local sparse-checkout rehearsal and remote sealed startup passed: 202
bound source paths, 206 physically verified files, 27,647,289 source/input
bytes. The local rehearsal receipt is retained at
`artifacts/EXP-523/local-sparse-rehearsal.json`. The remote preparation records
`startup.json`, `preparation.json` and `launch.json` are retained outside the
raw run. Prax had 23,546,470,400 bytes free after preparation. Its managed
runtime is CPython 3.13.13, NumPy 2.5.1 and SciPy 1.18.0 from the locked
dependencies. Exact run binding is recorded before target outcomes.

Only already-public frozen source and compact inputs were fetched from
GitHub; no historical raw archive was uploaded. No paid Pro request or new
GPU rental occurred. Mac raw evidence remains untouched. Newly generated
EXP-523 raw evidence resides on prax; a second raw backup or public raw release
has **not** been established.

The target run and complete audit each have a separate six-hour deadline.
There are no automatic numerical retries. A failure or timeout preserves the
consumed attempt and its evidence. Read the
[frozen protocol](../experiments/EXP-523-refreshed-contact-path.md) and
[design review](2026-09-10-exp523-refreshed-path-design.md) for scientific gates
and the pre-execution root-identity fix.

Next: observe operational completion, inspect and independently replay the
compact decision only after the complete raw audit, then publish the result,
data-derived figures and manuscript update. Preserve failed predictors and
any accepted prefix. Continue toward actual grazing and the independently
identified symbolic partition; a sampled path alone will not verify Jones's
flow-level symbolic chain.

Release housekeeping: EXP-521 (PR 87) and EXP-522 (PR 88) were normally merged
to main after all four checks on their final heads passed. EXP-520 (PR 86)
has passing checks but still needs its overlapping release documentation
reconciled with current main. No numerical source was altered to merge them.
