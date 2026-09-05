"""Protect the current anonymous draft and its main symbolic explanation."""

from pathlib import Path
import re


PAPER = Path(__file__).resolve().parents[1] / "paper"


def test_draft_title_author_is_blank():
    source = (PAPER / "manuscript.tex").read_text()
    authors = re.findall(r"\\author\s*\{([^{}]*)\}", source)
    assert authors == [""]


def test_draft_pdf_author_metadata_is_explicitly_blank():
    source = (PAPER / "manuscript.tex").read_text()
    authors = re.findall(r"pdfauthor\s*=\s*\{([^{}]*)\}", source)
    assert authors == [""]


def test_symbolic_chain_is_in_main_article_with_source_credit():
    main = (PAPER / "manuscript.tex").read_text()
    main_article = main.split(r"\appendix", 1)[0]
    assert r"\input{sections/05-topology-tests}" in main_article
    symbolic = (PAPER / "sections/05-topology-tests.tex").read_text()
    assert "figures/fig33-jones-symbolic-chain.png" in symbolic
    assert r"\label{fig:symbolic-chain}" in symbolic
    assert r"\citep{jones2012topological}" in symbolic
    assert r"\label{eq:jones-zero-insertion}" in symbolic
    assert r"\label{eq:jones-insertion-example}" in symbolic


def test_symbolic_hypothesis_precedes_methods_and_results():
    main_article = (PAPER / "manuscript.tex").read_text().split(r"\appendix", 1)[0]
    inputs = re.findall(r"\\input\{([^{}]+)\}", main_article)
    hypothesis = inputs.index("sections/05-topology-tests")
    assert inputs.index("sections/02-mathematical-objects") < hypothesis
    assert hypothesis < inputs.index("sections/03-methods")
    assert hypothesis < inputs.index("sections/04-results")
