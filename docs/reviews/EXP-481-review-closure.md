# EXP-481 prospective review closure

The review is a design audit, not a source audit or independent scientific
verification. Its packet consists only of `EXP-481-review-brief.md`, the exact
generated `EXP-481-decision-context.md`, and `EXP-481-evidence-context.md`.
No target outcomes or exhaustive source/runtime inventories are submitted.

| Decision claim | Local authority and checks |
| --- | --- |
| Fixed hypotheses, sample, stopping rules and all thresholds | `experiments/manifests/EXP-481-paired-design.json`; `paired_sampling_plan.py`, `paired_phases.py`; sampling-plan and phase tests |
| Preserved cycle events and candidate parameters | Nine-file package, `paired_inputs.py` raw audit; input-package/capture-input tests and actual setup witness |
| Original-ID cohort and no refilling/bridging | `paired_sampling.py`, `paired_replay.py`; sampling/replay tests |
| Scalar adequacy, bootstrap, critical proximity, nonrescuing diagnostics | `seed_return_map.py`, `paired_decisions.py`, `paired_campaign.py`; seed-map/decision/campaign tests |
| Actual setup, phase authorization and complete evidence before next stage | `run_paired_campaign.py`, `dispatch_paired_phases.py`, `paired_authorization.py`, `paired_supervisor.py`; 379 source-bound tests and actual three-phase circle control |
| Exact review provenance and finding/change adjudication | `paired_release.py`, `check_paired_release.py`; release tests and pinned canonical helper's offline completed-bundle validator |

The independent source closure is produced by `check_paired_release.check`,
not a reviewer-supplied allowlist. It has 364 source/test-support files; adding
the numeric design gives the reviewed inventory committed in the decision
context. Source qualification is tied to code freeze
`2f05fd2fb96e1ee7329010a8828e85e86f783db4`, not the later packet/release commit.
Later scientific changes must map to actual review findings and be qualified
under their own final code freeze. Evidence-only additions do not relabel the
earlier execution identity.

## Reserved review and release roles

The paid request starts in a fresh ignored `artifacts/EXP-481/review-01/`.
After offline validation, promote its exact `review_manifest.json`,
`request_payload.json`, `review_request.md`, `response.json` and `review.md`
to `docs/reviews/EXP-481-review-01/`. Preserve unsuccessful attempts without
overwriting them. The finding ledger will be
`docs/reviews/EXP-481-adjudication.json` with human explanation in
`docs/reviews/EXP-481-adjudication.md`; the final machine release will be
`experiments/manifests/EXP-481-reviewed-release.json`. These paths are reserved,
not placeholder approval files. The existing release schema binds actual
provider response/model/input hashes, reviewed packet commit, both complete
inventories, finding-specific changes and self-hashed adjudication.

## Model and budget

Official OpenAI documents checked on 2026-09-07 name `gpt-6-astra` as latest.
Use Pro mode, medium effort, 6,000 requested output tokens; short-context rates
per million tokens are $10 input, $12.50 cache write, $50 output. The long-input
threshold is 272,000 tokens; this compact packet is well below it. Reserve five
times input work and twice output work plus cache writes. Dry-run first under
the $1.25 authorization; the helper also counts actual input before generation.
This is a conservative authorization estimate, not a provider billing hard cap.
No additional reviewer emphasis, tools, background mode or API storage.

Sources: [latest model](https://developers.openai.com/api/docs/guides/latest-model),
[model limits](https://developers.openai.com/api/docs/models/gpt-6-astra),
[pricing](https://developers.openai.com/api/docs/pricing).

## Preserved pre-outcome incident

The first execution-branch control command accidentally constructed commit
`2f05fd2ab96e1ee7329010a8828e85e86f783db4` instead of the actual full Git ID.
`execution-source-control-01/preflight/failure.json` records its rejection at
2026-09-07T12:33:32.549836Z, before target authorization or trajectories. The
directory remains intact. The corrected, fresh `execution-source-control-02`
passed against the independently read actual commit; no code or threshold was
changed to make the failed command pass. This was an outcome-free control,
not a consumed research attempt or a paid review.
