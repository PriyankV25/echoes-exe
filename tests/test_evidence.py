"""
Tests for Evidence Extraction and Heuristics
"""
import pytest
from pathlib import Path
from core.evidence_extractor import EvidenceExtractor
from core.health_analyzer import HealthAnalyzer


def test_sample_repo_extraction():
    sample_dir = Path("samples/canvas-nest-legacy")
    extractor = EvidenceExtractor(sample_dir, source_meta={"repo_name": "canvas-nest-legacy", "source_type": "sample"})
    evidence = extractor.extract_all()

    assert evidence["project_name"] == "canvas-nest-legacy"
    assert evidence["primary_language"] == "JavaScript"
    assert evidence["total_files"] > 0
    assert len(evidence["evidence_chunks"]) > 0

    # Test Git verifiable metrics
    git = evidence["git_evidence"]
    assert git["available"] is True
    assert git["total_commits"] == 2
    assert git["first_commit"]["short_hash"] is not None
    assert git["latest_commit"]["short_hash"] is not None
    assert "Arthur Pendelton" in git["first_commit"]["author"]
    assert git["lifespan_days"] == 587
    assert git["days_since_last_commit"] > 2000

    # Test Manifest dependencies
    manifests = evidence["manifests"]
    assert "package_json" in manifests
    assert "webpack" in manifests["package_json"]["dependencies"]


def test_python_sample_extraction():
    sample_dir = Path("samples/phantom-cli-py")
    extractor = EvidenceExtractor(sample_dir, source_meta={"repo_name": "phantom-cli-py", "source_type": "sample"})
    evidence = extractor.extract_all()

    assert evidence["project_name"] == "phantom-cli-py"
    assert evidence["primary_language"] == "Python"
    assert "requirements_txt" in evidence["manifests"]
    assert evidence["manifests"]["requirements_txt"]["count"] >= 4

    git = evidence["git_evidence"]
    assert git["available"] is True
    assert "Eleanor Vance" in git["first_commit"]["author"]


def test_health_analyzer_metrics():
    sample_dir = Path("samples/canvas-nest-legacy")
    extractor = EvidenceExtractor(sample_dir)
    evidence = extractor.extract_all()

    health = HealthAnalyzer.analyze(evidence)
    assert 0 <= health["overall_health_score"] <= 100
    assert health["activity"]["state"] == "dormant"
    assert "Long-Term Inactivity" in health["activity"]["label"]
    assert len(health["documentation"]["findings"]) > 0
