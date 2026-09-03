#!/usr/bin/env python3
"""Switch the fixed-(a,b) period-8 flip onto its period-16 child in c."""

from switch_period2_c_flip import run_switch_solver


def main() -> int:
    return run_switch_solver(
        manifest_schema="butterfly.period8-c-flip-switch-manifest.v1",
        event_schema="butterfly.period8-c-flip-receipt.v1",
        parent_schema="butterfly.period8-c-arclength-to-flip-receipt.v1",
        output_schema="butterfly.period8-c-flip-switch-receipt.v1",
        scientific_scope=(
            "local period-16 branch switch at the fourth fixed-path flip; "
            "independent child identity, stability exchange, and attraction "
            "require qualification"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
