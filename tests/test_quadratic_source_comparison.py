"""Synthetic receipt plumbing only; never enumerate target critical cycles."""

from copy import deepcopy
import json

import pytest

from scripts import compare_quadratic_source_words as comparison


def synthetic_cycle(word, parameter="1"):
    """Fabricated structural fixture, not an assertion that this is an orbit."""
    return {
        "period": len(word), "critical_anchored_word": word,
        "parameter_interval": [parameter, parameter], "parameter_interval_width": "0",
        "exact_rational_root": True, "unique_root_certified": True,
        "exact_recurrence_factor_verified": True, "primitive_period_certified": True,
        "noncritical_sign_intervals": [
            {"iterate": index, "lower": "1" if symbol == "1" else "-1",
             "upper": "1" if symbol == "1" else "-1", "sign": 1 if symbol == "1" else -1}
            for index, symbol in enumerate(word[1:], start=1)
        ],
    }


def synthetic_receipt():
    return {
        "schema": comparison.CONTROL_SCHEMA, "passed": True,
        "experiment_id": "synthetic-not-a-dynamical-result",
        "family": "f_mu(x)=1-mu*x^2", "parameter_domain": ["0", "2"],
        "protocol": {"periods": list(comparison.PERIODS)},
        "period_results": [
            {"period": period, "passed": True, "primitive_polynomial_square_free": True,
             "complete_domain_root_count": 1, "cycles": [synthetic_cycle("C1" + "0" * (period - 2))]}
            for period in comparison.PERIODS
        ],
    }


def synthetic_source():
    return {"schema": comparison.SOURCE_SCHEMA,
            "source": {"paper_sha256": comparison.PAPER_SHA256, "arxiv_id": "1201.4343v1"},
            "figure6": {"nodes": [
                {"word": word, "period": period,
                 **({"branch3_connection": True} if word in comparison.OUT_OF_MODEL else {})}
                for period, words in comparison.SOURCE_TOP_TO_BOTTOM.items() for word in words
            ]}}


def test_dictionary_has_explicit_period_two_exception_and_no_second_critical_claim():
    assert comparison.proposed_dictionary("C1") == "C1"
    assert comparison.proposed_dictionary("C101") == "CD01"
    for word in ("C2", "C01", "1C01", "C1C", "CD0"):
        with pytest.raises(ValueError):
            comparison.proposed_dictionary(word)


def test_every_source_node_and_every_fabricated_cycle_is_reported():
    result = comparison.compare_control(synthetic_receipt(), synthetic_source())
    assert result["comparison_completed"]
    assert len(result["all_source_nodes"]) == 23
    assert sum(len(row["cycles"]) for row in result["period_results"]) == 6
    assert {row["source_word"] for row in result["all_source_nodes"] if row["status"] == "out_of_model"} == {"C2", "C21"}
    assert not result["conditional_multiset_match"]
    assert not result["conditional_order_match"]
    assert not result["source_arrows_tested"]
    assert not result["rossler_nodes_verified"]
    assert "no independent proof replay" in result["receipt_validation"]


def test_order_uses_source_geometry_not_node_array_order_or_outcome_selection():
    source = synthetic_source()
    source["figure6"]["nodes"].reverse()
    control = synthetic_receipt()
    row = control["period_results"][2]
    row["cycles"] = [synthetic_cycle("C101", "1/3"), synthetic_cycle("C100", "2/3")]
    row["complete_domain_root_count"] = 2
    result = comparison.compare_control(control, source)["period_results"][2]
    assert result["source_top_to_bottom_words"] == ["CD01", "CD00"]
    assert result["conditional_order_match"]
    # Reverse only the fabricated symbolic assignment, keeping mu increasing.
    row["cycles"] = [synthetic_cycle("C100", "1/3"), synthetic_cycle("C101", "2/3")]
    result = comparison.compare_control(control, source)["period_results"][2]
    assert result["conditional_multiset_match"]
    assert not result["conditional_order_match"]
    assert all(not entry["match"] for entry in result["ordered_positions"])
    assert comparison.SOURCE_TOP_TO_BOTTOM[7][2:5] == ("CD00101", "CD00111", "CD00110")


def test_extra_missing_and_duplicate_words_are_not_silently_dropped():
    control = synthetic_receipt()
    row = control["period_results"][2]
    row["cycles"] = [synthetic_cycle("C111", "1/3"), synthetic_cycle("C111", "2/3")]
    row["complete_domain_root_count"] = 2
    result = comparison.compare_control(control, synthetic_source())["period_results"][2]
    assert result["missing_source_words"] == ["CD01", "CD00"]
    assert len(result["extra_scalar_cycles"]) == 2
    assert result["duplicate_proposed_word_counts"] == {"CD11": 2}
    assert len(result["cycles"]) == 2


