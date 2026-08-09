# Update — EXP-151 transverse UPO identity gates frozen

Before EXP-150 target execution, the downstream primitivity and deduplication
rule is fixed. It reuses the continuous-phase EXP-135 audit, including all
proper divisor closures, 512 phase samples, `1e-12` continuous phase
refinement, and the unchanged `1e-6` whole-orbit identity gate.

After EXP-150, only the source receipt path/hash and experiment identifiers may
be inserted into the immutable manifest. This prevents the number or identity
of recovered transverse families from being chosen after seeing the result.
