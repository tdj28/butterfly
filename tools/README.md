# Pinned research-review helper

`review_experiment_plan.py` is an exact copy of the canonical helper supplied in
the user's sibling `agent-skill-documents/scripts/` checkout, captured 2026-09-07.
SHA-256: `7ebe3185868e0f4ebe07c162a95c7c2195669e02ce5dde088aad0456859b6dff`.
It is vendored so an offline release check does not depend on an untracked,
mutable sibling checkout. This file is host-side tooling, not part of the
isolated numerical worker's import closure.

`paired_release.validate_review_bundle` calls only its credential-free,
read-only completed-bundle validator. That reconstructs the exact packet and
checks the request, saved response, echoed metadata and review text. Tests use
synthetic provider responses with all network access disabled. Neither those
fixtures nor self-consistent JSON constitute a real advisory review.

The canonical tool also retains its original explicit `--execute` functionality;
the release verifier never invokes it. A future paid review must follow the
research-integrity playbook, use current official model/pricing information,
run a cost preflight and retain the actual provider response. No new paid review
has been submitted for EXP-481 at this checkpoint. Do not edit this pinned copy
silently: a tool update requires a new source binding and regression checks.

Response IDs, status and metadata are documented in the
[official Responses API reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/retrieve).
Matching saved metadata binds the preserved packet to that response; it is not
a digital signature, a provider-global one-call proof or review of omitted code.
