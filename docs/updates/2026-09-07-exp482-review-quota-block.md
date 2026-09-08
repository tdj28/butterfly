# EXP-482: packet published; API credit balance blocks review

**Superseded operational status, 2026-09-08:** the human reports funding the
account and has made Pro review optional, major-milestone-only, and subject to
explicit per-call human approval. Do not automatically retry this review. See
[the policy transition](2026-09-08-human-controlled-pro-reviews.md). The failure
and provenance recorded below remain historical evidence.

The user explicitly approved publication of the EXP-482 packet, including
the prior AI advisory, and requested continued flow-level symbolic testing.
The packet was committed and pushed at
`2415d0e32c792c2a7549d15d20d781f28f74de50` on
`codex/exp482-successor-gate`. The staged scan passed for 2,464 tracked files.
The publication permission block is resolved; do not ask for it again.

The exact source preflight passed at that live remote commit. Its source/design
inventory is unchanged:
`9c29baff1625297d022add54330fbd33d50dfb2f65e9167ce7e55d5a69396bca`.
The original 426-test qualification therefore remains bound to the same source.
The final packet dry-run contains 37,018 input characters and reserves $1.9883
within the $2 authorization. Current official model and pricing documentation
still specifies gpt-6-astra and standard input/cache-write/output rates of
10/12.5/50 USD per million tokens.

## Actual failure

At `2026-09-08T02:54:47.308781Z`, the canonical client's non-generating
input-token preflight returned HTTP 429 with `insufficient_quota` /
`credit_balance_exhausted`: the configured OpenAI API account has no credits.
The client stopped before calling its Responses generation function. No review
response or response ID exists, no scientific verdict was returned, and no
target trajectory or attempt slot was consumed. This is not a negative
scientific review. No automatic API retry or alternate account was attempted.

Preserved local bundle: `artifacts/EXP-482/review-01/`, containing the request,
request payload, failed manifest and failure receipt. Do not overwrite it.

- Input SHA-256: `4c0e2ef7c922d9a0ba3a68bb137b17a2b39e68f37e908ed725050e0f82faf12d`
- Request-payload SHA-256: `808c643983e2572666781d947160814dcbf38d3cbaa51726df12576a475dc750`
- Failure SHA-256: `29f09a5b99e70bd2b1ca041b0f266c00b48e6e2371488a7ae08bdf2d3c34df56`
- Failed-manifest SHA-256: `7e2bae94bcb124449dcc3af320b81223ab57324ea9c96bed4996ffa70b875284`

The needed external change is funding the configured API account. A standing
research dollar budget is permission to spend, not API credit. Once credit is
available and the user resumes, use a fresh review output directory and the
same frozen packet; preserve this failed token-count attempt. Adjudicate the
authentic completed review and create the actual release before the single
EXP-482 target execution. No fabricated approval or substitution of an old
review is permissible.

## Preserved separate manuscript audit

The preceding local root-origin audit and manuscript corrections are preserved
in the named path-scoped Git stash with object
`ef1de4127d5dd7f98454bc17e08ca8a1946a3170`. It includes the added audit source,
tests, exact receipt, update and five manuscript section edits, plus the local
successor-preflight update. This isolates that unrelated source addition from
EXP-482's already-qualified inventory; none of it was deleted or represented
as pushed. The rebuilt local PDF remains available. Restore those changes on
their own publication path without silently altering the reviewed source closure.

Prax backup and heartbeat approvals remain separate and do not gate this
review or local scientific execution. The stale heartbeat must not rerun old
benchmarks or retry an exhausted API account. Jones's flow-level itineraries
and connections remain unresolved; completing review or setup is not their
verification.
