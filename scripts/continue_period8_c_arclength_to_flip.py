#!/usr/bin/env python3
"""Pseudo-arclength continuation of the Jones-path period-8 child."""

from continue_period4_c_arclength_to_flip import run_arclength_continuation


def main() -> int:
    return run_arclength_continuation(
        manifest_schema="butterfly.period8-c-arclength-to-flip-manifest.v1",
        source_schema="butterfly.period4-c-flip-switch-receipt.v1",
        output_schema="butterfly.period8-c-arclength-to-flip-receipt.v1",
        expected_winding=8.0,
        scientific_scope=(
            "identity-safe pseudo-arclength period-8 continuation and first -1 "
            "bracket; not an exact event or switched period-16 child"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
