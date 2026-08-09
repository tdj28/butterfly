# Jones Figure 2 path and Figure 6 symbol transcription

Date: 2026-08-07

Source: Jones, *Topological origins of a bi-parameter periodicity hub for the
Rössler attractor*, arXiv:1201.4343v1, pages 2 and 4. Source PDF SHA-256:
`54b2a35bcfe50c5c2dc2f8ac1f3d3f98acbb2991dab7bc6e66cf61dc4b5ffb6f`.
The public arXiv source archive has SHA-256
`c7b38955cdfb5954c89dc5e86fc5a312ff9c2626a6e712173e8c58bcd09115bb`.

Machine-readable transcription:
[`../../experiments/source-transcriptions/jones2012-figures-2-and-6.json`](../../experiments/source-transcriptions/jones2012-figures-2-and-6.json).

## Result

The paper supplies enough information to define a faithful modern `L2`-like
test and a finite Figure 6 validation target, but it does **not** publish exact
historical `L1`/`L2` parameterizations or a complete reproducible symbolic
partition.

Figure 2 draws `L1` horizontally near `c=10` and `L2` vertically near
`a=0.18`. The surrounding text defines the intended class of slices
geometrically: begin at the Andronov--Hopf bifurcation or on the period-1
family created after it, remain in the two-branch regime, and terminate at the
homoclinic point on `TTL23`. No equations, arclength coordinates, sampled
points, or exact endpoints for the named lines are printed. The hub itself is
reported only approximately as `(a,c)=(0.1798,10.3084)`, whereas the schematic
red endpoint is drawn near `(0.18,10)`.

The current fixed `(a,b)=(0.1798,0.2)` computation is therefore an explicit,
endpoint-matched `L2`-like reconstruction, not recovered historical code. Its
small-equilibrium Hopf start at `c=0.5192306256940273` and four exact flips
through a stable period-16 child are independently qualified.

## `L1` consistency boundary

At the reported hub height `c=10.3084`, analytic inversion of the regular
small-equilibrium Hopf condition gives
`a=0.0018649211449047556`. At the drawn height `c=10`, it gives
`a=0.001980601948535982`. Both are far left of Figure 2's displayed
`a>=0.1` range. Consequently, the visible horizontal `L1` segment cannot begin
at that exact small-equilibrium Hopf point. It can consistently be read as a
clipped post-Hopf segment on an already existing period-1 family, and the
Figure 2 caption uses that weaker wording. It cannot yet be advertised as an
exact Hopf-to-homoclinic line without a new operational definition or the old
code.

This is a clarification, not a rejection of Jones's finite-ordering result.
The appropriate modern test is to declare both candidate `L1` definitions in
advance---the visible fixed-`c` segment and the full endpoint-matched path---and
retain any disagreement.

## Figure 6 validation target

Figure 6 and its surrounding text define `C` as the critical point retained on
the two-branch/unimodal side and `D` as the second critical point available on
the three-branch/bimodal side. Branch symbols `0`, `1`, and `2` are used. The
figure prints 23 words through period seven, ten state-space/symbol-matched
`p -> p+1` arrows, one visual-only arrow (`CD0111 -> CD00111`), three explicit
connections involving `C1`, `C2`, and `C21`, and ten approximate parameter
landmarks. Those objects are transcribed verbatim as symbols and numbers in the
JSON target.

The arXiv source audit also closes a possible recovery route. Figure 6 is the
author-supplied raster `6.png`, SHA-256
`264599bca7914db914bdaa32f6fbde7ea7eda325878f693185d32997a78943cf`,
with dimensions `823 x 534`. Its pixels agree exactly with the image embedded
in the PDF (zero differing pixels). There is no concealed vector version or
higher-resolution arrow geometry in the archive. Several gray-box attachments
are visually continuous, but upper-middle and lower-right routes are crowded;
therefore the machine transcription deliberately retains the ten coordinates
as an unordered source target instead of inventing a complete word-to-box
association. A recovered old plotting source could supersede this limitation
through a versioned transcription update.

This later evidence is stored separately in
[`../../experiments/source-transcriptions/jones2012-figure6-asset-audit.json`](../../experiments/source-transcriptions/jones2012-figure6-asset-audit.json).
The original Figure 2/6 transcription remains byte-for-byte frozen at SHA-256
`6a5aba797473d40db9197d7a2ebe51195193f888613800584f406742376581da`
because EXP-174 binds that exact target. The asset audit extends provenance; it
does not rewrite an executed experiment's input.

Every printed `p -> p+1` arrow obeys one simple finite grammar: insert `0`
immediately after `CD`. For example, `CD01 -> CD001`. That is now an auditable
source claim rather than a hand-read future figure.

The paper does not print the Poincaré-section equation, invariant return-map
domain, orientation, coordinate threshold, critical-point uncertainty, or a
complete partition boundary that turns a computed orbit into one of these
words. The transcription is therefore a target for reproduction, not evidence
that the words or arrows are dynamically correct.

## Execution consequence

1. Use the qualified fixed-`a=0.1798` path as `L2-like`, with the historical
   qualifier retained.
2. Freeze two `L1` controls separately instead of guessing one historical
   equation.
3. Reconstruct the return map and partition independently from orbit data.
4. Verify all 23 words and 11 printed arrows, preserving the visual-only arrow
   as a separate, weaker gate.
5. Only then compare the finite Rössler permutations/kneading data with a
   logistic-map control and search for the first disagreement.

DEC-014 now freezes the non-circular validation rule: infer the return
partition from dense transient or saddle data before assigning any independently
corrected target cycle a word.

The audit script
[`../../scripts/audit_jones2012_transcription.py`](../../scripts/audit_jones2012_transcription.py)
checks source hash formatting, word/period consistency, the zero-insertion
grammar, transition periods, landmark count, and the independent analytic
`L1`-height Hopf calculation. The separate
[`../../scripts/audit_jones_figure6_asset.py`](../../scripts/audit_jones_figure6_asset.py)
checks the source-archive and raster-asset record without mutating that frozen
transcription.
