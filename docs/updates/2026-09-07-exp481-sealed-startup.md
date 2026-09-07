# EXP-481: the isolated worker now passes its startup checks

The worker can import the numerical and analysis components from an exact-file
bundle without depending on the development checkout. All nine startup controls
pass, and every worker's cleanup is verified. No Rössler trajectory was generated
and no symbolic claim changed.

PR #41 is already merged into `main` at
`059d921c2df8488ee0460f13c75d0ba664193e66`; its complete-grid analysis is reused.

## What the startup checks establish

The builder copies 18 explicitly listed files, including a minimal package
initializer. The numerical modules are copied unchanged. This avoids executing
the development package's broad top-level imports, including the legacy
return-map API. The runtime contract hashes the copied files and the local
NumPy/SciPy dependency trees, records the exact interpreter, and binds a single
canonical process environment. This host has 2,872 bound dependency files.

The guest runs with `-I -S -B -X utf8=1`: no user/working-directory import path,
site initialization, editable-install hooks or bytecode writes. Its parent-loss
guard is installed before scientific imports. Missing, changed or extra source
files and environment variables fail closed. The actual Python-visible
environment is checked before and after imports, including the explicitly set
macOS `__CF_USER_TEXT_ENCODING` value. It is not inferred from requested values.

File-backed numerical imports are checked before their loaders run and rechecked
after startup. A host-current-directory `numpy.py` and `sitecustomize.py` control
cannot replace the imports. The success receipt records 776 observed import
entries, their locations and hashes, with namespace directories distinguished
from files. The standard library is checked against the actual interpreter's
directory; a forged root such as `/` is rejected.

These are integrity checks for trusted research code, **not OS confinement**.
The standard library and native system loader/libraries remain host trust.
The builder does not prove a remote Git freeze or an adjudicated review, and
the worker cannot authenticate its own initial loader: its controller must
independently check the launcher and contract against later authorization.

## Preserved controls and incident

The first bundle (`sealed-startup-01`) was a build-only probe. The first actual
control run (`sealed-startup-02`) failed on SciPy's vendored namespace package.
That run remains intact. The fix permits only a single, correctly named,
non-symlink namespace directory backed by inventoried files; sibling, foreign,
multiple-location and alias cases are rejected. No broad import exemption was
added. Negative controls also check the expected failure reason, so an unrelated
startup error cannot masquerade as successful rejection.

Runs 03 and 04 passed and remain preserved. Run 05 exercises the final tightened
runtime-root checks. Its nine cases are correct startup; missing, wrong and
extra environment settings; missing, extra and changed source files; wrong
contract digest; and refused target execution. Even a successful startup receipt
does not authorize `--mode execute`.

The [public summary](../experiments/receipts/EXP-481-sealed-startup.json) binds
the final local receipt and source hashes: 273 files, 7,455,417 bytes excluding
the receipt. Raw evidence is local; its hashes are not a public data release.
Reproduce into a fresh directory:

```sh
PYTHONPATH=.:python .venv/bin/python -B scripts/qualify_paired_startup.py \
  --output-dir artifacts/EXP-481/sealed-startup-NEW
```

This exercises real local processes and requires process-inventory access for
the supervisor. There are 28 new tests, including actual worker startup and
execution refusal, forged roots and narrow namespace handling.
The full local suite passes **1,547 tests**, with one older Linux-only skip on
macOS, using host access for the real process controls.

## Remaining work

The startup worker deliberately has **no target dispatcher yet**. Connect the
raw capture-input audit and existing qualification/collection/replay/analysis
components to a source/input/review-bound controller. Add their final files to
the sealed closure, then qualify that exact complete production path. The
current 30-second control guard is for startup tests, not the later research
phase deadlines. Obtain and adjudicate the compact design review, push the exact
executable freeze, and only then run the fixed experiment.

The research-integrity playbook directly motivated the isolated deployment and
actual-environment checks. It does not turn this software milestone into Jones
verification. No paid review, GPU rental or upload occurred. The unresolved
Runpod create still has no assigned ID or exact task-name inventory match;
its identity-checked watchdog is alive and remains in place.
