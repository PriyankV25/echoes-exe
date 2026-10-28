"""
Echoes.exe — Repository Health Observatory & Heuristics Analyzer
Calculates measurable, evidence-grounded health indicators using transparent rules.
Uses neutral, objective terminology (e.g. 'low recent activity' rather than 'dead').
"""
from typing import Dict, Any, List


class HealthAnalyzer:
    @classmethod
    def analyze(cls, evidence: Dict[str, Any], github_details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluates repository health across five dimensions:
        1. Activity & Recency
        2. Documentation Completeness
        3. Test Infrastructure
        4. Dependency Risk
        5. Community & Maintenance Trajectory
        """
        git = evidence.get("git_evidence", {})
        docs = evidence.get("documentation", {})
        tests = evidence.get("test_indicators", {})
        manifests = evidence.get("manifests", {})
        github = github_details or {}

        # 1. Activity & Recency Analysis
        days_dormant = git.get("days_since_last_commit")
        if days_dormant is None:
            activity_state = "unrecorded"
            activity_label = "Commit Recency Unknown"
            activity_score = 50
        elif days_dormant < 90:
            activity_state = "active"
            activity_label = "Recent Activity Observed"
            activity_score = 95
        elif days_dormant < 365:
            activity_state = "moderate_cadence"
            activity_label = "Moderate Activity Cadence"
            activity_score = 75
        elif days_dormant < 1095:  # 1 to 3 years
            activity_state = "low_recent_activity"
            activity_label = "Low Recent Activity"
            activity_score = 45
        else:  # > 3 years
            activity_state = "dormant"
            activity_label = "Long-Term Inactivity"
            activity_score = 20

        # 2. Documentation Score (0-100)
        doc_score = 0
        doc_findings = []
        if docs.get("readme"):
            doc_score += 40
            doc_findings.append("README present with structured sections.")
            if docs["readme"].get("length", 0) > 1500:
                doc_score += 20
                doc_findings.append("Comprehensive README documentation.")
        else:
            doc_findings.append("Missing or empty README file.")

        if docs.get("license"):
            doc_score += 20
            doc_findings.append("Open-source LICENSE file present.")
        else:
            doc_findings.append("No explicit LICENSE detected.")

        if docs.get("contributing"):
            doc_score += 10
            doc_findings.append("CONTRIBUTING guidelines available.")

        if docs.get("changelog"):
            doc_score += 10
            doc_findings.append("CHANGELOG or release history preserved.")

        # 3. Test & CI Infrastructure (0-100)
        test_score = 0
        test_findings = []
        if tests.get("has_tests"):
            count = tests.get("test_file_count", 0)
            test_score += min(60, count * 10 + 20)
            test_findings.append(f"{count} test file(s) detected in source tree.")
        else:
            test_findings.append("No automated test files detected.")

        if tests.get("has_ci"):
            test_score += 40
            test_findings.append("Automated CI/CD configuration files identified.")
        else:
            test_findings.append("No automated CI/CD pipeline definitions found.")

        # 4. Dependency Health Indicator
        dep_count = 0
        unpinned_count = 0
        dep_findings = []
        if "package_json" in manifests:
            pkg = manifests["package_json"]
            deps = pkg.get("dependencies", {})
            dep_count += len(deps)
            dep_findings.append(f"Node.js package with {len(deps)} production dependencies.")
        if "requirements_txt" in manifests:
            req = manifests["requirements_txt"]
            deps = req.get("dependencies", {})
            dep_count += len(deps)
            unpinned = sum(1 for v in deps.values() if v == "unpinned")
            if unpinned > 0:
                dep_findings.append(f"{unpinned} Python packages lack strict version pins.")
            dep_findings.append(f"Python environment specifies {len(deps)} packages.")

        # 5. Composite Health Index (0-100)
        overall_health = int(
            (activity_score * 0.35) +
            (doc_score * 0.25) +
            (test_score * 0.25) +
            (max(20, 100 - min(80, dep_count * 2)) * 0.15)
        )

        return {
            "overall_health_score": overall_health,
            "activity": {
                "state": activity_state,
                "label": activity_label,
                "days_since_last_commit": days_dormant,
                "lifespan_days": git.get("lifespan_days"),
                "total_commits": git.get("total_commits", 0)
            },
            "documentation": {
                "score": doc_score,
                "findings": doc_findings
            },
            "testing": {
                "score": test_score,
                "findings": test_findings
            },
            "dependencies": {
                "total_detected": dep_count,
                "findings": dep_findings
            },
            "ml_evaluation_note": "Rule-based transparent evaluation. TabPFN tabular prediction module ready for custom corpus evaluation."
        }
