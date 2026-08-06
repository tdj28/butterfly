# EXP-008 — Local forced-kill and resume

Status: passed local infrastructure qualification
Manifest: `experiments/manifests/EXP-008-forced-resume.json`
Claim target: local half of P1-004

## Purpose

Exercise a real operating-system process interruption during a nontrivial
Lyapunov-resolved tile, rather than relying only on simulated temporary files.
The owned child worker is killed during computation, its incomplete state is
inspected, and the identical tile is restarted with `--resume`.

## Command

```sh
.venv/bin/python scripts/qualify_forced_resume.py \
  --manifest experiments/manifests/EXP-008-forced-resume.json \
  --output-root artifacts/EXP-008 \
  --tile-count 2 \
  --tile-index 0 \
  --kill-after 0.5 \
  --receipt artifacts/EXP-008/forced-resume.json
```

## Acceptance criterion

- the first worker is still active when killed;
- no completion marker exists after the kill;
- restarting the exact source-bound tile succeeds;
- the completed result and marker hashes verify; and
- the receipt is produced from a clean source commit.

This qualifies the local restart path only. The same gate must pass on the
eventual remote container/storage stack before interruptible GPU production.

## Result

The clean run from commit `7704ab4acd479f8a80b79ef4c30922b27b6447c6`
passed:

- the first worker was killed after 0.5 seconds with return code `-9`;
- no completion marker existed after the kill;
- the restarted tile completed point indices 0 and 1 in 5.47 seconds;
- both completed rows carried full-spectrum chaotic classifications;
- result SHA-256:
  `97b7fc00628286ac193c2d44c52bb681be1f63c90277cf693e224d697601f272`;
  and
- completion-marker SHA-256:
  `12c0bb76b9d5939688d55b1d76c46c1143a3aeb5f51aa45ac03544a9d6831017`.

The checked-in receipt is
[`receipts/EXP-008.json`](receipts/EXP-008.json). This closes the actual local
process-kill requirement. Remote container/storage repetition remains open.
