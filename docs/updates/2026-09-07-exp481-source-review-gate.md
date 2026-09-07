# EXP-481: independently anchored source and review checks

The source/review prerequisite for the production controller is implemented.
It checks actual Git objects and a live pushed ref, reconstructs the exact
submitted review packet, and requires an explicit disposition for every finding
and every post-review source/design change. It does **not** yet issue worker
authorization or start a research phase.

The completed numerical pipeline remains unchanged from PR #44, merged at
`aa9d5b87d88c46de92c98b904688b7c4b3960e86`. No Rössler trajectory, paid review,
GPU rental or remote artifact upload was generated for this checkpoint.

## What is now checked

`paired_release.py` provides standard-library-only checks that a host controller
can run before importing the numerical package. The source check observes the
actual local HEAD, requires a clean tracked checkout and the expected public
repository URL, and compares the exact branch ref returned by `git ls-remote`.
It does not accept a receipt merely repeating the requested source commit.
Git replacement objects and filesystem-monitor shortcuts are disabled for
these checks. Individual inventory rows must match ordinary-file Git blobs
and current bounded, nonsymlink files. A rehashed modified checkout still fails.

`scripts/check_paired_release.py` fixes the source/test role set itself, including
the numerical runtime map, mandatory paired tests, direct numerical tests,
qualification producers, locked dependency declarations and its own checker.
A release cannot supply a shorter role list to omit a required file. Source
mode is a genuine outcome-free command; reviewed mode composes these checks
with the release's committed review evidence. Both deny target-launch authority.

The review check calls the canonical research-review helper's existing offline
validator, not a simplified reconstruction. An exact copy is checked into
`tools/review_experiment_plan.py` and pinned by SHA-256, so this check no longer
depends on a mutable sibling checkout. It does not enter the numerical worker.
Only its credential-free completed-bundle function is called; no API key or
network request is used by review validation.

That validator reconstructs the actual brief and bounded contexts, then checks
the physical request/payload/response/review bytes, the provider-echoed packet
metadata, response ID, model, usage and cost bookkeeping. The paired gate also
requires Pro mode, no unbound researcher-emphasis block, the expected packet
commit and no recorded review-budget overrun. The first context is generated
from the complete committed machine design and the local source/design inventory
hash. A self-consistent context describing different scientific choices fails.

Verdicts are parsed as one exact final line inside the `# Verdict` section.
`NOT READY TO FREEZE` cannot match the positive verdict by substring. Bold,
duplicate, absent and misleading-prose verdicts fail closed. Finding IDs come
from actual `## B01` / `## I01` headings in the appropriate sections, not mentions
inside checklists, prose or fenced quotations. The canonical section set is
required and an empty finding section must explicitly say `none`.

Every actual finding needs a disposition, rationale and resolution. Deferred
blockers and `needs_human` dispositions block release. A deferred nonblocking
item needs an explicit claim narrowing. Every changed, added or removed path
must match the before/after inventories and map to a finding that explicitly
authorizes a change. Rejected findings cannot license changes. A ready-with-fixes
verdict needs implemented changes; a no-findings review cannot authorize an
arbitrary new design. The inventory and review bindings are included in the
adjudication's checked self-hash.

## Scope and remaining work

The full local suite passes **1,658 tests**, with one older Linux-only skip on
macOS. The 56 new tests include real temporary Git repositories and bare remotes,
the canonical helper with synthetic provider responses and network disabled,
and a complete source-to-review consumer. They test unchanged approval and
reject a false committed inventory, substituted machine context, unmapped code
change, wrong packet commit, malformed verdicts and incomplete dispositions.
All recalculated local self-hashes are kept consistent in the semantic-tampering
controls so a broken checksum is not the reason those cases fail.

The actual source-preflight command also passed under `-I -S -B -X utf8`
against pushed implementation commit `9f942987f04369e1577094b19db0592e8e7d5cbc`.
It observed the matching live task-branch ref and checked 55 source/test files.
The [public receipt](../experiments/receipts/EXP-481-source-review-gate.json)
includes that complete observed source inventory. The local receipt is preserved
at `artifacts/EXP-481/release-source-01/receipt.json`: 8,985 bytes, SHA-256
`170062f7bd14cf642eec5dba307253e3ea35143106af3d3274a6545300c1c783`.
This was a source-only check, not a real reviewed-release approval. No source
file changed when this evidence was added afterward.

The checks assume trusted host Git/SSH, filesystem and preservation of the
provider response. Saved metadata is not a provider digital signature or proof
that no other review was requested. The reviewer sees the compact packet, not
omitted code or raw trajectories. Accepted implementation repairs are locally
verified, not retrospectively described as code inspected by the reviewer.
The gate observes that a ref is pushed now; the later controller must record
that observation before the first target outcome, rather than inventing a
historical push timestamp.

The next step is the controller's runtime/input handshake and one-shot worker
authorization around the already-tested phases, using their actual target
resource budgets. The numeric-only design and reviewed-release files are
reserved future paths, not placeholder approvals. Once that full entry point
is qualified, create the real compact review packet, adjudicate its actual
response and push the executable release. The current sampling proposal and
worker `execute` refusal remain unchanged. No synthetic review fixture grants
research execution authority.

The experiment-integrity playbook shaped these independent anchors, exact
packet reconstruction and explicit change accounting. OpenAI Docs was used to
check the [response metadata contract](https://developers.openai.com/api/reference/cli/resources/responses/methods/retrieve);
the canonical helper itself was copied without modification. This remains an
engineering prerequisite, not new evidence for or against Jones's symbols.
