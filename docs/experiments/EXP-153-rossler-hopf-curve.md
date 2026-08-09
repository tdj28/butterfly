# EXP-153 — Analytic Rössler Hopf curve

Status: code, method, and acceptance gates frozen before clean execution

## Question

Can the regular small-equilibrium Andronov--Hopf locus used in the Jones
Figure 2 construction be reconstructed without relying on PyCONT/AUTO, and
does an independent eigensystem root solve reproduce every analytic point?

## Exact construction

For an equilibrium `(a*z,-z,z)`, define `r=b/z=c-a*z`. The characteristic
polynomial is `lambda^3+A lambda^2+B lambda+C`, where

- `A=r-a`,
- `B=1+z-a*r`, and
- `C=r-a*z`.

The Hopf condition `A*B=C` reduces exactly to

`a*(1+r^2-a*r)=b`.

Each positive root gives `z=b/r` and `c=a*z+r`. EXP-153 evaluates the unique
regular small-equilibrium point at 191 evenly spaced `a` values over
`[0.1,0.195]`, plus the exact reported hub abscissa `a=0.1798`.

## Frozen independent gates

Every one of the 192 points must use equilibrium index zero, retain a negative
real eigenvalue with magnitude at least `0.05`, and pass equilibrium,
Routh--Hurwitz, characteristic-polynomial, imaginary-pair, frequency, and
independent Brent-root errors at the frozen limits in the manifest. A
`c +/- 1e-6` test must place the complex-pair real part below `-1e-8` and above
`+1e-8`, respectively.

## Interpretation boundary

Passing reconstructs and qualifies the local Hopf locus and locates the Hopf
endpoint of the fixed-`a=0.1798` vertical slice. It does not continue the
period-1 limit cycle, validate the proposed homoclinic endpoint, recover the
exact `L1`/`L2` paths, or establish logistic-map ordering.
