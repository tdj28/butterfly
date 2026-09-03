# EXP-468: seventy-sixth homoclinic point and new research branch

The merged research history now continues on
`codex/world-class-shrimp-research`. The new `main` branch is published at the
remote, and the old remote `master` is intentionally retained until GitHub's
default branch can be changed in an authenticated session. The repository
README was rebuilt at commit `5f484ade9b16f20ee895e54dd49a62842624d040`
as a current, figure-rich research landing page and passed all 401 tests,
numerical verification, citation checks, and local-link checks.

From that clean commit, EXP-468 passed every prospectively frozen gate in two
evaluations, adding the seventy-sixth qualified point to the Jones homoclinic
continuation:

```text
(a, c) = (0.17985430934117327, 10.316968440239535)
maximum block defect = 3.1997883185634873e-9
minimum singular value = 8.072649888863062e-10
node-boundary margin = 0.9938912216178979
```

The raw receipt is 78,608 bytes with SHA-256
`1a1b442d0ae81d815931f69737f9670f148c911b20503893be815271fb467b9a`.
The chain now contains 73 gauge-aligned pseudo-arclength roots and 76 qualified
roots overall. Fifty-nine tangent-recomputed outgoing steps after EXP-408
remain smooth and interior. EXP-403 remains the sampled local `a` minimum and
the closest root to the historical `a=0.1798` section. EXP-468 increases that
section gap to `5.430934117328645e-5`, so it strengthens the computed nearby
homoclinic curve without recovering the printed coordinate or proving that a
later branch cannot return.

The minimum singular value is `1.61x` the unchanged `5e-10` floor. EXP-469 is
therefore frozen prospectively from the exact EXP-467/468 receipts at the same
normalized step, with both parameters unconstrained and every numerical and
scientific gate retained. A pass adds the seventy-seventh point; a failure is
preserved. Global nonintersection, uniqueness, topology, and validated
existence remain open.
