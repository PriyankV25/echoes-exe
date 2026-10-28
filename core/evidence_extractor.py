"""
Echoes.exe — Evidence Extractor
Inspects source files, manifests, docs, and git logs to extract 100% evidence-backed technical history.
Never fabricates or extrapolates missing data.
"""
import os
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


class EvidenceExtractor:
    IGNORE_DIRS = {
        ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
        "dist", "build", "target", ".idea", ".vscode", "coverage", ".next"
    }

    LANG_EXT_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "React (JSX)",
        ".tsx": "React (TSX)",
        ".rs": "Rust",
        ".go": "Go",
        ".java": "Java",
        ".c": "C",
        ".cpp": "C++",
        ".h": "C/C++ Header",
        ".cs": "C#",
        ".rb": "Ruby",
        ".php": "PHP",
        ".sh": "Shell",
        ".html": "HTML",
        ".css": "CSS",
        ".scss": "SCSS",
        ".sql": "SQL",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".md": "Markdown",
        ".toml": "TOML"
    }

    def __init__(self, repo_dir: Path, source_meta: Optional[Dict[str, Any]] = None):
        self.repo_dir = Path(repo_dir)
        self.source_meta = source_meta or {}

    def extract_all(self) -> Dict[str, Any]:
        """Extracts complete evidence portfolio from the repository."""
        git_evidence = self._extract_git_history()
        file_tree, lang_stats, total_loc, test_indicators = self._analyze_file_structure()
        manifests = self._extract_manifests()
        docs = self._extract_documentation()
        evidence_chunks = self._generate_evidence_chunks(git_evidence, manifests, docs, file_tree)

        repo_name = self.source_meta.get("repo_name") or self.repo_dir.name
        primary_lang = max(lang_stats.items(), key=lambda x: x[1])[0] if lang_stats else "Unknown"

        return {
            "project_name": repo_name,
            "source_type": self.source_meta.get("source_type", "local"),
            "url": self.source_meta.get("url"),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "primary_language": primary_lang,
            "git_evidence": git_evidence,
            "language_breakdown": lang_stats,
            "total_files": len(file_tree),
            "total_loc": total_loc,
            "test_indicators": test_indicators,
            "manifests": manifests,
            "documentation": docs,
            "evidence_chunks": evidence_chunks,
            "file_sample": file_tree[:60]
        }

    def _extract_git_history(self) -> Dict[str, Any]:
        """Extracts verifiable commit history using Git CLI."""
        git_dir = self.repo_dir / ".git"
        if not git_dir.exists():
            return {
                "available": False,
                "reason": "No .git directory found in archive.",
                "total_commits": 0,
                "first_commit": None,
                "latest_commit": None,
                "lifespan_days": None,
                "days_since_last_commit": None,
                "commit_activity": {},
                "top_contributors": [],
                "recent_commits": []
            }

        try:
            # 1. Total commits
            total_commits_res = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            total_commits = int(total_commits_res.stdout.strip()) if total_commits_res.returncode == 0 and total_commits_res.stdout.strip().isdigit() else 0

            # 2. Latest commit
            latest_res = subprocess.run(
                ["git", "log", "-1", "--format=%H%x1f%an%x1f%aI%x1f%s"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            latest_commit = None
            if latest_res.returncode == 0 and latest_res.stdout.strip():
                parts = latest_res.stdout.strip().split("\x1f")
                if len(parts) >= 4:
                    latest_commit = {
                        "hash": parts[0],
                        "short_hash": parts[0][:7],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    }

            # 3. First commit (root)
            first_res = subprocess.run(
                ["git", "log", "--reverse", "--format=%H%x1f%an%x1f%aI%x1f%s"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            first_commit = None
            if first_res.returncode == 0 and first_res.stdout.strip():
                first_line = first_res.stdout.strip().splitlines()[0]
                parts = first_line.split("\x1f")
                if len(parts) >= 4:
                    first_commit = {
                        "hash": parts[0],
                        "short_hash": parts[0][:7],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    }

            # 4. Recent commits (up to 30)
            recent_res = subprocess.run(
                ["git", "log", "-30", "--format=%H%x1f%an%x1f%aI%x1f%s"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            recent_commits = []
            if recent_res.returncode == 0 and recent_res.stdout.strip():
                for line in recent_res.stdout.strip().splitlines():
                    parts = line.split("\x1f")
                    if len(parts) >= 4:
                        recent_commits.append({
                            "hash": parts[0],
                            "short_hash": parts[0][:7],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })

            # 5. Top contributors
            contrib_res = subprocess.run(
                ["git", "shortlog", "-sn", "--no-merges", "HEAD"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            top_contributors = []
            if contrib_res.returncode == 0 and contrib_res.stdout.strip():
                for line in contrib_res.stdout.strip().splitlines()[:10]:
                    match = re.match(r"^\s*(\d+)\s+(.+)$", line)
                    if match:
                        top_contributors.append({
                            "author": match.group(2).strip(),
                            "commits": int(match.group(1))
                        })

            # 6. Commit activity by month/year (timeline)
            activity_res = subprocess.run(
                ["git", "log", "--format=%aI"],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            commit_activity = {}
            if activity_res.returncode == 0 and activity_res.stdout.strip():
                for date_str in activity_res.stdout.strip().splitlines():
                    if len(date_str) >= 7:
                        month_key = date_str[:7]  # YYYY-MM
                        commit_activity[month_key] = commit_activity.get(month_key, 0) + 1

            # 7. Calculate time spans
            lifespan_days = None
            days_since_last_commit = None
            if first_commit and latest_commit:
                try:
                    d_first = datetime.fromisoformat(first_commit["date"].replace("Z", "+00:00"))
                    d_last = datetime.fromisoformat(latest_commit["date"].replace("Z", "+00:00"))
                    lifespan_days = max(0, (d_last - d_first).days)
                    now = datetime.now(d_last.tzinfo)
                    days_since_last_commit = max(0, (now - d_last).days)
                except Exception:
                    pass

            return {
                "available": True,
                "total_commits": total_commits,
                "first_commit": first_commit,
                "latest_commit": latest_commit,
                "lifespan_days": lifespan_days,
                "days_since_last_commit": days_since_last_commit,
                "commit_activity": dict(sorted(commit_activity.items())),
                "top_contributors": top_contributors,
                "recent_commits": recent_commits
            }

        except Exception as e:
            return {
                "available": False,
                "reason": f"Git command failed: {str(e)}",
                "total_commits": 0,
                "first_commit": None,
                "latest_commit": None,
                "lifespan_days": None,
                "days_since_last_commit": None,
                "commit_activity": {},
                "top_contributors": [],
                "recent_commits": []
            }

    def _analyze_file_structure(self) -> Tuple[List[str], Dict[str, int], int, Dict[str, Any]]:
        """Walks repository to detect languages, lines of code, and test infrastructure."""
        file_tree = []
        lang_counts: Dict[str, int] = {}
        total_loc = 0
        test_files = []
        ci_configs = []

        for root, dirs, files in os.walk(self.repo_dir):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for file in files:
                full_path = Path(root) / file
                rel_path = str(full_path.relative_to(self.repo_dir)).replace("\\", "/")
                file_tree.append(rel_path)

                # Check extension
                ext = full_path.suffix.lower()
                lang = self.LANG_EXT_MAP.get(ext)
                if lang:
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

                # Check test indicators
                lower_path = rel_path.lower()
                if any(k in lower_path for k in ["test_", "_test.", ".test.", ".spec.", "tests/", "__tests__/"]):
                    test_files.append(rel_path)

                # Check CI / Automation
                if ".github/workflows" in lower_path or lower_path in [".travis.yml", "circle.yml", "jenkinsfile", ".gitlab-ci.yml"]:
                    ci_configs.append(rel_path)

                # Quick LOC count on text files under 500KB
                if ext in self.LANG_EXT_MAP and full_path.stat().st_size < 500_000:
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            total_loc += sum(1 for _ in f)
                    except Exception:
                        pass

        test_indicators = {
            "has_tests": len(test_files) > 0,
            "test_file_count": len(test_files),
            "test_files": test_files[:20],
            "has_ci": len(ci_configs) > 0,
            "ci_configs": ci_configs
        }

        return file_tree, lang_counts, total_loc, test_indicators

    def _extract_manifests(self) -> Dict[str, Any]:
        """Parses dependency manifests across Python, Node, Rust, Go, Java, etc."""
        manifests = {}

        # 1. Node.js: package.json
        pkg_path = self.repo_dir / "package.json"
        if pkg_path.exists():
            try:
                data = json.loads(pkg_path.read_text(encoding="utf-8", errors="ignore"))
                manifests["package_json"] = {
                    "path": "package.json",
                    "name": data.get("name"),
                    "version": data.get("version"),
                    "description": data.get("description"),
                    "main": data.get("main"),
                    "scripts": list(data.get("scripts", {}).keys()),
                    "dependencies": data.get("dependencies", {}),
                    "devDependencies": data.get("devDependencies", {}),
                    "engines": data.get("engines", {})
                }
            except Exception as e:
                manifests["package_json"] = {"path": "package.json", "error": f"Failed to parse: {str(e)}"}

        # 2. Python: requirements.txt
        req_path = self.repo_dir / "requirements.txt"
        if req_path.exists():
            try:
                lines = req_path.read_text(encoding="utf-8", errors="ignore").splitlines()
                deps = {}
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = re.split(r"(==|>=|<=|~=|>|<)", line, maxsplit=1)
                        name = parts[0].strip()
                        ver = "".join(parts[1:]).strip() if len(parts) > 1 else "unpinned"
                        deps[name] = ver
                manifests["requirements_txt"] = {
                    "path": "requirements.txt",
                    "dependencies": deps,
                    "count": len(deps)
                }
            except Exception as e:
                manifests["requirements_txt"] = {"path": "requirements.txt", "error": f"Failed to parse: {str(e)}"}

        # 3. Python: pyproject.toml
        pyproj_path = self.repo_dir / "pyproject.toml"
        if pyproj_path.exists():
            manifests["pyproject_toml"] = {
                "path": "pyproject.toml",
                "content_preview": pyproj_path.read_text(encoding="utf-8", errors="ignore")[:2000]
            }

        # 4. Rust: Cargo.toml
        cargo_path = self.repo_dir / "Cargo.toml"
        if cargo_path.exists():
            manifests["cargo_toml"] = {
                "path": "Cargo.toml",
                "content_preview": cargo_path.read_text(encoding="utf-8", errors="ignore")[:2000]
            }

        # 5. Go: go.mod
        go_path = self.repo_dir / "go.mod"
        if go_path.exists():
            manifests["go_mod"] = {
                "path": "go.mod",
                "content_preview": go_path.read_text(encoding="utf-8", errors="ignore")[:2000]
            }

        return manifests

    def _extract_documentation(self) -> Dict[str, Any]:
        """Detects and extracts project documentation, license, and architectural guides."""
        docs = {
            "readme": None,
            "license": None,
            "contributing": None,
            "changelog": None
        }

        # Find README
        for cand in ["README.md", "README.rst", "README.txt", "README", "readme.md"]:
            p = self.repo_dir / cand
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="ignore")
                headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")]
                docs["readme"] = {
                    "path": cand,
                    "length": len(text),
                    "headings": headings[:15],
                    "excerpt": text[:4000]
                }
                break

        # Find LICENSE
        for cand in ["LICENSE", "LICENSE.md", "LICENSE.txt", "license"]:
            p = self.repo_dir / cand
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="ignore")
                first_lines = "\n".join(text.splitlines()[:5])
                docs["license"] = {
                    "path": cand,
                    "excerpt": first_lines
                }
                break

        # Find CONTRIBUTING
        for cand in ["CONTRIBUTING.md", "CONTRIBUTING"]:
            p = self.repo_dir / cand
            if p.exists():
                docs["contributing"] = {"path": cand, "present": True}
                break

        # Find CHANGELOG
        for cand in ["CHANGELOG.md", "HISTORY.md", "RELEASES.md"]:
            p = self.repo_dir / cand
            if p.exists():
                text = p.read_text(encoding="utf-8", errors="ignore")
                docs["changelog"] = {
                    "path": cand,
                    "excerpt": text[:2000]
                }
                break

        return docs

    def _generate_evidence_chunks(
        self,
        git_evidence: Dict[str, Any],
        manifests: Dict[str, Any],
        docs: Dict[str, Any],
        file_tree: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Creates fine-grained, verifiable evidence chunks with exact source citations.
        Used for Vector Search and Grounded Retrieval during Ghost Interviews.
        """
        chunks = []
        chunk_idx = 1

        # 1. Documentation chunks (README)
        if docs.get("readme") and docs["readme"].get("excerpt"):
            content = docs["readme"]["excerpt"]
            # Split into 500-char blocks with 100-char overlap
            step = 600
            for i in range(0, len(content), step):
                sub = content[i:i + step + 100].strip()
                if sub:
                    chunks.append({
                        "chunk_id": f"chk_{chunk_idx:03d}",
                        "source_type": "readme",
                        "source_path": docs["readme"]["path"],
                        "citation": f"{docs['readme']['path']} (offset {i}-{i+len(sub)})",
                        "category": "FACT",
                        "content": sub
                    })
                    chunk_idx += 1

        # 2. Dependency Manifest chunks
        if "package_json" in manifests and "dependencies" in manifests["package_json"]:
            pkg = manifests["package_json"]
            deps_summary = f"Node.js Package: {pkg.get('name')} v{pkg.get('version')}\nDependencies: {json.dumps(pkg.get('dependencies', {}), indent=2)}\nDevDependencies: {json.dumps(pkg.get('devDependencies', {}), indent=2)}"
            chunks.append({
                "chunk_id": f"chk_{chunk_idx:03d}",
                "source_type": "manifest",
                "source_path": "package.json",
                "citation": "package.json:dependencies",
                "category": "FACT",
                "content": deps_summary
            })
            chunk_idx += 1

        if "requirements_txt" in manifests and "dependencies" in manifests["requirements_txt"]:
            req = manifests["requirements_txt"]
            deps_summary = f"Python requirements.txt ({req.get('count', 0)} dependencies):\n" + "\n".join(
                f"- {k}: {v}" for k, v in req.get("dependencies", {}).items()
            )
            chunks.append({
                "chunk_id": f"chk_{chunk_idx:03d}",
                "source_type": "manifest",
                "source_path": "requirements.txt",
                "citation": "requirements.txt:dependencies",
                "category": "FACT",
                "content": deps_summary
            })
            chunk_idx += 1

        # 3. Git commit history chunks
        if git_evidence.get("available"):
            if git_evidence.get("first_commit"):
                fc = git_evidence["first_commit"]
                chunks.append({
                    "chunk_id": f"chk_{chunk_idx:03d}",
                    "source_type": "commit",
                    "source_path": f"commit:{fc['hash']}",
                    "citation": f"Initial Commit {fc['short_hash']} ({fc['date']}) by {fc['author']}",
                    "category": "FACT",
                    "content": f"Repository Genesis: First recorded commit {fc['short_hash']} on {fc['date']} by {fc['author']}. Message: '{fc['message']}'"
                })
                chunk_idx += 1

            if git_evidence.get("latest_commit"):
                lc = git_evidence["latest_commit"]
                chunks.append({
                    "chunk_id": f"chk_{chunk_idx:03d}",
                    "source_type": "commit",
                    "source_path": f"commit:{lc['hash']}",
                    "citation": f"Final Recorded Commit {lc['short_hash']} ({lc['date']}) by {lc['author']}",
                    "category": "FACT",
                    "content": f"Repository Last Known Activity: Final recorded commit {lc['short_hash']} on {lc['date']} by {lc['author']}. Message: '{lc['message']}'. Lifespan: {git_evidence.get('lifespan_days')} days. Dormant for: {git_evidence.get('days_since_last_commit')} days."
                })
                chunk_idx += 1

            # Recent commits batch
            if git_evidence.get("recent_commits"):
                summary_lines = []
                for c in git_evidence["recent_commits"][:15]:
                    summary_lines.append(f"- {c['short_hash']} ({c['date'][:10]}): {c['message']} [Author: {c['author']}]")
                chunks.append({
                    "chunk_id": f"chk_{chunk_idx:03d}",
                    "source_type": "commit_log",
                    "source_path": "git:recent_log",
                    "citation": "git log --recent-15",
                    "category": "FACT",
                    "content": "Recent Commit Log Sequence:\n" + "\n".join(summary_lines)
                })
                chunk_idx += 1

        # 4. Architecture / File structure chunk
        chunks.append({
            "chunk_id": f"chk_{chunk_idx:03d}",
            "source_type": "file_tree",
            "source_path": "tree:root",
            "citation": "repository file structure",
            "category": "FACT",
            "content": f"Repository File Composition: Total files: {len(file_tree)}. Structure overview: {', '.join(file_tree[:35])}"
        })

        return chunks
