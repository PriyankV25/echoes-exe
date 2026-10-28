"""
Tests for Grounded Citations Validator and Retrieval
"""
import pytest
from core.citations import CitationValidator
from core.retrieval import EvidenceRetriever


def test_citation_extraction():
    sample_text = (
        "The project was created by Arthur [Source: commit:7190e45]. "
        "The package dependencies are listed in [Source: package.json:dependencies]. "
        "[FACT] No releases were published after 2017."
    )
    cites = CitationValidator.extract_citations(sample_text)
    assert len(cites) == 2
    assert "commit:7190e45" in cites[0]
    assert "package.json:dependencies" in cites[1]


def test_citation_validation():
    chunks = [
        {"chunk_id": "chk_001", "source_path": "package.json", "citation": "package.json:dependencies", "content": "dependencies"},
        {"chunk_id": "chk_002", "source_path": "commit:7190e45", "citation": "commit 7190e45", "content": "Initial commit"}
    ]

    valid_response = "[FACT] The dependencies are preserved [Source: package.json:dependencies]."
    res = CitationValidator.validate_citations(valid_response, chunks)
    assert len(res["valid_citations"]) == 1
    assert len(res["unverified_citations"]) == 0
    assert res["has_epistemic_labels"] is True
    assert res["confidence_score"] >= 0.9


def test_evidence_retriever():
    chunks = [
        {"chunk_id": "c1", "source_type": "commit", "content": "Initial commit created by Arthur introducing webpack."},
        {"chunk_id": "c2", "source_type": "manifest", "content": "Python dependencies requirements.txt containing click and requests."},
        {"chunk_id": "c3", "source_type": "readme", "content": "Documentation explaining particle canvas library usage and installation."}
    ]
    retriever = EvidenceRetriever(chunks)
    results = retriever.search("webpack particle", top_k=2)
    assert len(results) > 0
    # Chunks mentioning webpack or particle should rank high
    assert any(c["chunk_id"] in ("c1", "c3") for c in results)
