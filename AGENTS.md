# Research review policy

Human-directed policy, 2026-09-08. This supersedes older automatic Pro-review
requirements in experiment plans, status notes, and recurring task prompts.

- Paid Pro reviews are optional and allowed only at major research or
  publication milestones, with explicit human approval for each paid request.
  A standing budget, API refill, upload/publication approval, or "keep going"
  does not authorize a call, retry, continuation, or second review pass.
- Routine numerical refinements, successor experiments, tests, bug fixes,
  recovery, and manuscript edits use local audits. Do not block them on an
  optional paid review or repeatedly ask for one at ordinary checkpoints.
- Before proposing a paid review, state the milestone, packet, model, estimated
  cost, and known cumulative spend. Use GPT-6 Astra (`gpt-6-astra`) in Pro mode
  for new approved calls; verify current official rates. Preserve historical
  models, responses, and receipts unchanged.
- The canonical policy and client are in `../agent-skill-documents/`, especially
  `EXPERIMENT_INTEGRITY_SKILLS.md` §7A. Its client requires a human-approval
  reference and major-milestone argument. Do not execute an older vendored
  client to evade the human-approval policy.
- Where a frozen executable gate still requires an AI response, amend and test
  a clearly labeled no-paid-review release path prospectively. Never fabricate
  approval, reuse an old response as a new review, weaken scientific accuracy
  thresholds, erase failures, or reset a consumed experiment attempt.

Current transition: see `docs/updates/2026-09-08-human-controlled-pro-reviews.md`.
