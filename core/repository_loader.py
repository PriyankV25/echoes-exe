"""
Echoes.exe — Safe Repository Ingestion Loader
Handles GitHub URLs, ZIP uploads, local directories, and built-in sample repos.
Enforces strict security against path traversal, zip bombs, and SSRF.
"""
import os
import re
import shutil
import zipfile
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
from urllib.parse import urlparse

from config.settings import settings


class SecurityValidationError(Exception):
    """Raised when repository input violates security constraints."""
    pass


class RepositoryLoader:
    GITHUB_URL_PATTERN = re.compile(
        r"^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$"
    )

    @classmethod
    def validate_github_url(cls, url: str) -> Tuple[str, str]:
        """
        Validates public GitHub repository URL and extracts (owner, repo).
        Protects against SSRF, internal network probing, and malicious schemes.
        """
        if not url or not isinstance(url, str):
            raise SecurityValidationError("Invalid URL provided.")

        url = url.strip()
        parsed = urlparse(url)

        if parsed.scheme != "https":
            raise SecurityValidationError("Only secure HTTPS GitHub URLs are accepted.")

        if parsed.netloc.lower() not in ("github.com", "www.github.com"):
            raise SecurityValidationError("URL domain must be github.com.")

        match = cls.GITHUB_URL_PATTERN.match(url)
        if not match:
            raise SecurityValidationError(
                "Invalid GitHub repository URL format. Expected: https://github.com/owner/repository"
            )

        owner, repo = match.groups()
        if repo.endswith(".git"):
            repo = repo[:-4]

        # Sanitize characters
        if ".." in owner or ".." in repo or "/" in owner or "/" in repo:
            raise SecurityValidationError("Repository path contains forbidden characters.")

        return owner, repo

    @classmethod
    def clone_github_repo(cls, url: str) -> Tuple[Path, Dict[str, Any]]:
        """
        Safely clones a public GitHub repository into a temporary directory
        with depth limit and execution timeout.
        """
        owner, repo = cls.validate_github_url(url)
        clean_url = f"https://github.com/{owner}/{repo}.git"

        temp_dir = Path(tempfile.mkdtemp(prefix=f"echoes_clone_{owner}_{repo}_", dir=settings.TEMP_DIR))

        try:
            cmd = [
                "git", "clone",
                "--depth", str(settings.GIT_CLONE_DEPTH),
                "--single-branch",
                clean_url,
                str(temp_dir)
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.GIT_TIMEOUT_SECONDS,
                check=False
            )

            if result.returncode != 0:
                shutil.rmtree(temp_dir, ignore_errors=True)
                error_msg = result.stderr.strip() or "Failed to clone repository."
                # Don't leak raw internal paths in error
                raise RuntimeError(f"Git clone error: {error_msg}")

            meta = {
                "source_type": "github_clone",
                "owner": owner,
                "repo_name": repo,
                "url": f"https://github.com/{owner}/{repo}",
                "local_path": str(temp_dir)
            }
            return temp_dir, meta

        except subprocess.TimeoutExpired:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise TimeoutError("Git clone timed out. The repository may be too large or unreachable.")
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    @classmethod
    def extract_zip(cls, zip_file_path: Path) -> Tuple[Path, Dict[str, Any]]:
        """
        Safely unpacks a ZIP archive protecting against:
        - Zip Slip (path traversal ../../)
        - Zip Bombs (excessive uncompressed size or file count)
        """
        if not zip_file_path.exists():
            raise FileNotFoundError(f"Archive file not found: {zip_file_path}")

        temp_dir = Path(tempfile.mkdtemp(prefix="echoes_zip_", dir=settings.TEMP_DIR))
        max_uncompressed_bytes = settings.MAX_CONTENT_LENGTH * 3
        max_file_count = 5000

        total_bytes = 0
        total_files = 0

        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zf:
                # Check for zip bomb characteristics before extraction
                for info in zf.infolist():
                    total_files += 1
                    total_bytes += info.file_size
                    if total_files > max_file_count:
                        raise SecurityValidationError("ZIP archive exceeds safe file count limit (5,000 files).")
                    if total_bytes > max_uncompressed_bytes:
                        raise SecurityValidationError("ZIP archive exceeds safe uncompressed size limit.")

                # Extract safely with path traversal check
                for member in zf.infolist():
                    extracted_path = (temp_dir / member.filename).resolve()
                    # Path traversal check
                    if not str(extracted_path).startswith(str(temp_dir.resolve())):
                        raise SecurityValidationError(f"Attempted path traversal detected in ZIP: {member.filename}")

                    zf.extract(member, temp_dir)

            # If the zip had a single top-level directory, set target_dir to that directory
            sub_dirs = [p for p in temp_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
            actual_root = temp_dir
            if len(sub_dirs) == 1 and not any(p.is_file() for p in temp_dir.iterdir()):
                actual_root = sub_dirs[0]

            meta = {
                "source_type": "zip_upload",
                "repo_name": zip_file_path.stem,
                "local_path": str(actual_root),
                "total_files": total_files
            }
            return actual_root, meta

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    @classmethod
    def load_local_repo(cls, path_str: str) -> Tuple[Path, Dict[str, Any]]:
        """
        Loads a local repository path, ensuring it is a valid directory
        and not a sensitive system directory.
        """
        path = Path(path_str).resolve()
        if not path.exists() or not path.is_dir():
            raise FileNotFoundError(f"Local repository directory does not exist: {path_str}")

        # Block root system directories
        prohibited = [Path("C:/Windows"), Path("C:/"), Path("/"), Path("/etc"), Path("/var"), Path("/sys")]
        for p in prohibited:
            if path == p:
                raise SecurityValidationError("Cannot analyze root or critical system directories.")

        meta = {
            "source_type": "local_directory",
            "repo_name": path.name,
            "local_path": str(path)
        }
        return path, meta

    @classmethod
    def load_sample_repo(cls, sample_id: str) -> Tuple[Path, Dict[str, Any]]:
        """
        Loads one of the packaged safe sample repositories for instant offline demonstration.
        """
        sample_path = settings.SAMPLES_DIR / sample_id
        if not sample_path.exists() or not (sample_path / ".git").exists():
            from scripts.create_samples import ensure_samples
            ensure_samples()

        if not sample_path.exists() or not sample_path.is_dir():
            raise FileNotFoundError(f"Sample archive '{sample_id}' not found.")

        meta = {
            "source_type": "sample_archive",
            "repo_name": sample_id,
            "local_path": str(sample_path)
        }
        return sample_path, meta

    @classmethod
    def cleanup(cls, path: Path):
        """Safely removes temporary extraction directories."""
        if path and path.exists():
            resolved = path.resolve()
            # Only delete if inside our designated temp directory
            if str(resolved).startswith(str(settings.TEMP_DIR.resolve())):
                shutil.rmtree(resolved, ignore_errors=True)
