# FND-019 — Blind `a=0.147` saddle is two-branch

Status: qualified blind local result

## Result

EXP-122 passes from clean commit `57e629b` in `272.07 s`. The manifest encodes
no expected branch count. Candidate counts two and three are evaluated
separately under the qualified EXP-121 rule, and all seven ensembles in both
coordinates uniquely select two. Candidate three fails every run-coordinate
decision.

Across the 210 variant cells, 207 resolve normally as two. The remaining three
are 80-bin `y` coverage censors in the later-conditioned run and retain the
required nominal two-branch geometry. No variant is rejected or returns three.

The weakest run retains 350 final survivors and 3008 return pairs. Maximum
survivor-fraction drift is `0.00568`, maximum across-run critical drift is
`0.01499`, all short-horizon audits pass, and no integration fails.

## Implication and boundary

Together with the prospectively qualified three-branch saddle at `a=0.149`,
this halves the sampled transition bracket to `[0.147,0.149]`. The result is
stronger than an expected-label confirmation because the candidate count was
selected blindly and unanimously across all run-coordinate decisions.

It remains a finite bracket, not a proof of a continuous curve or an exact TBA
location. Further blind bisection and independent local continuation are still
required.

Raw receipt SHA-256:
`938896accbfef79e2212588b3174a6ec2f21a3ae9dc51038f925e801932f1928`.
