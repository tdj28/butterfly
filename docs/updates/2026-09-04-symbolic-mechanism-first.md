# Put the symbolic explanation at the center of the paper

Date: 2026-09-04. Branch: `codex/center-symbolic-mechanism`.

## What was still wrong

Restoring the chain did not fix the manuscript's emphasis. It remained a late
section, while the title, abstract, numerical results, and next-step ordering
gave much greater prominence to cascades and homoclinic calculations.
The user clarified that the symbolic explanation is one of the paper's most
important contributions. The narrative and research priorities now reflect that.

The central question is specific: does changing reinjection insert the
predicted inner return into an orbit's word, connecting period `p` to `p+1`
and helping explain the shrimp chains? A deeper period-doubling cascade,
`p -> 2p`, cannot answer that question on its own.

## Manuscript changes

- The title is now *Testing a Symbolic Explanation for Periodicity Hubs in
  the Rössler Flow*. The author line and PDF author metadata remain blank.
- The abstract and introduction lead with the reinjection-to-word prediction,
  rather than a list of numerical achievements.
- The symbolic section now precedes methods and results. Section 3 begins
  on page 4; the chain is Figure 2 on page 6, previously Figure 10 on page 14.
- The results begin with the locally qualified operational alphabet and the
  failed exact-landmark word test, followed by the supporting computations.
- The claims table starts with the status of the symbolic chain. The
  conclusion identifies one independently defined, held-out `p -> p+1` test
  as the next decisive scientific advance.
- All 34 figures remain: ten in the 16-page main article and 24 in the
  supplement. The complete PDF remains 63 pages. Figure assets, receipts,
  source transcription, bibliography, and numerical results are unchanged.

## Evidence boundaries

An independent framing review identified an important ambiguity in the old
abstract's claim to support a local account of the pattern. The saddle-lobe
result at `c=20`, period-6 studies near `c=6–8`, and initial homoclinic
candidate at `c=10.3084` are separate calculations. They have not been joined
into one verified `CDw -> CD0w` connection. The new text says so explicitly.

The source chain remains an attributed reproduction target. Local alphabet
qualification is not a generating-partition proof or validation of the 23
critical words and arrows. The landmark failure does not refute all nearby
centers; conversely, strengthening the emphasis does not promote any open
claim to an established result.

## Research priority

The [next-step list](../next-steps.md) now puts a bounded symbolic pilot ahead
of further homoclinic refinement, subject to reproducible inputs and valid
partition/center measurements. It must locate a center without using the
desired word, encode the independently corrected orbit, and compare the
measured extra return with the predicted insertion. Unresolved measurements
must stop the test, not be tuned into agreement.

Homoclinic accuracy remains necessary for claims about the global organizer.
All existing failures, acceptance gates, and deferred manifests remain in
force. No new numerical experiment or paid job was run for this revision.

## Verification

All 791 tests pass on Python 3.13.11. The presentation tests now protect the
symbolic section's position before methods and results, as well as the blank
author and source-attributed diagram. The citation/figure check passes all
16 cited bibliography entries, 15 required citations, and 34 figures.

Independent review prompted three wording corrections: no unsupported exact
landmark-to-word association in the abstract; genuine doubling is not
described as simply repeating a parent; and the reading guide counts the
symbolic diagram within, not in addition to, the ten main figures.

The final LaTeX build has no warnings or overfull/underfull boxes. All 63
pages were rendered and visually reviewed, with the title and chain inspected
at higher resolution. The local PDF SHA-256 is
`181d90fb41ccccbe87bdaddac371a9faaf8622aff0b21fad4efaeab1ccd72460`.
The frozen transcription and chain PNG retain their previous hashes.

## Publication status

This is a local PDF and source revision. The earlier
`manuscript-symbolic-v1` GitHub draft still contains the previous layout;
it was not replaced or published. Public PDF publication remains pending
approval. Existing published research releases are unchanged.
