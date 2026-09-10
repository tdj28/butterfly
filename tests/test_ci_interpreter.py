"""Selection validation does not skip tests or modify frozen timeouts."""
from pathlib import Path
import pytest
from scripts.check_ci_interpreter import validate


@pytest.mark.parametrize('requested,actual', [('3.12', (3, 12, 11)), ('3.13', (3, 13, 11)), ('3.12.11', (3, 12, 11))])
def test_matching_managed_interpreter(tmp_path, requested, actual):
    assert validate(tmp_path/'cpython'/'install', str(tmp_path), actual, requested)


@pytest.mark.parametrize('kind', ['system', 'sibling', 'relative', 'wrong-minor', 'wrong-patch', 'missing-root', 'missing-version'])
def test_fallback_or_wrong_version_rejected(tmp_path, kind):
    root, prefix, actual, wanted = str(tmp_path), tmp_path/'cpython', (3, 12, 11), '3.12'
    if kind == 'system': prefix = '/usr'
    elif kind == 'sibling': prefix = str(tmp_path)+'-other/cpython'
    elif kind == 'relative': root = 'relative-root'
    elif kind == 'wrong-minor': wanted = '3.13'
    elif kind == 'wrong-patch': wanted = '3.12.3'
    elif kind == 'missing-root': root = None
    else: wanted = None
    with pytest.raises(ValueError): validate(prefix, root, actual, wanted)


def test_workflow_requires_managed_selection_without_test_filters():
    text = (Path(__file__).resolve().parents[1]/'.github/workflows/checks.yml').read_text()
    assert 'UV_MANAGED_PYTHON: "true"' in text
    assert 'uv run --no-sync python scripts/check_ci_interpreter.py' in text
    assert 'uv run --no-sync python -m pytest -q\n' in text
