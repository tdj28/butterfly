#!/usr/bin/env python3
"""Independently qualify the primitive stable period-8 child after EXP-166."""

from qualify_period4_c_child import run_child_qualification


def main() -> int:
    return run_child_qualification(
        manifest_schema="butterfly.period8-c-child-qualification-manifest.v1",
        output_schema="butterfly.period8-c-child-qualification-receipt.v1",
        labels=["period4-parent", "period8-minus", "period8-plus"],
        expected_parent_winding=4.0,
        expected_child_winding=8.0,
        scientific_scope=(
            "primitive stable period-8 child and local stability exchange after the "
            "third fixed-path flip; not the later cascade or homoclinic endpoint"
        ),
    )


if __name__ == "__main__":
    raise SystemExit(main())
