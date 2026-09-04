# Later research: what it changes for this project

Date: 2026-09-04. Scope: targeted primary-source update, not an exhaustive
literature review or independent verification of the cited proofs.

The defensible aim is a reproducible, uncertainty-aware extension of the
Jones/Barrio co-discovery, not a claim that hub organization or symbolic
parameter scans were previously unknown. The following comparison guides
experiments; uncompleted work is not presented as a new result.

| Question | Relevant prior result | Our current contribution and remaining test |
|---|---|---|
| Why do shrimp patterns form hubs? | Barrio et al. (2013) connects the canonical Rössler hub to a turning homoclinic curve and distinguishes Lorenz-like organizing centers. | Reproduce geometry with explicit numerical uncertainty; do not claim the connection itself is new. |
| Can multiple hubs be organized symbolically? | Malykh et al. (2020) studies primary/secondary hubs, both saddle-foci, return maps and symbolic scans. | Compare corrected orbits and parameterized branches, with equation conversion first. |
| Does finite period ordering imply a one-dimensional flow? | Gierzkiewicz and Zgliczyński (2021) proves period-existence statements using two-dimensional covering relations and CAPD. | Our finite word table remains incomplete; period counts alone do not establish Jones's exact words or a global scalar conjugacy. |
| What would make a homoclinic claim rigorous? | Capiński and Wasieczko-Zając (2017) combines invariant-manifold bounds with interval propagation; Nitta et al. (2022) uses verified Lyapunov regions and a topological existence argument. | Floating-point collocation agreement is a numerical cross-check, not an existence or uniqueness proof. |

Sources: [2013 chapter](https://doi.org/10.1007/978-3-642-38830-9_4),
[2020 article](https://doi.org/10.1063/5.0026188),
[2021 article](https://doi.org/10.1016/j.cnsns.2021.105891),
[2017 article](https://doi.org/10.1137/16M1079956),
[2022 article](https://doi.org/10.1007/s13160-022-00502-5).
Bibliographic and reading status are recorded separately in the
[reference ledger](../../paper/reference-ledger.md).

## A parameter-convention trap we must avoid

Malykh et al.'s equation (1) uses

\[
\dot X=-Y-Z,\qquad \dot Y=X+\alpha Y,\qquad
\dot Z=\beta X+Z(X-\gamma),
\]

with the origin fixed and `beta = 0.3` in that study. Their equation (2) lists
the canonical form used here. These equal-looking parameter names do not
describe the same numerical parameter slice.
Source: [author preprint, equations (1)–(2)](https://arxiv.org/abs/2008.12865).

**Our algebraic conversion:** translate the canonical equilibrium
`(a*z0, -z0, z0)` to the origin, where `a*z0^2 - c*z0 + b = 0`:

```
X = x - a*z0,  Y = y + z0,  Z = z - z0
alpha = a,    beta = z0,    gamma = c - a*z0

inverse: a = alpha,  b = beta*gamma,  c = gamma + alpha*beta
```

The translated right-hand side follows by substitution, without time scaling.
At fixed canonical `b = 0.2`, the corresponding translated parameters obey
`beta*gamma = 0.2`; they do not lie on the fixed-`beta = 0.3` plane.
The conversion is implemented and tested in
`python/butterfly/rossler_conventions.py`. It is a coordinate/parameter
conversion, not an independent dynamical result.

The 2021 period paper has a simpler naming difference: its `(a,b)` means
our `(c,a=b)`. Its two parameter cases therefore mean canonical
`(a,b,c)=(0.2,0.2,5.25)` and `(0.2,0.2,4.7)`, not a value of our `a` above four.
Source: [publisher model and introduction](https://www.sciencedirect.com/science/article/pii/S1007570421002033).

## Experiments this changes

1. Test the new independent boundary-value implementation on a known
   connection before using it to qualify the historical Rössler candidate.
2. Track both saddle-foci explicitly; never infer equilibrium identity from
   labels such as `P2` or `O1` used in different papers.
3. Compare parameter slices only after an equation-level conversion.
4. Use Lorenz-like geometry as a contrasting transfer test, not as evidence
   that every strange attractor must share one shrimp mechanism.
5. Treat interval validation and finite word ordering as distinct deliverables.

Still open: a complete 2013–2026 bibliography, proof/code reproductions,
exact symbolic partition conventions, and a claim-by-claim comparison of
our proposed new results with all relevant later work.
