# EXP-229 retracts the distinct second-flip claim

All 21 exact-coordinate DOP853 comparisons and three Radau controls identify
EXP-227 with the known EXP-217 returning arm. The maximum `a` difference is
`1.46e-14`; the former `5.60e-7--5.85e-7` gap is entirely the error from
linear interpolation of a curved, sparsely sampled arm.

The raw EXP-223, EXP-226, and EXP-227 orbit calculations remain valid. Their
topological interpretation changes: the constructed offset path recrosses the
same returning flip locus, rather than meeting a new shrimp boundary. FND-089
is retracted, FND-088 is corrected, and the manuscript/figure are being
updated. Future branch-distinctness gates must use fresh same-coordinate event
corrections or a certified interpolation-error bound.

The corrected four-panel Figure 22 is 640,299 bytes with SHA-256
`4d57c1fa4add5b143a7b0edb8b61467d97a6eefa9facd41bf3a3c762d5b9ea17`.
The rebuilt manuscript has 42 pages and 22 figures, no LaTeX warnings, and
SHA-256
`31a75b9a0595c79bc5a7ef8a8653201baa96236720b80e455066c761f7665ccf`.
All 287 tests and the 10/10 reference contract pass.
