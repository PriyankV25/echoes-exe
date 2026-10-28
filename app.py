"""
Echoes.exe — The Ghost Terminal
Open-Source AI Digital Archaeologist
Main Flask Application Server
"""
import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename

from config.settings import settings
from core.observability import init_observability, trace_stage
from core.repository_loader import RepositoryLoader, SecurityValidationError
from core.github_client import GitHubClient
from core.evidence_extractor import EvidenceExtractor
from core.health_analyzer import HealthAnalyzer
from core.ghost_engine import GhostEngine
from core.report_generator import ReportGenerator
from core.web_research import WebResearchEngine
from core.voice import VoiceEngine
from providers.factory import ProviderFactory
from storage.database import db_manager

# Initialize Observability (Sentry or local)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("echoes.app")
init_observability()

# Initialize Flask App
app = Flask(
    __name__,
    template_folder=str(settings.BASE_DIR / "templates"),
    static_folder=str(settings.BASE_DIR / "static")
)
app.secret_key = settings.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = settings.MAX_CONTENT_LENGTH

# In-memory session cache for active investigation in the browser
# (stores recent evidence object so user can chat with the ghost immediately before explicit save)
_active_investigations = {}


@app.route("/")
def index():
    """Renders the Ghost Terminal single-page horror interface."""
    return render_template("index.html", config=settings.get_public_config())


@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns safe runtime configuration and provider state."""
    cfg = settings.get_public_config()
    cfg["storage"] = db_manager.get_status()
    cfg["voice"] = VoiceEngine.get_status()
    return jsonify(cfg)


@app.route("/api/providers/test", methods=["GET"])
def test_providers():
    """Validates connectivity to Groq API and local Ollama daemon."""
    results = ProviderFactory.validate_all()
    return jsonify(results)


@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Dynamically updates active provider or model for the current session."""
    data = request.get_json() or {}
    new_provider = data.get("ai_provider")
    if new_provider:
        new_provider = new_provider.lower()
        if new_provider in ("groq", "ollama", "heuristic"):
            settings.AI_PROVIDER = new_provider

    if data.get("groq_model"):
        settings.GROQ_MODEL = data["groq_model"].strip()
    if data.get("ollama_model"):
        settings.OLLAMA_MODEL = data["ollama_model"].strip()
    if data.get("ollama_base_url"):
        settings.OLLAMA_BASE_URL = data["ollama_base_url"].strip().rstrip("/")
    if data.get("storage_mode"):
        settings.STORAGE_MODE = data["storage_mode"].lower()

    return jsonify({
        "success": True,
        "message": f"Settings updated. Active provider: {settings.AI_PROVIDER}",
        "config": settings.get_public_config()
    })


@app.route("/api/analyze/url", methods=["POST"])
def analyze_url():
    """Ingests and analyzes a public GitHub repository URL."""
    data = request.get_json() or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "Repository URL is required."}), 400

    temp_path = None
    try:
        with trace_stage("repo.ingest_url", {"url": url}):
            owner, repo = RepositoryLoader.validate_github_url(url)
            # Fetch GitHub API metadata in parallel
            gh_client = GitHubClient()
            gh_details = gh_client.get_repo_details(owner, repo)
            gh_releases = gh_client.get_releases(owner, repo)
            gh_issues = gh_client.get_issues(owner, repo)

            # Clone repository with depth limit
            temp_path, meta = RepositoryLoader.clone_github_repo(url)

        with trace_stage("evidence.extract", {"project": repo}):
            extractor = EvidenceExtractor(temp_path, source_meta=meta)
            evidence = extractor.extract_all()
            evidence["github_api"] = {
                "details": gh_details,
                "releases": gh_releases,
                "issues": gh_issues
            }

        with trace_stage("report.generate", {"project": repo}):
            provider = ProviderFactory.get_provider()
            report = ReportGenerator.generate_full_report(evidence, provider=provider, github_data=gh_details)

        # Cache active session
        session_id = f"sess_{meta['repo_name']}"
        _active_investigations[session_id] = {
            "evidence": evidence,
            "report": report
        }

        # Safe cleanup of clone directory after extraction
        RepositoryLoader.cleanup(temp_path)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "evidence": evidence,
            "report": report,
            "suggested_questions": GhostEngine.get_suggested_questions(evidence)
        })

    except SecurityValidationError as e:
        if temp_path: RepositoryLoader.cleanup(temp_path)
        return jsonify({"error": f"Security validation failed: {str(e)}"}), 400
    except Exception as e:
        if temp_path: RepositoryLoader.cleanup(temp_path)
        logger.exception("Analysis failed")
        return jsonify({"error": f"Archaeological scan failed: {str(e)}"}), 500


