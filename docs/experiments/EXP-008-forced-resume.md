# EXP-008 — Local forced-kill and resume

Status: prospective infrastructure qualification
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
