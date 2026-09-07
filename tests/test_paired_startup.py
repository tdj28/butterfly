"""Target-free sealed bootstrap controls and narrow import-policy regressions."""
import copy
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

import pytest

from scripts.build_paired_runtime import build, ROOT, SOURCE_MAP


API = runpy.run_path(str(ROOT/"python/butterfly/_paired_startup.py"))


@pytest.fixture(scope="module")
def sealed(tmp_path_factory):
    directory = tmp_path_factory.mktemp("sealed-paired")/"bundle"
    built = build(directory, startup_guard_seconds=20.)
    return directory, built, API["load_contract"](directory, built["sha256"])


def test_build_is_exact_and_cannot_overwrite(sealed):
    root, built, contract = sealed
    assert set(contract["source_files"]) == set(SOURCE_MAP)
    assert built["source_files"] == 18 and not built["target_execution_authorized"]
    assert API["verify_runtime"](root, contract) == root
    assert not (root/"python/butterfly/return_map.py").exists()
    with pytest.raises(FileExistsError):
        build(root)


@pytest.mark.parametrize("kind", ["missing", "extra", "changed", "symlink", "source-map"])
def test_inventory_rejects_changed_bundle_before_numerics(sealed, tmp_path, kind):
    original, _, contract = sealed
    root = tmp_path/"bundle"
    shutil.copytree(original, root)
    path = root/"python/butterfly/models.py"
    if kind == "missing": path.rename(tmp_path/"withheld-models.py")
    elif kind == "extra": (root/"surprise.py").write_text("raise AssertionError('must not run')")
    elif kind == "changed": path.write_text("raise AssertionError('must not run')")
    elif kind == "source-map":
        contract = copy.deepcopy(contract)
        contract["source_map"]["worker.py"]["sha256"] = "0"*64
    else:
        path.rename(tmp_path/"withheld-models.py")
        path.symlink_to(tmp_path/"withheld-models.py")
    with pytest.raises(ValueError):
        API["verify_runtime"](root, contract)


@pytest.mark.parametrize("kind", ["digest", "bytes", "authorization"])
def test_contract_is_externally_bound_not_authorization(sealed, tmp_path, kind):
    original, built, contract = sealed
    root = tmp_path/"bundle"
    shutil.copytree(original, root)
    digest = built["sha256"]
    if kind == "digest": digest = "0"*64
    elif kind == "bytes":
        with (root/"runtime-contract.json").open("ab") as stream:
            stream.write(b"\n")
    else:
        contract = copy.deepcopy(contract)
        contract["target_execution_authorized"] = True
        (root/"runtime-contract.json").write_text(json.dumps(contract))
        digest = API["sha256"](root/"runtime-contract.json")
    with pytest.raises(ValueError):
        API["load_contract"](root, digest)


def test_environment_constructor_does_not_copy_host_secrets(monkeypatch):
    monkeypatch.setenv("PAIRED_TEST_SECRET", "synthetic-only")
    monkeypatch.setenv("PYTHONPATH", "/unbound-checkout")
    env = API["canonical_environment"]()
    assert "PAIRED_TEST_SECRET" not in env and "PYTHONPATH" not in env
    assert env["LC_ALL"] == "C" and env["OPENBLAS_NUM_THREADS"] == "1"


@pytest.mark.parametrize("relative", ["../escape", "/absolute", "a/../file", "./file", ""])
def test_noncanonical_inventory_paths_rejected(tmp_path, relative):
    with pytest.raises(ValueError):
        API["safe_file"](tmp_path, relative)


def test_import_gate_rejects_outside_or_changed_files_before_loader(sealed, tmp_path):
    root, _, contract = sealed
    finder = API["BoundImports"](root, contract)
    finder.check("butterfly.models", str(root/"python/butterfly/models.py"))
    foreign = tmp_path/"outside.py"
    foreign.write_text("raise AssertionError('must not execute')")
    with pytest.raises(ImportError, match="outside sealed"):
        finder.check("outside", str(foreign))
    bad = copy.deepcopy(contract)
    bad["source_files"]["python/butterfly/models.py"]["sha256"] = "0"*64
    with pytest.raises(ImportError, match="bytes changed"):
        API["BoundImports"](root, bad).check("butterfly.models", str(root/"python/butterfly/models.py"))


