"""
Tests for Security Guards (SSRF, Path Traversal, Zip Slip)
"""
import pytest
import zipfile
from pathlib import Path
from core.repository_loader import RepositoryLoader, SecurityValidationError


def test_github_url_ssrf_protection():
    # Valid URLs
    owner, repo = RepositoryLoader.validate_github_url("https://github.com/expressjs/express")
    assert owner == "expressjs"
    assert repo == "express"

    owner2, repo2 = RepositoryLoader.validate_github_url("https://github.com/psf/requests.git")
    assert owner2 == "psf"
    assert repo2 == "requests"

    # Malicious or internal URLs must fail
    invalid_urls = [
        "http://github.com/owner/repo", # HTTP scheme
        "https://127.0.0.1/owner/repo", # Localhost IP
        "https://169.254.169.254/latest/meta-data", # AWS Metadata SSRF
        "https://evil.com/owner/repo", # Non-github domain
        "file:///etc/passwd", # File URI
        "https://github.com/../../etc/passwd", # Traversal
        "javascript:alert(1)" # Script scheme
    ]

    for bad_url in invalid_urls:
        with pytest.raises(SecurityValidationError):
            RepositoryLoader.validate_github_url(bad_url)


def test_zip_slip_protection(tmp_path):
    # Construct a malicious zip archive attempting to write outside the extraction folder
    bad_zip_path = tmp_path / "malicious.zip"
    with zipfile.ZipFile(bad_zip_path, "w") as zf:
        # File with path traversal "../evil.txt"
        zf.writestr("../../evil.txt", "pwned")

    with pytest.raises(SecurityValidationError) as exc_info:
        RepositoryLoader.extract_zip(bad_zip_path)
    assert "traversal" in str(exc_info.value).lower()
