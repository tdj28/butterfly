# Require a consistent managed Python distribution in release CI

After the EXP-519 last-bit norm assertion was corrected, both Python 3.13
jobs passed at `048955c347adec72fb68e3e2396fd221dcbb1b59`. Python 3.12
still timed out in the unchanged isolated startup checks:

- Run 34515504556, job 102999855389: one 240-second EXP-519 startup timeout;
  3,054 other tests passed in 3,232 seconds.
- Run 34515498584, job 102999755744: 240-second EXP-518 public replay and
  EXP-519 startup timeouts; 3,053 other tests passed in 3,402 seconds.

The logs show that `uv sync` selected **Ubuntu's CPython 3.12.3 at
`/usr/bin/python3.12`**, despite setup-uv's Python-version request. The other
matrix arm uses a uv-managed interpreter. The prior zero-IVP profile shows
heavy recursive ancestry replay and JSON decoding; interpreter and runner
performance matter for this bounded startup. The distribution difference
is observed; it is not yet proven to explain every timing variation.

The workflow now sets `UV_MANAGED_PYTHON=true` for both matrix arms. The
installed uv CLI documents this as requiring uv-managed Python. A small
fail-closed check verifies the actual base interpreter lies in setup-uv's
managed installation root and matches the requested matrix version, then
records its actual version and compiler. This prevents a silent system
fallback. Unit tests reject wrong versions, system/sibling prefixes and
missing configuration.

No test is skipped or filtered; no timeout, historical source, numerical
threshold, receipt or consumed attempt is changed. The full exact-head
matrix must pass before merge. This is a CI-environment correction to test
the same research code; it is not a claim that the original Ubuntu-system
Python jobs passed. Live Linux validation remains pending until CI completes.
