# Paid Pro reviews: major milestones and human approval only

The human reported $50 total API spend yesterday, confirmed an account refill,
and explicitly changed the review policy. The $50 is a human-reported total,
not a figure reconciled from provider billing here. The previously quoted
$0.5888 was one completed review's cost, not the project's total spend.

## Current policy

Paid Pro reviews are optional, reserved for major research/publication
milestones, and require explicit human approval for each paid request. Routine
experiments, numerical refinements, recovery, tests, and editing do not trigger
them. Refilling the account does not approve another review. New approved calls
use GPT-6 Astra (`gpt-6-astra`) in Pro mode, with current explicit pricing.

The shared experiment-integrity, research-note, and knowledge-base guides were
updated, along with their README and the Git guide's live-credential exception.
Their canonical client now defaults to Astra and refuses execute mode without
a human-approval reference and named major milestone. Those fields are operator
attestations, not independent proof of consent. All 25 client tests passed
offline with mocks, including legacy-bundle compatibility. No paid review ran.
The first test pass exposed a test-only reference to a nonexistent profile
registry; the test was corrected to cover the four actual CLI review kinds.

## Effect on EXP-482

The quota failure in `review-01` remains immutable historical evidence. The
account refill is reported by the human, not verified with a billable call.
Do not retry the pending review automatically or wait for funding again. The
new policy supersedes the old prospective-Pro requirement and stale heartbeat
instructions; the human has authorized continued research under this policy.

The existing EXP-482 executable release validator still requires an authentic
review bundle. Its migration is not completed by changing prose. The next
implementation step is a prospectively committed and tested, explicit
no-paid-review release path that preserves all source/input binding, numerical
qualification, analysis rules, and one-shot attempt protection. Retain earlier
review findings and adjudications as prior context, never as an EXP-482 verdict.
No EXP-482 target trajectories have been generated during this policy change.

Historical manuscript/audit changes remain preserved in the existing scoped
stash. Frozen experimental branches and the vendored historical API client
remain unchanged. Jones's flow-level symbolic chains are still unresolved.