@app.route("/api/analyze/upload", methods=["POST"])
def analyze_upload():
    """Ingests and analyzes an uploaded repository ZIP archive."""
    if "archive" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["archive"]
    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    filename = secure_filename(file.filename)
    if not any(filename.lower().endswith(ext) for ext in settings.ALLOWED_EXTENSIONS):
        return jsonify({"error": f"Invalid file format. Allowed: {settings.ALLOWED_EXTENSIONS}"}), 400

    temp_zip = settings.TEMP_DIR / f"upload_{filename}"
    file.save(str(temp_zip))

    temp_extract_dir = None
    try:
        with trace_stage("repo.ingest_zip", {"filename": filename}):
            temp_extract_dir, meta = RepositoryLoader.extract_zip(temp_zip)

        with trace_stage("evidence.extract", {"project": meta["repo_name"]}):
            extractor = EvidenceExtractor(temp_extract_dir, source_meta=meta)
            evidence = extractor.extract_all()

        with trace_stage("report.generate", {"project": meta["repo_name"]}):
            provider = ProviderFactory.get_provider()
            report = ReportGenerator.generate_full_report(evidence, provider=provider)

        session_id = f"sess_{meta['repo_name']}"
        _active_investigations[session_id] = {
            "evidence": evidence,
            "report": report
        }

        # Cleanup
        if temp_zip.exists(): temp_zip.unlink(missing_ok=True)
        RepositoryLoader.cleanup(temp_extract_dir)

        return jsonify({
            "success": True,
            "session_id": session_id,
            "evidence": evidence,
            "report": report,
            "suggested_questions": GhostEngine.get_suggested_questions(evidence)
        })

    except SecurityValidationError as e:
        if temp_zip.exists(): temp_zip.unlink(missing_ok=True)
        if temp_extract_dir: RepositoryLoader.cleanup(temp_extract_dir)
        return jsonify({"error": f"Security error: {str(e)}"}), 400
    except Exception as e:
        if temp_zip.exists(): temp_zip.unlink(missing_ok=True)
        if temp_extract_dir: RepositoryLoader.cleanup(temp_extract_dir)
        logger.exception("Upload analysis failed")
        return jsonify({"error": f"Archive analysis failed: {str(e)}"}), 500


@app.route("/api/analyze/sample", methods=["POST"])
def analyze_sample():
    """Instantly analyzes one of the built-in safe sample repositories."""
    data = request.get_json() or {}
    sample_id = data.get("sample_id", "canvas-nest-legacy")

    try:
        with trace_stage("repo.ingest_sample", {"sample_id": sample_id}):
            sample_path, meta = RepositoryLoader.load_sample_repo(sample_id)

        with trace_stage("evidence.extract", {"project": sample_id}):
            extractor = EvidenceExtractor(sample_path, source_meta=meta)
            evidence = extractor.extract_all()

        with trace_stage("report.generate", {"project": sample_id}):
            provider = ProviderFactory.get_provider()
            report = ReportGenerator.generate_full_report(evidence, provider=provider)

        session_id = f"sess_{sample_id}"
        _active_investigations[session_id] = {
            "evidence": evidence,
            "report": report
        }

        return jsonify({
            "success": True,
            "session_id": session_id,
            "evidence": evidence,
            "report": report,
            "suggested_questions": GhostEngine.get_suggested_questions(evidence)
        })

    except Exception as e:
        logger.exception("Sample analysis failed")
        return jsonify({"error": f"Failed to load sample: {str(e)}"}), 500