@pytest.mark.parametrize("mutation", [
    lambda receipt: receipt.update(passed=False),
    lambda receipt: receipt["protocol"].update(periods=[2]),
    lambda receipt: receipt["period_results"][0].update(complete_domain_root_count=2),
    lambda receipt: receipt["period_results"][0]["cycles"][0].update(primitive_period_certified=False),
    lambda receipt: receipt["period_results"][0]["cycles"][0].update(parameter_interval=["2", "1"]),
    lambda receipt: receipt["period_results"][0]["cycles"][0].update(parameter_interval_width="1"),
    lambda receipt: receipt["period_results"][0]["cycles"][0].update(exact_rational_root=False),
    lambda receipt: receipt["period_results"][0]["cycles"][0]["noncritical_sign_intervals"][0].update(lower="-1"),
])
def test_incomplete_or_inconsistent_control_is_not_compared(mutation):
    control = synthetic_receipt()
    mutation(control)
    with pytest.raises(ValueError):
        comparison.compare_control(control, synthetic_source())


def test_unordered_or_overlapping_intervals_are_rejected_not_resorted():
    control = synthetic_receipt()
    row = control["period_results"][2]
    row["complete_domain_root_count"] = 2
    for first, second in (("2/3", "1/3"), ("1/3", "1/3")):
        row["cycles"] = [synthetic_cycle("C101", first), synthetic_cycle("C100", second)]
        with pytest.raises(ValueError, match="no reorder"):
            comparison.compare_control(control, synthetic_source())


def test_changed_source_word_or_third_branch_flag_fails_closed():
    for mutation in (lambda source: source["figure6"]["nodes"].pop(),
                     lambda source: source["figure6"]["nodes"][1].update(branch3_connection=False)):
        source = synthetic_source()
        mutation(source)
        with pytest.raises(ValueError):
            comparison.compare_control(synthetic_receipt(), source)


def test_comparison_does_not_mutate_inputs():
    control, source = synthetic_receipt(), synthetic_source()
    before = deepcopy((control, source))
    comparison.compare_control(control, source)
    assert (control, source) == before


def test_cli_binds_both_input_hashes_and_retains_mismatch_receipt(tmp_path, monkeypatch):
    control_path, source_path, output = (tmp_path / name for name in ("control.json", "source.json", "comparison.json"))
    control_path.write_text(json.dumps(synthetic_receipt()))
    source_path.write_text(json.dumps(synthetic_source()))
    source_hash = comparison.sha256_bytes(source_path.read_bytes())
    monkeypatch.setattr(comparison, "TRANSCRIPTION_SHA256", source_hash)
    control_hash = comparison.sha256_bytes(control_path.read_bytes())
    assert comparison.main(["--control", str(control_path), "--control-sha256", control_hash,
                            "--source", str(source_path), "--output", str(output)]) == 0
    result = json.loads(output.read_text())
    assert result["comparison_completed"]
    assert not result["conditional_multiset_match"]
    assert result["input_hashes"]["scalar_control"] == control_hash
    assert result["input_hashes"]["source_transcription"] == source_hash
    assert str(tmp_path) not in output.read_text()
    failed = tmp_path / "failed.json"
    assert comparison.main(["--control", str(control_path), "--control-sha256", "0" * 64,
                            "--source", str(source_path), "--output", str(failed)]) == 1
    assert "hash mismatch" in json.loads(failed.read_text())["failure"]["message"]


def test_source_hash_and_nonfinite_json_fail_closed(tmp_path, monkeypatch):
    control_path, source_path, output = (tmp_path / name for name in ("control.json", "source.json", "failed.json"))
    control_path.write_text(json.dumps(synthetic_receipt()))
    source_path.write_text(json.dumps(synthetic_source()))
    assert comparison.main(["--control", str(control_path), "--control-sha256", comparison.sha256_bytes(control_path.read_bytes()),
                            "--source", str(source_path), "--output", str(output)]) == 1
    assert "source-transcription hash mismatch" in json.loads(output.read_text())["failure"]["message"]
    with pytest.raises(ValueError, match="nonfinite"):
        comparison.read_json('{"value": NaN}')


def test_exclusive_output_preserves_existing_file_or_dangling_symlink(tmp_path):
    path = tmp_path / "receipt.json"
    comparison.write_exclusive(path, {"comparison_completed": False})
    previous = path.read_bytes()
    with pytest.raises(FileExistsError):
        comparison.write_exclusive(path, {})
    assert path.read_bytes() == previous
    link = tmp_path / "link.json"
    link.symlink_to(tmp_path / "missing.json")
    with pytest.raises(FileExistsError):
        comparison.write_exclusive(link, {})
    with pytest.raises(SystemExit):
        comparison.main(["--control", "not-read.json", "--control-sha256", "0" * 64,
                         "--output", str(path)])
