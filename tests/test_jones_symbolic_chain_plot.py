"""Coverage and claim-boundary tests for an exact source-derived diagram."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from scripts import plot_jones_symbolic_chain as plot


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTION = ROOT / "experiments/source-transcriptions/jones2012-figures-2-and-6.json"
AUDIT = ROOT / "experiments/source-transcriptions/jones2012-figure6-asset-audit.json"


@pytest.fixture
def source_documents():
    return json.loads(TRANSCRIPTION.read_text()), json.loads(AUDIT.read_text())


def test_frozen_bytes_have_expected_hash_bindings():
    assert plot.file_hash(TRANSCRIPTION) == plot.TRANSCRIPTION_SHA256
    assert plot.file_hash(AUDIT) == plot.ASSET_AUDIT_SHA256
    graph = plot.load_graph(TRANSCRIPTION, AUDIT)
    assert len(graph["nodes"]) == 23


def test_all_words_periods_categories_and_four_orphans_are_preserved(source_documents):
    source, audit = source_documents
    before = deepcopy(source), deepcopy(audit)
    graph = plot.graph_from_transcription(source, audit)
    assert (source, audit) == before
    assert {row["word"] for row in graph["nodes"]} == set(plot.WORDS)
    assert all(row["period"] == len(row["word"]) for row in graph["nodes"])
    assert {row["period"] for row in graph["nodes"]} == set(range(2, 8))
    assert graph["edge_counts"] == {
        "source_matched_p_to_p_plus_1": 10,
        "visual_only": 1,
        "text_branch3_connection": 2,
        "text_period_double": 1,
    }
    assert len(graph["edges"]) == 14
    assert set(graph["orphan_words"]) == {"CD00101", "CD00110", "CD01101", "CD01111"}
    assert not any(edge[endpoint] in graph["orphan_words"] for edge in graph["edges"] for endpoint in ("source", "target"))


def test_isolated_origin_flags_and_doubling_marker_do_not_invent_a_doubling_link(source_documents):
    graph = plot.graph_from_transcription(*source_documents)
    isolated = {row["word"] for row in graph["nodes"] if row.get("isolated_branch3_origin")}
    assert isolated == {"CD011", "CD0010", "CD0111", "CD00101", "CD01101", "CD01111"}
    assert [row["word"] for row in graph["nodes"] if row.get("period_double_marker")] == ["CD0010"]
    doubling = [row for row in graph["edges"] if row["category"] == "text_period_double"]
    assert [(row["source"], row["target"]) for row in doubling] == [("C1", "CD01")]
    assert [(row["source"], row["target"]) for row in graph["edges"] if row["source"] == "CD0010"] == [("CD0010", "CD00010")]


def test_original_claims_never_become_modern_orbit_validation(source_documents):
    graph = plot.graph_from_transcription(*source_documents)
    assert graph["modern_orbit_validated"] is False
    assert graph["parameter_coordinates_assigned"] is False
    assert all(row["modern_orbit_validated"] is False for row in graph["edges"])
    assert "not new orbit validation" in graph["claim_boundary"]
    assert "not modern numerical qualification" in graph["claim_boundary"]
    assert "original report's geometry-and-symbol evidence category" in graph["claim_boundary"]


@pytest.mark.parametrize("change, message", [
    (lambda source: source.update(schema="wrong"), "frozen Jones"),
    (lambda source: source["source"].update(arxiv_id="1201.4343v2"), "paper identity"),
    (lambda source: source["source"].update(paper_sha256="0" * 64), "paper identity"),
    (lambda source: source.update(claim_boundary="All transitions are now verified."), "modern numerical validation"),
    (lambda source: source["figure6"]["nodes"].pop(), "23 distinct"),
    (lambda source: source["figure6"]["nodes"].append({"word": "CD000000", "period": 8}), "23 distinct"),
    (lambda source: source["figure6"]["nodes"].__setitem__(1, deepcopy(source["figure6"]["nodes"][0])), "23 distinct"),
    (lambda source: source["figure6"]["nodes"][0].update(period=4), "word length"),
    (lambda source: source["figure6"]["nodes"][0].update(period=True), "word length"),
    (lambda source: source["figure6"]["nodes"][0].update(isolated_branch3_origin=True), "isolated_branch3_origin"),
    (lambda source: source["figure6"]["nodes"][1].update(branch3_connection=False), "branch3_connection"),
    (lambda source: source["figure6"]["nodes"][11].update(period_double_marker=False), "period_double_marker"),
    (lambda source: source["figure6"]["nodes"][0].update(modern_orbit_validated=True), "untranscribed metadata"),
    (lambda source: source["figure6"]["matched_p_to_p_plus_1_transitions"].pop(), "ten source-matched"),
    (lambda source: source["figure6"]["matched_p_to_p_plus_1_transitions"].append({"source": "CD0010", "target": "CD00101"}), "ten source-matched"),
    (lambda source: source["figure6"]["matched_p_to_p_plus_1_transitions"][0].update(target="CD01"), "ten source-matched"),
    (lambda source: source["figure6"]["visual_only_transition"].update(target="CD01111"), "visual-only"),
    (lambda source: source["figure6"]["explicit_text_relationships"][0].update(kind="period-double"), "remain distinct"),
    (lambda source: source["figure6"]["explicit_text_relationships"].append({"source": "CD0010", "target": "CD00101", "kind": "period-double"}), "remain distinct"),
])
def test_transcription_mutations_cannot_rewrite_graph_claims(source_documents, change, message):
    source, audit = source_documents
    change(source)
    with pytest.raises(ValueError, match=message):
        plot.graph_from_transcription(source, audit)


@pytest.mark.parametrize("change, message", [
    (lambda audit: audit.update(schema="wrong"), "asset audit"),
    (lambda audit: audit["source"].update(paper_sha256="0" * 64), "paper identity"),
    (lambda audit: audit["frozen_transcription"].update(sha256="0" * 64), "bind the frozen transcription"),
    (lambda audit: audit["attachment_assessment"].update(status="fully resolved"), "associations must remain unresolved"),
])
def test_asset_audit_cannot_silently_upgrade_unresolved_associations(source_documents, change, message):
    source, audit = source_documents
    change(audit)
    with pytest.raises(ValueError, match=message):
        plot.graph_from_transcription(source, audit)


def test_layout_covers_every_word_once_and_uses_period_not_parameter_coordinates():
    positions = plot.graph_positions()
    assert set(positions) == set(plot.WORDS)
    assert len(set(positions.values())) == 23
    for word, (horizontal, vertical) in positions.items():
        assert horizontal == 1.8 * (len(word) - 2)
        assert 0 <= vertical <= 8


@pytest.mark.parametrize("which, expected", [("transcription", "transcription SHA-256"), ("audit", "asset audit SHA-256")])
def test_modified_bytes_are_rejected_before_figure_creation(tmp_path, which, expected):
    source, audit = TRANSCRIPTION, AUDIT
    changed = tmp_path / "changed.json"
    changed.write_bytes((source if which == "transcription" else audit).read_bytes() + b"\n")
    if which == "transcription":
        source = changed
    else:
        audit = changed
    output, receipt = tmp_path / "figure.png", tmp_path / "receipt.json"
    with pytest.raises(SystemExit, match=expected):
        plot.main(["--transcription", str(source), "--asset-audit", str(audit), "--output", str(output), "--receipt", str(receipt)])
    assert not output.exists() and not receipt.exists()


def test_source_only_render_has_full_provenance_without_orbit_integrations(monkeypatch, tmp_path):
    def no_integration(*args, **kwargs):
        pytest.fail("source graph must not integrate or validate an orbit")

    monkeypatch.setattr("scipy.integrate.solve_ivp", no_integration)
    monkeypatch.setattr("scipy.integrate.solve_bvp", no_integration)
    monkeypatch.setattr(plot, "git_value", lambda *args: "" if args[0] == "status" else "test-commit")
    output, receipt_path = tmp_path / "source-graph.png", tmp_path / "receipt.json"
    assert plot.main(["--output", str(output), "--receipt", str(receipt_path), "--dpi", "40"]) == 0
    receipt = json.loads(receipt_path.read_text())
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert receipt["figure_sha256"] == hashlib.sha256(output.read_bytes()).hexdigest()
    assert receipt["transcription_sha256"] == plot.TRANSCRIPTION_SHA256
    assert receipt["asset_audit_sha256"] == plot.ASSET_AUDIT_SHA256
    assert receipt["node_words"] == list(plot.WORDS)
    assert len(receipt["edges"]) == 14
    assert set(receipt["orphan_words"]) == plot.ORPHAN_WORDS
    assert receipt["raw_artifact_required_to_regenerate_figure"] is False
    assert receipt["modern_orbit_validated"] is False
    assert receipt["parameter_coordinates_assigned"] is False
    assert all(edge["modern_orbit_validated"] is False for edge in receipt["edges"])