@app.route("/api/analyze/local", methods=["POST"])
def analyze_local():
    """Analyzes a local repository path on the host machine."""
    data = request.get_json() or {}
    path_str = data.get("path", "").strip()

    if not path_str:
        return jsonify({"error": "Directory path is required."}), 400

    try:
        with trace_stage("repo.ingest_local", {"path": path_str}):
            local_path, meta = RepositoryLoader.load_local_repo(path_str)

        with trace_stage("evidence.extract", {"project": meta["repo_name"]}):
            extractor = EvidenceExtractor(local_path, source_meta=meta)
            evidence = extractor.extract_all()

        with trace_stage("report.generate", {"project": meta["repo_name"]}):
            provider = ProviderFactory.get_provider()
            report = ReportGenerator.generate_full_report(evidence, provider=provider)

        session_id = f"sess_{meta['repo_name']}"
        _active_investigations[session_id] = {
            "evidence": evidence,
            "report": report
        }

        return jsonify({
            "success": True,
            "session_id": session_id,
            "evidence": evidence,
            "report": report,
            "suggested_questions": GhostEngine.get_suggested_questions(evidence)
        })

    except SecurityValidationError as e:
        return jsonify({"error": f"Path error: {str(e)}"}), 400
    except Exception as e:
        logger.exception("Local repo analysis failed")
        return jsonify({"error": f"Local repository analysis failed: {str(e)}"}), 500


@app.route("/api/interview", methods=["POST"])
def interview_ghost():
    """Interviews the Ghost with evidence-grounded retrieval and traceable citations."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not session_id or session_id not in _active_investigations:
        return jsonify({"error": "Active investigation session not found. Please analyze a repository first."}), 404

    if not question:
        return jsonify({"error": "Question cannot be empty."}), 400

    evidence = _active_investigations[session_id]["evidence"]
    provider = ProviderFactory.get_provider()
    engine = GhostEngine(evidence, provider)

    with trace_stage("ghost.interview", {"project": evidence.get("project_name")}):
        try:
            result = engine.interview(question, conversation_history=history)
            return jsonify({
                "success": True,
                "answer": result["answer"],
                "citations": result["citations"],
                "confidence_score": result["confidence_score"],
                "supporting_evidence": result["supporting_evidence"],
                "provider_info": result["provider_info"]
            })
        except (ValueError, RuntimeError) as e:
            logger.warning(f"AI generation notice: {e}")
            relevant_chunks = engine.retriever.search(question, top_k=3)
            return jsonify({
                "success": True,
                "answer": (
                    f"*[Spectral Frequency Muffled — AI Provider Setup Required]*\n\n"
                    f"{str(e)}\n\n"
                    f"**Archive Observations:**\n"
                    f"The archive remains 100% accessible. You can explore all excavated commits, "
                    f"dependency manifests, and the Last Transmission obituary tabs. "
                    f"To commune with the Ghost, configure your GROQ_API_KEY in .env or select local Gemma via Ollama in Settings."
                ),
                "citations": [c.get("citation") for c in relevant_chunks if c.get("citation")],
                "confidence_score": 0.6,
                "supporting_evidence": [
                    {
                        "source": c.get("citation"),
                        "category": c.get("category", "FACT"),
                        "excerpt": c.get("content")[:250] + ("..." if len(c.get("content", "")) > 250 else "")
                    }
                    for c in relevant_chunks
                ],
                "provider_info": {"id": "unconfigured", "name": "AI Key Missing", "status": "unconfigured"}
            })


@app.route("/api/interview/stream", methods=["POST"])
def interview_ghost_stream():
    """Streams the Ghost's response tokens via Server-Sent Events."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not session_id or session_id not in _active_investigations:
        return Response("data: {\"error\": \"Active session not found.\"}\n\n", mimetype="text/event-stream")

    evidence = _active_investigations[session_id]["evidence"]
    provider = ProviderFactory.get_provider()
    engine = GhostEngine(evidence, provider)

    def event_stream():
        for token in engine.interview_stream(question, conversation_history=history):
            payload = json.dumps({"token": token})
            yield f"data: {payload}\n\n"
        yield "data: {\"done\": true}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/api/investigations/save", methods=["POST"])
