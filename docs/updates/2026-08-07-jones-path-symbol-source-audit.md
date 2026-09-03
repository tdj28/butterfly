# Jones path and symbol source audit completed

Date: 2026-08-07

The original PDF has now been inspected at figure resolution rather than only
through extracted text. Figure 2 defines `L1` and `L2` geometrically and draws
horizontal and vertical examples, but prints no exact path equations or
endpoint coordinates. The qualified fixed-`a=0.1798` cascade is therefore an
explicit `L2`-like reconstruction, not recovered historical code.

Figure 6 has been converted into a machine-readable source target: 23 words
through period seven, ten state-space/symbol-matched `p -> p+1` transitions,
one visual-only transition, three explicit lower-period relationships, and ten
parameter landmarks. All eleven `p -> p+1` arrows use the same zero-insertion
grammar. The source still lacks a reproducible return-map partition, so none of
those words has yet been revalidated dynamically.

The audit also exposes a useful `L1` boundary. The exact regular
small-equilibrium Hopf intersection at `c=10.3084` is
`a=0.0018649211449047556`, outside Figure 2's displayed `a>=0.1` range. The
visible horizontal segment should therefore be tested as a post-Hopf segment
separately from a full endpoint-matched path.

DEC-014 now freezes the partition-reconstruction acceptance order: dense
transient/saddle data define critical intervals before an independently
corrected target cycle is labeled. Next: implement those controls and classify
the ten approximate landmarks without expected labels; freeze the two `L1`
controls before computing either path.
