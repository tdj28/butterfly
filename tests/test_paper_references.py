from pathlib import Path

import pytest

from scripts.check_paper_references import check_paper, citation_keys, strip_comments


def paper(tmp_path: Path, source: str) -> Path:
    (tmp_path / "manuscript.tex").write_text(source, encoding="utf-8")
    (tmp_path / "references.bib").write_text(
        "@article{required, title={Required source}}\n", encoding="utf-8"
    )
    (tmp_path / "required-citations.txt").write_text("required\n", encoding="utf-8")
    return tmp_path


def test_commented_citation_does_not_satisfy_required_source(tmp_path):
    failures, _ = check_paper(paper(tmp_path, "% \\cite{required}"))
    assert "required but not cited in manuscript: required" in failures


def test_unincluded_tex_does_not_satisfy_required_source(tmp_path):
    paper(tmp_path, "No citations here.")
    (tmp_path / "abandoned-draft.tex").write_text(r"\cite{required}", encoding="utf-8")
    failures, _ = check_paper(tmp_path)
    assert "required but not cited in manuscript: required" in failures


def test_follows_manuscript_inputs(tmp_path):
    paper(tmp_path, r"\input{sections/results}")
    (tmp_path / "sections").mkdir()
    (tmp_path / "sections/results.tex").write_text(r"\citep*{required}", encoding="utf-8")
    failures, counts = check_paper(tmp_path)
    assert failures == []
    assert counts["sources"] == 2


def test_missing_input_is_failure(tmp_path):
    failures, _ = check_paper(paper(tmp_path, r"\cite{required}\input{missing}"))
    assert any("missing manuscript source:" in failure for failure in failures)


def test_duplicate_bibtex_key_is_failure(tmp_path):
    paper(tmp_path, r"\cite{required}")
    with (tmp_path / "references.bib").open("a", encoding="utf-8") as bibliography:
        bibliography.write("@article{required, title={Accidental duplicate}}\n")
    failures, _ = check_paper(tmp_path)
    assert "duplicate BibTeX keys: required" in failures


@pytest.mark.parametrize("filename", ["figure", "figure.png"])
def test_missing_graphics_are_detected(tmp_path, filename):
    paper(tmp_path, r"\cite{required}\includegraphics[width=\textwidth]{" + filename + "}")
    failures, _ = check_paper(tmp_path)
    assert f"missing manuscript figure: {filename}" in failures
    (tmp_path / "figure.png").touch()
    assert check_paper(tmp_path)[0] == []


def test_escaped_percent_and_starred_optional_citation_arguments():
    assert citation_keys(r"50\% \citep*[see][p. 2]{first, second} % \cite{ignored}") == {
        "first", "second"
    }
    assert strip_comments(r"line break\\% comment") == r"line break\\"
