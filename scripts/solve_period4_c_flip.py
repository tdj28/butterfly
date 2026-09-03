#!/usr/bin/env python3
"""Solve the fixed-(a,b) period-4-to-8 flip with an exact c-Jacobian."""

from solve_period2_c_flip import run_flip_solver


def main() -> int:
    return run_flip_solver(
        manifest_schema="butterfly.period4-c-flip-manifest.v1",
        source_schema="butterfly.period4-c-arclength-to-flip-receipt.v1",
        output_schema="butterfly.period4-c-flip-receipt.v1",
        expected_winding=4.0,
        scientific_scope=(
            "coupled period-4-to-8 flip on the fixed-(a,b) Jones path; not a "
            "switched period-8 child, higher cascade, symbolic ordering, or "
            "homoclinic connection"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
