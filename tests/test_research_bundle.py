import io
import json
from pathlib import Path
import tarfile

import pytest

from scripts import research_bundle as bundle


@pytest.fixture
def source(tmp_path, monkeypatch):
    root = tmp_path / "source"
    root.mkdir()
    name = "artifacts/EXP-001/receipt.json"
    data = b'{"passed":true}\n'
    (root / name).parent.mkdir(parents=True)
    (root / name).write_bytes(data)
    (root / "experiments").mkdir()
    spec = {
        "schema": bundle.SPEC_SCHEMA, "bundle_id": "test-core", "license": "GPL-2.0-only",
        "scope": "Synthetic test only", "files": [bundle.file_entry(name, data, "test input")],
    }
    (root / bundle.SPEC_PATH).write_bytes(bundle.canonical_json(spec))
    for name in ("LICENSE", "uv.lock", "pyproject.toml"):
        (root / name).write_bytes(b"test support file\n")
    monkeypatch.setattr(bundle, "source_revision", lambda *args, **kwargs: {
        "commit": "a" * 40, "tree": "b" * 40, "dirty": False,
    })
    return root


def build(source, tmp_path):
    output = tmp_path / "bundle.tar.gz"
    return output, bundle.build_archive(source, output)


def repack(path: Path, payload: dict[str, bytes], extra: tarfile.TarInfo | None = None):
    with tarfile.open(path, mode="w:gz") as archive:
        for name, data in payload.items():
            member = tarfile.TarInfo(name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        if extra is not None:
            archive.addfile(extra)
    return bundle.file_sha256(path)


def archive_payload(path, checksum):
    index, payload = bundle.read_archive(path, expected_sha256=checksum)
    return {**payload, "index.json": bundle.canonical_json(index)}


def test_deterministic_export_and_verified_extraction(source, tmp_path):
    first, result = build(source, tmp_path)
    second = tmp_path / "second.tar.gz"
    bundle.build_archive(source, second)
    assert first.read_bytes() == second.read_bytes()
    destination = tmp_path / "extracted"
    index = bundle.extract_archive(first, destination, expected_sha256=result["sha256"])
    assert bundle.verify_bundle(destination) == index
    assert len(index["files"]) == 5
    assert (destination / "artifacts/EXP-001/receipt.json").read_bytes() == b'{"passed":true}\n'


def test_export_rejects_changed_frozen_input(source, tmp_path):
    (source / "artifacts/EXP-001/receipt.json").write_bytes(b"changed")
    with pytest.raises(ValueError, match="frozen input hash/size mismatch"):
        build(source, tmp_path)


def test_export_rejects_symlink_source(source, tmp_path):
    path = source / "artifacts/EXP-001/receipt.json"
    path.unlink()
    path.symlink_to(source / "LICENSE")
    with pytest.raises(ValueError, match="symlink"):
        build(source, tmp_path)


def test_export_does_not_overwrite_existing_path(source, tmp_path):
    output = tmp_path / "bundle.tar.gz"
    output.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        bundle.build_archive(source, output)
    assert output.read_bytes() == b"keep"


def test_extract_does_not_overwrite_or_merge(source, tmp_path):
    archive, result = build(source, tmp_path)
    destination = tmp_path / "existing"
    destination.mkdir()
    (destination / "keep").write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        bundle.extract_archive(archive, destination, expected_sha256=result["sha256"])
    assert (destination / "keep").read_bytes() == b"keep"


def test_wrong_archive_checksum_creates_no_destination(source, tmp_path):
    archive, _ = build(source, tmp_path)
    destination = tmp_path / "output"
    with pytest.raises(ValueError, match="archive SHA-256 mismatch"):
        bundle.extract_archive(archive, destination, expected_sha256="0" * 64)
    assert not destination.exists()


@pytest.mark.parametrize("name", ["../outside", "/absolute", "a/../../outside", "./file", "a//file", "C:/file", "a\\file"])
def test_unsafe_paths_rejected(name):
    with pytest.raises(ValueError, match="archive path"):
        bundle.safe_name(name)


@pytest.mark.parametrize("kind", [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.DIRTYPE])
def test_nonregular_tar_members_rejected_before_extraction(source, tmp_path, kind):
    archive, result = build(source, tmp_path)
    payload = archive_payload(archive, result["sha256"])
    extra = tarfile.TarInfo("bad-link")
    extra.type = kind
    extra.linkname = "../outside"
    checksum = repack(archive, payload, extra)
    destination = tmp_path / "output"
    with pytest.raises(ValueError, match="regular archive files"):
        bundle.extract_archive(archive, destination, expected_sha256=checksum)
    assert not destination.exists()


def test_duplicate_tar_member_rejected(source, tmp_path):
    archive, result = build(source, tmp_path)
    payload = archive_payload(archive, result["sha256"])
    checksum = repack(archive, payload, tarfile.TarInfo("LICENSE"))
    with pytest.raises(ValueError, match="duplicate"):
        bundle.read_archive(archive, expected_sha256=checksum)


def test_unlisted_member_rejected(source, tmp_path):
    archive, result = build(source, tmp_path)
    payload = archive_payload(archive, result["sha256"])
    checksum = repack(archive, {**payload, "extra.json": b"{}"})
    with pytest.raises(ValueError, match="exact index inventory"):
        bundle.read_archive(archive, expected_sha256=checksum)


def test_rehashed_data_cannot_bypass_frozen_policy(source, tmp_path):
    archive, result = build(source, tmp_path)
    payload = archive_payload(archive, result["sha256"])
    name = "artifacts/EXP-001/receipt.json"
    payload[name] = b'{"passed":false}\n'
    index = json.loads(payload["index.json"])
    index["files"] = [bundle.file_entry(name, payload[name], "forged") if entry["path"] == name else entry for entry in index["files"]]
    payload["index.json"] = bundle.canonical_json(index)
    checksum = repack(archive, payload)
    with pytest.raises(ValueError, match="frozen policy hash/size mismatch"):
        bundle.read_archive(archive, expected_sha256=checksum)


def test_changed_extracted_file_rejected(source, tmp_path):
    archive, result = build(source, tmp_path)
    destination = tmp_path / "output"
    bundle.extract_archive(archive, destination, expected_sha256=result["sha256"])
    (destination / "LICENSE").write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash/size mismatch"):
        bundle.verify_bundle(destination)


def test_missing_and_extra_extracted_files_rejected(source, tmp_path):
    archive, result = build(source, tmp_path)
    destination = tmp_path / "output"
    bundle.extract_archive(archive, destination, expected_sha256=result["sha256"])
    (destination / "extra").write_bytes(b"extra")
    with pytest.raises(ValueError, match="exact index inventory"):
        bundle.verify_bundle(destination)
    (destination / "extra").unlink()
    (destination / "LICENSE").unlink()
    with pytest.raises(ValueError, match="exact index inventory"):
        bundle.verify_bundle(destination)


def test_replay_requires_matching_active_policy_and_environment(source, tmp_path):
    from scripts.replay_research_bundle import check_replay_environment

    archive, result = build(source, tmp_path)
    destination = tmp_path / "output"
    bundle.extract_archive(archive, destination, expected_sha256=result["sha256"])
    check_replay_environment(destination, source)
    (source / "uv.lock").write_bytes(b"different environment")
    with pytest.raises(ValueError, match="active checkout differs"):
        check_replay_environment(destination, source)


def test_release_export_requires_clean_git_source(monkeypatch, tmp_path):
    def git(command, **kwargs):
        if command[1:3] == ["status", "--porcelain"]:
            return b" M changed-source.py\n"
        return ("a" * 40 + "\n").encode()

    monkeypatch.setattr(bundle.subprocess, "check_output", git)
    with pytest.raises(ValueError, match="clean source checkout"):
        bundle.source_revision(tmp_path, allow_dirty=False)
    assert bundle.source_revision(tmp_path, allow_dirty=True)["dirty"] is True


def test_tar_path_traversal_is_rejected_before_writing(source, tmp_path):
    archive, result = build(source, tmp_path)
    payload = archive_payload(archive, result["sha256"])
    checksum = repack(archive, {**payload, "../outside": b"no"})
    destination = tmp_path / "output"
    with pytest.raises(ValueError, match="unsafe archive path"):
        bundle.extract_archive(archive, destination, expected_sha256=checksum)
    assert not destination.exists()
    assert not (tmp_path / "outside").exists()


def test_oversized_tar_member_is_rejected(source, tmp_path, monkeypatch):
    archive, result = build(source, tmp_path)
    payload = archive_payload(archive, result["sha256"])
    # Use a valid small archive rather than an incomplete oversized header:
    # newer tarfile versions reject nonempty members without a file object.
    limit = max(len(data) for name, data in payload.items() if name != "index.json")
    monkeypatch.setattr(bundle, "MAX_FILE_BYTES", limit)
    checksum = repack(archive, {**payload, "large.json": b"x" * (limit + 1)})
    with pytest.raises(ValueError, match="size limit"):
        bundle.read_archive(archive, expected_sha256=checksum)
