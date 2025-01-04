butterfly
=========

Numerical Program / Physics / Applied Mathematics: An MPI parallel program for producing co-parameter 2 mappings of strange attractors

Codimension-2 parameter space has proven to be a rich source of information about the behavior
of chaotic strange attractors. As part of my thesis work, this MPI parallel program was used on
a cluster to create rich maps of co-parameter 2 space which yielded new finds on the behavior of 
such systems.

This is an MPI-based program that has been tested on linux clusters.

```bash
(find . -type f \( -name "*.c" -o -name "*.h" -o -name "Makefile" \) -print0 | while IFS= read -r -d '' file; do echo -e "\n# $file\n\n\`\`\`cpp"; cat "$file"; echo -e "\n\`\`\`\n"; done) > combined.md
```
