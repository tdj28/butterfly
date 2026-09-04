import pytest

from scripts.check_public_repository import check_file, worktree_contents


def test_empty_example_is_safe_but_local_variants_are_not():
    assert check_file(".env-example", b"RUNPOD_API_KEY=\n") == []
    assert check_file(".env.local", b"")
    assert check_file(".env.backup", b"")
    assert check_file(".env-example.bak", b"")


def test_template_rejects_nonempty_values_even_for_unknown_providers():
    assert check_file(".env-example", b"CUSTOM_API_KEY=example\n")
    assert check_file(".env-example", b"# CUSTOM_API_KEY=example\n") == []


@pytest.mark.parametrize("assignment", [
    b"  CUSTOM_API_KEY=example\n",
    b"export CUSTOM_API_KEY=example\n",
    b"\texport CUSTOM_API_KEY = example\n",
])
def test_template_rejects_whitespace_and_export_assignments(assignment):
    assert check_file(".env-example", assignment) == [
        "environment template contains a nonempty value"
    ]


def test_worktree_scan_reads_broken_link_text_without_following_it(tmp_path):
    target = "ghp_" + "a" * 36
    link = tmp_path / "broken-link"
    link.symlink_to(target)
    data = worktree_contents(link)
    assert data == target.encode()
    assert check_file(link.name, data) == ["provider credential"]
    assert worktree_contents(tmp_path / "deleted-file") is None


def test_worktree_scan_does_not_read_live_symlink_target(tmp_path):
    target = tmp_path / "private-target"
    target.write_bytes(b"private contents")
    link = tmp_path / "link"
    link.symlink_to("private-target")
    assert worktree_contents(link) == b"private-target"


def test_detector_never_returns_matching_credential_contents():
    token = b"ghp_" + b"a" * 36
    issues = check_file("notes.txt", b"credential: " + token)
    assert issues == ["provider credential"]
    assert token.decode() not in str(issues)


def test_private_keys_are_rejected_in_arbitrary_files():
    header = b"-----BEGIN " + b"OPENSSH PRIVATE KEY-----"
    assert check_file("notes.txt", header) == ["private key"]
    assert check_file("worker.pem", b"")
