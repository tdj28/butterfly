"""Synthetic, local-only validation of EXP-476 release metadata preparation."""

import hashlib
import json

import pytest

from scripts import prepare_exp476_release as release


@pytest.fixture
def evidence(tmp_path):
    source = tmp_path / "inputs"
    source.mkdir()
    manifest_hash = "a" * 64
    raw = {
        "schema": "butterfly.projected-homoclinic-pilot-receipt.v2", "experiment_id": "EXP-476",
        "complete": True, "passed": False, "manifest_sha256": manifest_hash,
        "source": {"commit": release.SOURCE_COMMIT, "dirty": False},
        "cases": [{"status": status, "passed": index < 5} for index, status in enumerate(["passed"] * 5 + ["failed"] + ["skipped"] * 3)],
    }
    raw["cases"][5].update({"case": {"name": "r0.005-tol1e-8"}, "collocation": {"solver_status": 1}})
    mesh = {"experiment_id": "EXP-476", "source_commit": release.SOURCE_COMMIT, "manifest_sha256": manifest_hash}
    arithmetic = {"experiment_id": "EXP-476", "manifest_sha256": manifest_hash}
    docs = {"receipt.json": raw, "mesh-diagnostic.json": mesh, "arithmetic-diagnostic.json": arithmetic}
    pdf = tmp_path / "manuscript.pdf"
    pdf.write_bytes(b"%PDF-1.4\nSynthetic public test document.\n%%EOF\n")

    def save(*, rebind=True):
        hashes = {}
        for name, doc in docs.items():
            if rebind and name == "mesh-diagnostic.json":
                doc["receipt_sha256"] = hashes["receipt.json"]
            if rebind and name == "arithmetic-diagnostic.json":
                doc.update({"raw_receipt_sha256": hashes["receipt.json"], "mesh_diagnostic_sha256": hashes["mesh-diagnostic.json"]})
            data = json.dumps(doc).encode()
            (source / name).write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        return hashes

    hashes = save()
    return {"root": tmp_path, "source": source, "pdf": pdf, "output": tmp_path / "prepared", "docs": docs, "hashes": hashes, "save": save}


def prepare(evidence, **kwargs):
    return release.prepare_release(evidence["source"], evidence["pdf"], evidence["output"], expected_hashes=evidence["hashes"], **kwargs)


def test_prepares_only_metadata_and_preserves_original_assets(evidence):
    original = {path: path.read_bytes() for path in evidence["source"].iterdir()}
    original[evidence["pdf"]] = evidence["pdf"].read_bytes()
    result = prepare(evidence)
    assert result["release_tag"] == "research-exp476"
    assert result["experiment_passed"] is False and result["uploaded"] is False and result["copied"] is False
    assert result["case_status_counts"] == {"passed": 5, "failed": 1, "skipped": 3}
    assert {path.name for path in evidence["output"].iterdir()} == {"SHA256SUMS", "release-body.md", "asset-inventory.json"}
    assert all(path.read_bytes() == content for path, content in original.items())
    expected_names = ["receipt.json", "mesh-diagnostic.json", "arithmetic-diagnostic.json", "manuscript.pdf"]
    assert [asset["name"] for asset in result["assets"]] == expected_names
    lines = (evidence["output"] / "SHA256SUMS").read_text().splitlines()
    assert [line.split("  ")[1] for line in lines] == expected_names
    for line, asset in zip(lines, result["assets"]):
        assert line == f"{asset['sha256']}  {asset['name']}"
    body = (evidence["output"] / "release-body.md").read_text()
    assert "did **not** pass" in body and "research-core-v1 release is unchanged" in body
    assert release.PROTOCOL_TAG in body and release.SOURCE_COMMIT in body
    assert "33 figures" not in body and "61 pages" not in body
    assert str(evidence["root"]) not in body


def test_manuscript_counts_are_explicit_parameters(evidence):
    prepare(evidence, manuscript_pages=61, manuscript_figures=33)
    body = (evidence["output"] / "release-body.md").read_text()
    assert "61 pages, 33 figures" in body
    assert "counts supplied by the release operator" in body


@pytest.mark.parametrize("field", ("manuscript_pages", "manuscript_figures"))
def test_invalid_counts_fail_before_output_creation(evidence, field):
    with pytest.raises(ValueError, match="positive integer"):
        prepare(evidence, **{field: 0})
    assert not evidence["output"].exists()