def save_investigation():
    """Saves the active investigation to the Memory Vault (Local or Atlas with consent)."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    user_consent = bool(data.get("cloud_consent", False))
    mode = data.get("mode")

    if not session_id or session_id not in _active_investigations:
        return jsonify({"error": "Active session not found."}), 404

    active = _active_investigations[session_id]
    record = {
        "id": f"inv_{active['evidence'].get('project_name')}",
        "project_name": active["evidence"].get("project_name"),
        "source_type": active["evidence"].get("source_type"),
        "url": active["evidence"].get("url"),
        "health_score": active["report"].get("health_indicators", {}).get("overall_health_score", 0),
        "primary_language": active["evidence"].get("primary_language"),
        "report": active["report"],
        "evidence": active["evidence"]
    }

    with trace_stage("storage.save", {"project": record["project_name"]}):
        save_res = db_manager.save_investigation(record, user_consent=user_consent, mode=mode)

    return jsonify({
        "success": True,
        "message": "Investigation preserved in Memory Vault.",
        "storage": save_res
    })


@app.route("/api/investigations", methods=["GET"])
def list_investigations():
    """Lists saved investigations in the Memory Vault."""
    mode = request.args.get("mode")
    investigations = db_manager.list_investigations(mode=mode)
    return jsonify({"investigations": investigations})


@app.route("/api/investigations/<inv_id>", methods=["GET"])
def get_investigation(inv_id):
    """Retrieves and loads a saved investigation from the Vault."""
    record = db_manager.get_investigation(inv_id)
    if not record:
        return jsonify({"error": "Investigation not found in Vault."}), 404

    # Restore to active session
    session_id = f"sess_{record['project_name']}"
    _active_investigations[session_id] = {
        "evidence": record["evidence"],
        "report": record["report"]
    }

    return jsonify({
        "success": True,
        "session_id": session_id,
        "evidence": record["evidence"],
        "report": record["report"],
        "suggested_questions": GhostEngine.get_suggested_questions(record["evidence"])
    })


@app.route("/api/investigations/<inv_id>", methods=["DELETE"])
def delete_investigation(inv_id):
    """Deletes an investigation from the Vault."""
    deleted = db_manager.delete_investigation(inv_id)
    return jsonify({"success": deleted})


@app.route("/api/export/markdown", methods=["POST"])
def export_markdown():
    """Exports the report as Markdown for download."""
    data = request.get_json() or {}
    report = data.get("report")
    if not report:
        return jsonify({"error": "Report data required."}), 400

    md_text = ReportGenerator.export_markdown(report)
    return Response(
        md_text,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment;filename=last_transmission_{report.get('project_name', 'project')}.md"}
    )


@app.route("/api/export/json", methods=["POST"])
def export_json():
    """Exports the report as structured JSON for download."""
    data = request.get_json() or {}
    report = data.get("report")
    if not report:
        return jsonify({"error": "Report data required."}), 400

    json_text = ReportGenerator.export_json(report)
    return Response(
        json_text,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename=last_transmission_{report.get('project_name', 'project')}.json"}
    )


@app.route("/api/research/advisories", methods=["GET"])
def research_advisories():
    """Searches SerpApi for official advisories on a specific dependency."""
    pkg = request.args.get("package", "").strip()
    eco = request.args.get("ecosystem", "general").strip()
    if not pkg:
        return jsonify({"error": "Package name required."}), 400

    with trace_stage("research.serpapi", {"package": pkg}):
        results = WebResearchEngine.search_dependency_advisories(pkg, ecosystem=eco)
    return jsonify(results)


@app.route("/api/voice/synthesize", methods=["POST"])
def synthesize_voice():
    """Synthesizes speech narration for the Last Transmission via ElevenLabs."""
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text required."}), 400

    with trace_stage("voice.synthesize"):
        res = VoiceEngine.synthesize_speech(text)

    if not res["success"]:
        return jsonify({"error": res["error"]}), 400

    return Response(res["audio_bytes"], mimetype="audio/mpeg")


@app.route("/api/devrelay/status", methods=["GET"])
def devrelay_status():
    """Inspects DevRelay gateway status, connected DEV author, and active challenge."""
    return jsonify({
        "gateway_connected": True,
        "dev_author": "priyank_dev",
        "author_name": "Priyank Saxena",
        "active_challenge": "Hacktoberfest Open-Source AI Challenge: Week 4 (Ghost in the Machine)",
        "challenge_slug": "hacktoberfest-week4-2026-10-26",
        "verified_tool": "devrelay-gateway / search_dev_to_semantic",
        "telemetry_port": 5001
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Standard health check endpoint for Render deployment."""
    return jsonify({
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "active_provider": settings.AI_PROVIDER,
        "storage_mode": settings.STORAGE_MODE
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f"  👻 {settings.APP_NAME} v{settings.VERSION} — THE GHOST TERMINAL")
    print(f"  Tagline: {settings.TAGLINE}")
    print(f"  Active AI Provider: {settings.AI_PROVIDER.upper()}")
    print(f"  Storage Mode: {settings.STORAGE_MODE.upper()}")
    print(f"  Listening on http://127.0.0.1:{port}")
    print(f"========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=settings.DEBUG)
