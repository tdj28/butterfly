"""Published receipt presentation checks; no root enumeration or flow run."""

from copy import deepcopy
import csv
from fractions import Fraction
import io
import json

import pytest

from scripts import render_quadratic_control_table as table


def test_published_inputs_rederive_every_table_count_and_match():
    control, compared, source = table.load_frozen_inputs()
    rows, derived = table.derive_rows(control, compared, source)
    assert [row["period"] for row in rows] == list(range(2, 8))
    assert [row["scalar_cycle_count"] for row in rows] == [len(row["cycles"]) for row in control["period_results"]]
    assert [row["comparable_source_node_count"] for row in rows] == [len(row["source_top_to_bottom_words"]) for row in derived["period_results"]]
    assert all(row["conditional_set_match"] and row["conditional_order_match"] for row in rows)
    assert len(derived["all_source_nodes"]) == 23
    assert {row["source_word"] for row in derived["all_source_nodes"] if row["status"] == "out_of_model"} == {"C2", "C21"}


@pytest.mark.parametrize("mutation", [
    lambda compared: compared.update(conditional_order_match=False),
    lambda compared: compared["period_results"][0].update(conditional_set_match=False),
    lambda compared: compared["period_results"][0]["cycles"][0].update(scalar_word="C2"),
    lambda compared: compared["all_source_nodes"].pop(),
    lambda compared: compared["period_results"][4]["increasing_mu_proposed_words"].reverse(),
])
def test_changed_comparison_values_are_rejected_not_rendered(mutation):
    control, compared, source = table.load_frozen_inputs()
    mutation(compared)
    with pytest.raises(ValueError, match="stored comparison differs"):
        table.derive_rows(control, compared, source)


def test_input_hash_change_fails_before_table_derivation(tmp_path):
    name = next(iter(table.FROZEN_HASHES))
    path = tmp_path / name
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    with pytest.raises(ValueError, match="frozen input SHA-256 mismatch"):
        table.load_frozen_inputs(tmp_path)


def test_generation_is_deterministic_and_full_table_has_six_data_rows():
    first, second = table.build_artifacts(), table.build_artifacts()
    assert first == second
    latex, words, provenance_bytes = first
    text = latex.decode()
    provenance = json.loads(provenance_bytes)
    data_lines = [line for line in text.splitlines() if line[:1].isdigit()]
    assert len(data_lines) == 6
    assert text.count(r"\begin{table}") == text.count(r"\end{table}") == 1
    assert text.count(r"\caption{") == 1
    assert r"\label{tab:quadratic-symbolic-control}" in text
    assert "No R" in text and "connecting arrow" in text
    assert provenance["output"]["sha256"] == table.sha256_bytes(latex)
    assert provenance["output"]["bytes"] == len(latex)
    assert provenance["word_csv"]["sha256"] == table.sha256_bytes(words)
    assert provenance["word_csv"]["bytes"] == len(words)
    assert provenance["generator"]["sha256"] == table.sha256_bytes(table.Path(table.__file__).read_bytes())
    assert not provenance["root_enumeration_rerun"]
    assert not provenance["root_proof_independently_replayed"]


def test_published_generated_outputs_match_reproducible_bytes():
    latex, words, provenance = table.build_artifacts()
    assert (table.ROOT / table.TABLE_PATH).read_bytes() == latex
    assert (table.ROOT / table.WORDS_PATH).read_bytes() == words
    assert (table.ROOT / table.PROVENANCE_PATH).read_bytes() == provenance


def test_render_table_handles_a_mismatch_without_forcing_yes():
    rendered = table.render_table([{"period": 2, "scalar_cycle_count": 1,
                                   "comparable_source_node_count": 2,
                                   "conditional_set_match": False, "conditional_order_match": False}]).decode()
    assert "2 & 1 & 2 & No & No" in rendered


@pytest.mark.parametrize("changed_path", [table.TABLE_PATH, table.WORDS_PATH, table.PROVENANCE_PATH])
def test_verify_never_writes_and_detects_stale_artifact(tmp_path, monkeypatch, changed_path):
    latex, words, provenance = table.build_artifacts()
    monkeypatch.setattr(table, "ROOT", tmp_path)
    monkeypatch.setattr(table, "build_artifacts", lambda: (latex, words, provenance))
    for name, payload in ((table.TABLE_PATH, latex), (table.WORDS_PATH, words), (table.PROVENANCE_PATH, provenance)):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    monkeypatch.setattr(table.Path, "write_bytes", lambda *_args, **_kwargs: pytest.fail("verify must be read-only"))
    assert table.main(["--verify"]) == 0
    with (tmp_path / changed_path).open("ab") as stream:
        stream.write(b"% drift\n")
    assert table.main(["--verify"]) == 1


def test_csv_has_every_root_word_and_verbatim_rational_enclosure():
    control, compared, source = table.load_frozen_inputs()
    _rows, derived = table.derive_rows(control, compared, source)
    payload, count = table.render_word_csv(control, derived)
    parsed = list(csv.DictReader(io.StringIO(payload.decode())))
    assert len(parsed) == count == sum(len(row["cycles"]) for row in control["period_results"])
    assert list(parsed[0]) == list(table.WORD_COLUMNS)
    expected = [(period, index, cycle)
                for period in control["period_results"]
                for index, cycle in enumerate(period["cycles"])]
    for row, (period, index, cycle) in zip(parsed, expected, strict=True):
        lower, upper = cycle["parameter_interval"]
        assert row["period"] == str(period["period"])
        assert row["root_index_zero_based"] == str(index)
        assert (row["mu_lower_exact"], row["mu_upper_exact"]) == (lower, upper)
        assert row["native_word"] == cycle["critical_anchored_word"]
        assert row["mapped_source_word"] == table.comparison.proposed_dictionary(cycle["critical_anchored_word"])
        assert row["conditional_membership_match"] == "true"
        midpoint = (Fraction(lower) + Fraction(upper)) / 2
        assert abs(Fraction(row["mu_midpoint_decimal_approx"]) - midpoint) <= Fraction(1, 2 * 10 ** 16)
    assert parsed[0]["mu_midpoint_decimal_approx"] == "1.0000000000000000"
    assert {row["mapped_source_word"] for row in parsed}.isdisjoint({"C2", "C21"})


def test_decimal_display_rounds_exactly_even_at_halfway_cases():
    # These are synthetic rounding fixtures, not critical-cycle parameters.
    scale = 10 ** table.MIDPOINT_DECIMAL_PLACES
    even_tie = str(Fraction(1, 2 * scale))
    odd_tie = str(Fraction(3, 2 * scale))
    assert table.approximate_midpoint(even_tie, even_tie) == "0.0000000000000000"
    assert table.approximate_midpoint(odd_tie, odd_tie) == "0.0000000000000002"
    assert table.approximate_midpoint("1/3", "1/3") == "0.3333333333333333"
    with pytest.raises(ValueError, match="no negative"):
        table.approximate_midpoint("-1", "-1")


def test_derive_does_not_mutate_receipts_or_source():
    inputs = table.load_frozen_inputs()
    original = deepcopy(inputs)
    table.derive_rows(*inputs)
    assert inputs == original