def test_existing_output_directory_is_never_reused(evidence):
    evidence["output"].mkdir()
    sentinel = evidence["output"] / "SHA256SUMS"
    sentinel.write_bytes(b"existing metadata")
    with pytest.raises(ValueError, match="already exists"):
        prepare(evidence)
    assert sentinel.read_bytes() == b"existing metadata"


def test_existing_output_symlink_is_never_followed(evidence):
    evidence["output"].symlink_to(evidence["root"] / "missing-directory")
    with pytest.raises(ValueError, match="already exists"):
        prepare(evidence)
    assert evidence["output"].is_symlink()


def test_frozen_hash_mismatch_prevents_output(evidence):
    (evidence["source"] / "receipt.json").write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash mismatch"):
        prepare(evidence)
    assert not evidence["output"].exists()


@pytest.mark.parametrize("mutation, message", (
    (lambda docs: docs["receipt.json"].update(passed=True), "complete failed study"),
    (lambda docs: docs["receipt.json"]["source"].update(dirty=True), "clean frozen source"),
    (lambda docs: docs["receipt.json"]["source"].update(commit="b" * 40), "clean frozen source"),
    (lambda docs: docs["receipt.json"]["cases"][5].update(status="passed"), "five passed"),
    (lambda docs: docs["receipt.json"]["cases"][0].update(passed=False), "pass flags"),
    (lambda docs: docs["receipt.json"]["cases"][5]["collocation"].update(solver_status=0), "node-budget failure"),
    (lambda docs: docs["mesh-diagnostic.json"].update(source_commit="b" * 40), "source identity"),
    (lambda docs: docs["arithmetic-diagnostic.json"].update(manifest_sha256="b" * 64), "manifest links"),
))
def test_semantic_bindings_are_checked_beyond_hashes(evidence, mutation, message):
    mutation(evidence["docs"])
    evidence["hashes"] = evidence["save"]()
    with pytest.raises(ValueError, match=message):
        prepare(evidence)
    assert not evidence["output"].exists()


@pytest.mark.parametrize("name, field", (
    ("mesh-diagnostic.json", "receipt_sha256"),
    ("arithmetic-diagnostic.json", "raw_receipt_sha256"),
    ("arithmetic-diagnostic.json", "mesh_diagnostic_sha256"),
))
def test_diagnostic_cross_links_must_match_actual_inputs(evidence, name, field):
    evidence["docs"][name][field] = "b" * 64
    evidence["hashes"] = evidence["save"](rebind=False)
    with pytest.raises(ValueError, match="link mismatch"):
        prepare(evidence)
    assert not evidence["output"].exists()


def test_all_four_assets_are_scanned_and_pdf_secrets_are_not_echoed(evidence):
    token = "ghp_" + "a" * 36
    evidence["pdf"].write_bytes(f"%PDF-1.4\n{token}\n%%EOF\n".encode())
    with pytest.raises(ValueError, match="public-file scan rejected manuscript.pdf") as raised:
        prepare(evidence)
    assert token not in str(raised.value)
    assert not evidence["output"].exists()


def test_public_scanner_receives_each_explicit_asset(evidence, monkeypatch):
    names = []
    actual = release.check_file

    def observed(name, data):
        names.append(name)
        return actual(name, data)

    monkeypatch.setattr(release, "check_file", observed)
    prepare(evidence)
    assert names[:4] == ["receipt.json", "mesh-diagnostic.json", "arithmetic-diagnostic.json", "manuscript.pdf"]


def test_incomplete_pdf_and_symlink_assets_are_rejected(evidence):
    evidence["pdf"].write_bytes(b"%PDF-1.4\nunfinished build")
    with pytest.raises(ValueError, match="complete PDF"):
        prepare(evidence)
    assert not evidence["output"].exists()
    linked = evidence["root"] / "linked"
    linked.mkdir()
    for name in release.EXPECTED_HASHES:
        (linked / name).symlink_to(evidence["source"] / name)
    with pytest.raises(ValueError, match="non-symlink"):
        release.prepare_release(linked, evidence["pdf"], evidence["output"], expected_hashes=evidence["hashes"])


def test_cli_does_not_expose_hash_override():
    with pytest.raises(SystemExit) as raised:
        release.main(["--expected-hashes", "anything"])
    assert raised.value.code == 2
