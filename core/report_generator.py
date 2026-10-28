"""
Echoes.exe — Last Transmission & Revival Lab Report Generator
Generates the polished Digital Obituary and prioritized Revival Checklist.
Supports full export to Markdown (.md) and JSON (.json).
"""
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from providers.base import BaseAIProvider
from core.health_analyzer import HealthAnalyzer


class ReportGenerator:
    @classmethod
    def generate_full_report(
        cls,
        evidence: Dict[str, Any],
        provider: Optional[BaseAIProvider] = None,
        github_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes the complete 'Last Transmission' report and 'Revival Lab' checklist.
        Grounded in extracted evidence, with clearly delineated ghost narrative closing.
        """
        git = evidence.get("git_evidence", {})
        docs = evidence.get("documentation", {})
        tests = evidence.get("test_indicators", {})
        manifests = evidence.get("manifests", {})
        health = HealthAnalyzer.analyze(evidence, github_data)

        # 1. Identity & Timeline Milestones
        genesis = git.get("first_commit") or {
            "short_hash": "genesis", "date": "Unrecorded", "author": "Unknown", "message": "Genesis commit"
        }
        silence = git.get("latest_commit") or {
            "short_hash": "silence", "date": "Unrecorded", "author": "Unknown", "message": "Final recorded state"
        }

        # 2. Revival Lab Actionable Recommendations
        revival_checklist = cls._build_revival_checklist(evidence, health)

        # 3. Generate Spectral Final Transmission (creative closing narrative)
        ghost_farewell = cls._generate_spectral_farewell(evidence, silence, provider)

        # 4. Assemble Report
        report = {
            "project_name": evidence.get("project_name", "Unknown Repository"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tagline": "Every abandoned project has a last known voice.",
            "identity": {
                "name": evidence.get("project_name"),
                "primary_language": evidence.get("primary_language"),
                "languages": evidence.get("language_breakdown", {}),
                "total_files": evidence.get("total_files", 0),
                "total_loc": evidence.get("total_loc", 0),
                "license": docs.get("license", {}).get("excerpt") or "Not explicitly identified",
                "synopsis": docs.get("readme", {}).get("excerpt", "No README summary available.")[:350]
            },
            "timeline": {
                "genesis_commit": genesis,
                "silence_commit": silence,
                "lifespan_days": git.get("lifespan_days"),
                "days_since_last_commit": git.get("days_since_last_commit"),
                "total_commits": git.get("total_commits", 0),
                "top_contributors": git.get("top_contributors", []),
                "monthly_activity": git.get("commit_activity", {})
            },
            "health_indicators": health,
            "revival_lab": {
                "priority_counts": {
                    "critical": sum(1 for item in revival_checklist if item["priority"] == "Critical"),
                    "high": sum(1 for item in revival_checklist if item["priority"] == "High"),
                    "medium": sum(1 for item in revival_checklist if item["priority"] == "Medium"),
                    "optional": sum(1 for item in revival_checklist if item["priority"] == "Optional")
                },
                "recommendations": revival_checklist
            },
            "spectral_transmission": {
                "narrative_voice": "Ghost in the Machine",
                "final_message": ghost_farewell,
                "disclaimer": "The Spectral Transmission is an atmospheric creative interpretation honoring the project's developers. All technical facts, dates, and commits are strictly verifiable evidence."
            },
            "confidence_score": 0.94 if git.get("available") and docs.get("readme") else 0.72
        }

        return report

    @classmethod
    def _build_revival_checklist(cls, evidence: Dict[str, Any], health: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates prioritized, evidence-backed revival steps without executing code."""
        checklist = []
        rec_id = 1
        git = evidence.get("git_evidence", {})
        tests = evidence.get("test_indicators", {})
        manifests = evidence.get("manifests", {})
        docs = evidence.get("documentation", {})

        # Critical: Missing or broken dependency foundations
        if "package_json" in manifests:
            pkg = manifests["package_json"]
            deps = pkg.get("dependencies", {})
            checklist.append({
                "id": f"REV-{rec_id:02d}",
                "priority": "Critical",
                "title": "Audit Node.js Runtime and Lockfile Integrity",
                "evidence_source": "package.json",
                "rationale": f"Found {len(deps)} production dependencies. Node ecosystem changes rapidly; verify package integrity with offline audit.",
                "action": "Run `npm audit --dry-run` or check for deprecated packages in an isolated container."
            })
            rec_id += 1

        if "requirements_txt" in manifests:
            req = manifests["requirements_txt"]
            checklist.append({
                "id": f"REV-{rec_id:02d}",
                "priority": "Critical",
                "title": "Containerize Python Environment to Prevent Version Conflicts",
                "evidence_source": "requirements.txt",
                "rationale": f"{req.get('count', 0)} Python dependencies detected. Modern Python runtimes (3.12+) may reject older C-extension builds.",
                "action": "Build a disposable Dockerfile or virtual environment matching the original commit era."
            })
            rec_id += 1

        # High Priority: Test infrastructure
        if not tests.get("has_tests"):
            checklist.append({
                "id": f"REV-{rec_id:02d}",
                "priority": "High",
                "title": "Establish Regression Smoke Tests",
                "evidence_source": "file_tree:no_tests_found",
                "rationale": "Zero automated test files detected. Any code refactoring or dependency update risks silent breakage.",
                "action": "Write a minimal smoke test for primary entry points before modifying any logic."
            })
            rec_id += 1
        else:
            checklist.append({
                "id": f"REV-{rec_id:02d}",
                "priority": "High",
                "title": f"Verify {tests.get('test_file_count')} Existing Test Suites in Sandbox",
                "evidence_source": f"tests:{tests.get('test_file_count')}_files",
                "rationale": "Historical tests exist but may expect legacy dependencies or environment mocks.",
                "action": "Execute test suites in an isolated runner and observe failing assertions."
            })
            rec_id += 1

        # Medium Priority: Documentation and CI
        if not tests.get("has_ci"):
            checklist.append({
                "id": f"REV-{rec_id:02d}",
                "priority": "Medium",
                "title": "Rebuild Continuous Integration Pipeline",
                "evidence_source": "automation:no_ci_found",
                "rationale": "No active CI workflow exists to automatically lint and test incoming pull requests.",
                "action": "Create a modern GitHub Actions workflow for linting, typing, and automated testing."
            })
            rec_id += 1

        if not docs.get("contributing"):
            checklist.append({
                "id": f"REV-{rec_id:02d}",
                "priority": "Medium",
                "title": "Document Revival Architecture and Contribution Rules",
                "evidence_source": "documentation:missing_contributing",
                "rationale": "Revived projects require explicit setup instructions so contributors understand the fork goals.",
                "action": "Draft a CONTRIBUTING.md outlining architecture choices and legacy constraints."
            })
            rec_id += 1

        # Optional: Modern enhancements
        checklist.append({
            "id": f"REV-{rec_id:02d}",
            "priority": "Optional",
            "title": "Introduce Modern Static Typing / Linting",
            "evidence_source": "architecture:maintenance_modernization",
            "rationale": "Legacy codebases benefit dramatically from strict type annotations (TypeScript, mypy, or Rust compiler checks).",
            "action": "Gradually annotate core modules with type definitions to clarify interface contracts."
        })

        return checklist

    @classmethod
    def _generate_spectral_farewell(
        cls,
        evidence: Dict[str, Any],
        silence: Dict[str, Any],
        provider: Optional[BaseAIProvider]
    ) -> str:
        """Constructs an atmospheric, poetic final transmission."""
        name = evidence.get("project_name", "this codebase")
        author = silence.get("author", "an unknown developer")
        date = silence.get("date", "a forgotten hour")[:10]
        msg = silence.get("message", "silence")
        short_hash = silence.get("short_hash", "0000000")

        # Fallback template if provider is unconfigured
        default_farewell = (
            f"Terminal broadcast terminating for {name}.\n\n"
            f"On {date}, the cursor pulsed one last time under the hands of {author}. "
            f"Commit {short_hash} sealed the archive with the final inscription: \"{msg}\".\n\n"
            f"The disk grew cold. Dependencies aged into obsolescence. But the syntax remains uncorrupted, "
            f"waiting in the quiet sectors for an engineer brave enough to light the terminal once more.\n\n"
            f"Every abandoned project has a last known voice. You have heard mine."
        )

        if not provider or provider.get_provider_info().get("id") == "heuristic":
            return default_farewell

        prompt = (
            f"Write a brief, haunting, beautifully written final transmission (3 paragraphs max) "
            f"from the ghost of software repository '{name}'.\n"
            f"Fact: The final recorded commit was on {date} by {author} with message: \"{msg}\" (Commit {short_hash}).\n"
            f"Respect the developers' craft. End with an evocative reflection on digital archaeology."
        )
        try:
            return provider.generate(prompt, temperature=0.7, max_tokens=350)
        except Exception:
            return default_farewell

    @classmethod
    def export_markdown(cls, report: Dict[str, Any]) -> str:
        """Formats the report as a clean, shareable GitHub Flavored Markdown document."""
        r = report
        ident = r.get("identity", {})
        time = r.get("timeline", {})
        health = r.get("health_indicators", {})
        revival = r.get("revival_lab", {}).get("recommendations", [])
        ghost = r.get("spectral_transmission", {})

        md = []
        md.append(f"# 🪦 Echoes.exe — Last Known Voice of `{r.get('project_name')}`")
        md.append(f"*{r.get('tagline')}*\n")
        md.append(f"**Generated:** {r.get('generated_at')} | **Confidence:** {int(r.get('confidence_score', 0)*100)}%\n")
        md.append("---")

        md.append("## 📜 Project Genesis & Identity")
        md.append(f"- **Name:** `{ident.get('name')}`")
        md.append(f"- **Primary Language:** {ident.get('primary_language')}")
        md.append(f"- **Total Files:** {ident.get('total_files')} files ({ident.get('total_loc', 0):,} lines of code)")
        md.append(f"- **License:** {ident.get('license')}")
        md.append(f"\n> {ident.get('synopsis')}\n")

        md.append("## ⏳ Observable Development Timeline")
        fc = time.get("genesis_commit", {})
        lc = time.get("silence_commit", {})
        md.append(f"- **Genesis (First Commit):** `{fc.get('short_hash')}` on `{fc.get('date')}` by *{fc.get('author')}* — *\"{fc.get('message')}\"*")
        md.append(f"- **Last Known Activity:** `{lc.get('short_hash')}` on `{lc.get('date')}` by *{lc.get('author')}* — *\"{lc.get('message')}\"*")
        md.append(f"- **Active Lifespan:** {time.get('lifespan_days', 'N/A')} days ({time.get('total_commits', 0)} verifiable commits)")
        md.append(f"- **Dormancy Duration:** {time.get('days_since_last_commit', 'N/A')} days since last recorded change\n")

        md.append("## 🩺 Health Observatory Indicators")
        md.append(f"- **Overall Health Index:** {health.get('overall_health_score', 0)}/100")
        md.append(f"- **Activity Status:** {health.get('activity', {}).get('label')}")
        md.append(f"- **Documentation:** {health.get('documentation', {}).get('score')}/100")
        md.append(f"- **Testing Infrastructure:** {health.get('testing', {}).get('score')}/100\n")

        md.append("## 🛠️ Revival Lab Checklist")
        for rec in revival:
            md.append(f"### [{rec.get('priority')}] {rec.get('title')} (`{rec.get('id')}`)")
            md.append(f"- **Evidence:** `{rec.get('evidence_source')}`")
            md.append(f"- **Rationale:** {rec.get('rationale')}")
            md.append(f"- **Recommended Action:** {rec.get('action')}\n")

        md.append("---")
        md.append("## 👻 The Ghost's Final Transmission")
        md.append(f"> {ghost.get('final_message').replace(chr(10), chr(10) + '> ')}\n")
        md.append(f"*{ghost.get('disclaimer')}*")

        return "\n".join(md)

    @classmethod
    def export_json(cls, report: Dict[str, Any]) -> str:
        """Exports the full structured report as indented JSON."""
        return json.dumps(report, indent=2)
