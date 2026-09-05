# Restore the symbolic mechanism to the main manuscript

Date: 2026-09-04. Branch: `codex/restore-symbolic-chain`.

## Why the chain was missing

The readability rewrite at `ef7390f` shortened the main topology section from
227 to 44 lines and moved its detailed numerical history into the symbolic
supplement. Even before that rewrite, the manuscript contained no symbolic
chain figure: it only promised a future computed unfolded-spiral diagram.
The result was a presentation omission, not a finding that the original chain
had been disproved.

That omission matters. Jones's proposed explanation connects the parameter
spiral, reinjection geometry, and a specific change in a symbolic itinerary.
A manuscript about the explanation should display that construction while
clearly identifying which parts have and have not been independently tested.

## Changes

- The main article now explains `C`, `D`, branch symbols `0/1/2`, cyclic words,
  and the difference between a return count and physical flight time.
- The worked source example `C100 -> C200 -> C1000` explains the proposed
  extra inner return. The finite critical-word rule `CDw -> CD0w` is shown
  separately from period doubling.
- A generated source-chain diagram retains all 23 words through period seven
  and all 14 transcribed relationships: ten source-matched period-increment
  arrows, one visual-only arrow, two lower-period third-branch connections,
  and the separate `C1 -> CD01` period doubling.
- Isolated-shrimp origin marks and words with no transcribed edge are retained.
  No missing edge or word-to-coordinate-box association is invented.
- The title-page author and PDF author metadata are blank, as requested.
  Historical citations continue to credit the original authors.
- The paper and README now distinguish the locally qualified operational
  alphabet from the unverified generating partition, target words, and
  dynamical connections. The supplement links back to the main chain figure.

## Evidence boundary

The figure is a source reconstruction, not a new numerical experiment. Its
input remains the frozen Figure 2/6 transcription at SHA-256
`6a5aba797473d40db9197d7a2ebe51195193f888613800584f406742376581da`.
That file is unchanged because historical experiments bind its exact bytes.

An independent review checked the revised explanation against the original
PDF, transcription, alphabet semantics, and EXP-185/186/202 findings. The
local alphabet has support; the 23-word and arrow validation remains open.
The failed landmark/center searches do not amount to a refutation of the
entire original chain. No new trajectory, orbit solve, or paid job was run.

The next scientific figure is still a computed unfolded spiral joining
parameter position, return geometry, corrected orbits, and symbols. That
would test the historical chain now displayed, rather than substitute for
showing the hypothesis in the first place.

## Verification and manuscript checkpoint

All **790 tests pass**, including 31 source-graph checks and three manuscript
presentation checks. The citation checker verifies 16 cited bibliography
entries, all 15 required citations, and 34 figures. The final PDF builds
without warnings. All 63 pages were rendered for layout review; the new chain
page and blank-author title page were also inspected at higher resolution.

The main article is 16 pages. Section 5 starts on page 12 and the chain is
Figure 10 on page 14. `pdfinfo` confirms an empty Author field, and extracted
title-page text contains no author line. Citations and source attributions
remain intact.

The source changes were merged in [PR #7](https://github.com/tdj28/butterfly/pull/7)
at `33156f01909115dfa9955ce7a446fa083b231297`, with CI passing on Python 3.12
and 3.13. The `manuscript-symbolic-v1` release is prepared as a draft containing
the revised PDF, separate chain PNG, and checksums. Uploaded asset digests
match the local files. Public release publication was blocked by a permission
check and awaits explicit approval; no public-download verification is claimed.
Earlier research-checkpoint release assets are left unchanged. The new PDF SHA-256 is
`5eb3daa3dfc1c9e97200b2d24194a8aada910f89dd155e1f60646eeda2790e8f`;
the chain PNG is
`486493ed088a386d829bf3e29a089c8aa3d68c8ca6a7089988dca6986f0530ef`.
