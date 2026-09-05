"""Keep publication access and selected review-response tables auditable."""

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def test_data_availability_is_in_main_article_and_links_public_material():
    main = (PAPER / "manuscript.tex").read_text().split(r"\appendix", 1)[0]
    assert r"\input{sections/08-data-availability}" in main
    availability = (PAPER / "sections/08-data-availability.tex").read_text()
    for path in (
        "https://github.com/tdj28/butterfly",
        "/releases/tag/research-core-v1",
        "/releases/tag/research-exp476",
        "/paper/supplement/rossler-multib-atlas.gif",
    ):
        assert path in availability


def test_mathematical_objects_and_claim_closure_have_explicit_labels():
    objects = (PAPER / "sections/02-mathematical-objects.tex").read_text()
    claims = (PAPER / "sections/06-discussion.tex").read_text()
    assert r"\label{eq:quotient-condition}" in objects
    assert r"\label{tab:distinct-loci}" in objects
    assert "Evidence needed for closure" in claims


def test_saddle_endpoint_csv_matches_tracked_source_summaries():
    with (PAPER / "tables/review001-saddle-bracket.csv").open(newline="") as source:
        rows = list(csv.DictReader(source))
    expected = []
    lower_path = "docs/experiments/receipts/EXP-148.json"
    lower = json.loads((ROOT / lower_path).read_text())
    for profile in lower["profiles"]:
        expected.append((
            lower["parameters"]["a"], profile["maximum_escape_returns"],
            profile["pair_count_per_coordinate"], profile["successful_straddles"],
            profile["y_branch_count"], profile["z_branch_count"], lower_path,
        ))
    upper_path = "docs/experiments/receipts/EXP-128.json"
    upper = json.loads((ROOT / upper_path).read_text())
    assert upper["observed_branch_count"] == 3
    for label, profile in upper["profiles"].items():
        assert profile["passed"] and profile["resolved_three_branch_variants"] == 30
        expected.append((
            upper["a"], int(label.removeprefix("horizon-")),
            profile["return_pairs_per_coordinate"], profile["successful_straddles"],
            3, 3, upper_path,
        ))
    actual = [(
        float(row["a"]), int(row["maximum_escape_returns"]),
        int(row["pair_count_per_coordinate"]), int(row["successful_access_lines"]),
        int(row["y_branch_count"]), int(row["z_branch_count"]), row["source_summary"],
    ) for row in rows]
    assert sorted(actual) == sorted(expected)
    assert all(float(row["b"]) == 0.2 and float(row["c"]) == 20 for row in rows)