@pytest.mark.parametrize("kind", ["stdlib", "dependency-root", "duplicate-dependency"])
def test_forged_runtime_roots_cannot_widen_import_policy(sealed, kind):
    root, _, original = sealed
    contract = copy.deepcopy(original)
    if kind == "stdlib": contract["stdlib"] = "/"
    elif kind == "dependency-root": contract["dependency_roots"][0]["path"] = str(root)
    else: contract["dependency_roots"].append(copy.deepcopy(contract["dependency_roots"][0]))
    with pytest.raises(ValueError):
        API["verify_runtime"](root, contract)


@pytest.mark.parametrize("kind", ["foreign", "sibling", "multiple", "alias"])
def test_namespace_exception_cannot_expand_search_roots(sealed, tmp_path, kind):
    root, _, contract = sealed
    # Older SciPy versions need not contain this namespace; construct its exact
    # prospective path in a private fake inventory for this policy-only test.
    fake_site = tmp_path/"site"
    package = fake_site/"scipy/_external"
    package.mkdir(parents=True)
    (package/"version.py").write_text("# synthetic")
    fake = copy.deepcopy(contract)
    fake["site_packages"] = str(fake_site)
    fake["dependency_roots"] = [{"path": str(fake_site/"scipy"), "files": API["inventory"](fake_site/"scipy")}]
    finder = API["BoundImports"](root, fake)
    finder.check_namespace("scipy._external", [str(package)])
    if kind == "foreign": locations = [str(tmp_path)]
    elif kind == "sibling": locations = [str(fake_site/"scipy")]
    elif kind == "multiple": locations = [str(package), str(tmp_path)]
    else:
        alias = tmp_path/"alias"
        alias.symlink_to(package, target_is_directory=True)
        locations = [str(alias)]
    with pytest.raises(ImportError):
        finder.check_namespace("scipy._external", locations)


def test_startup_receipts_are_exclusive(tmp_path):
    path = tmp_path/"receipt.json"
    API["write_json"](path, {"passed": True})
    with pytest.raises(FileExistsError):
        API["write_json"](path, {"passed": False})
    assert json.loads(path.read_bytes()) == {"passed": True}


@pytest.mark.parametrize("case", ["correct", "wrong-env", "no-isolation", "execute"])
def test_exact_worker_entrypoint_has_no_target_authority(sealed, tmp_path, case):
    if os.name != "posix":
        pytest.skip("worker parent guard requires POSIX sessions")
    root, built, contract = sealed
    evidence = tmp_path/"evidence"
    evidence.mkdir()
    (tmp_path/"numpy.py").write_text("raise AssertionError('unsealed cwd imported')")
    env = API["canonical_environment"]()
    if case == "wrong-env": env["OMP_NUM_THREADS"] = "2"
    flags = ["-I", "-S", "-B", "-X", "utf8=1"]
    if case == "no-isolation": flags.remove("-I")
    command = [sys.executable, *flags, str(root/"worker.py"), "--contract-sha256", built["sha256"],
        "--output-dir", str(evidence), "--mode", "execute" if case == "execute" else "startup"]
    # Keep the parent liveness pipe open until the child finishes. communicate()
    # would close it first, intentionally triggering the guard instead of startup.
    with (tmp_path/"stdout").open("wb") as stdout, (tmp_path/"stderr").open("wb") as stderr:
        process = subprocess.Popen(command, env=env, cwd=tmp_path, stdin=subprocess.PIPE,
            stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=30)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            process.stdin.close()
    if case in ("correct", "execute"):
        receipt = json.loads((evidence/"startup.json").read_bytes())
        assert receipt["environment"] == contract["environment"] and receipt["guard_alive"]
        assert receipt["target_trajectories_generated"] == 0 and not receipt["target_execution_authorized"]
        assert "butterfly.paired_campaign" in receipt["loaded_modules"]
        assert "butterfly.return_map" not in receipt["loaded_modules"]
        assert not list(root.rglob("*.pyc"))
    if case == "correct":
        assert code == 0, (tmp_path/"stderr").read_text()
    else:
        assert code != 0
        message = json.loads((evidence/"failure.json").read_bytes())["message"]
        assert {"wrong-env": "environment differs", "no-isolation": "requires -I -S", "execute": "target execution refused"}[case] in message
