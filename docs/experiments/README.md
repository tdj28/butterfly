# Experiment records

Every nontrivial run receives a committed `EXP-###-short-name.md` record. A run
does not count as evidence merely because it produced an attractive figure.

## Required metadata

```text
Experiment ID:
Date/time and timezone:
Operator:
Purpose and linked claim IDs:
Git commit:
Working-tree state:
Environment/lockfile:
Hardware:
Command or workflow:
Configuration file:
Random seed or deterministic initial conditions:
Input dataset IDs:
Output dataset and figure IDs:
Runtime:
```

## Required scientific record

1. **Hypothesis** - a falsifiable statement made before inspecting the result.
2. **Method** - equations, solver, tolerances, precision, transient and
   observation criteria, Poincaré section, classification method, and parameter
   sampling.
3. **Acceptance criteria** - numerical conditions that determine success,
   failure, or unresolved status.
4. **Results** - numerical summaries and artifact paths, including failures.
5. **Validation** - tolerance, horizon, precision, resolution, solver, and basin
   comparisons appropriate to the claim.
6. **Interpretation** - what the experiment changes in the claim ledger.
7. **Limitations and next action** - remaining uncertainty and the next decisive
   test.

Large generated artifacts should not be committed blindly. Record their schema,
size, checksum, storage location, and regeneration command.
