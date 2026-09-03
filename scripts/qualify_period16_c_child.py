#!/usr/bin/env python3
"""Independently qualify the primitive stable period-16 child after EXP-172."""

from qualify_period4_c_child import run_child_qualification


def main() -> int:
    return run_child_qualification(
        manifest_schema="butterfly.period16-c-child-qualification-manifest.v1",
        output_schema="butterfly.period16-c-child-qualification-receipt.v1",
        labels=["period8-parent", "period16-minus", "period16-plus"],
        expected_parent_winding=8.0,
        expected_child_winding=16.0,
        scientific_scope=(
            "primitive stable period-16 child and local stability exchange after the "
            "fourth fixed-path flip; not the later cascade or homoclinic endpoint"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
