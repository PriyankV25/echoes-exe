# 🪦 Echoes.exe — The Ghost Terminal
### Open-Source AI Digital Archaeologist
> *"Every abandoned project has a last known voice."*

[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.15-00ff88.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-00f0ff.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-20%20passed-20e070.svg)](tests/)
[![DevRelay](https://img.shields.io/badge/DevRelay-v0.1.26%20connected-f5a623.svg)](docs/DEVRELAY_DEMO.md)
[![Challenge](https://img.shields.io/badge/Hacktoberfest-Ghost%20in%20the%20Machine-ff5555.svg)](https://dev.to/challenges/hf26)

---

## 1. Project Vision & Core Principle

**Echoes.exe** is an AI-powered digital archaeologist that investigates forgotten, inactive, or legacy software projects. 

Developers input a public GitHub repository URL, upload a repository ZIP, or point to a local directory. The system analyzes observable Git commit histories, dependency manifests, documentation, tests, and file structures.

It reconstructs the project's technical history, renders an evidence-backed chronological timeline, conducts grounded terminal interviews with the project's digital ghost, generates a haunting final transmission (digital obituary), and formulates practical revival recommendations.

> **The Archaeologist's Core Law:**  
> *Horror is the presentation; evidence-based software archaeology is the product.*  
> Echoes.exe **never invents repository history, dates, issue numbers, vulnerabilities, or reasons why development halted**. If data is unrecorded or inaccessible, the ghost explicitly admits the digital void.

---

## 2. Architecture & Flow Diagram

```mermaid
flowchart TD
    subgraph UI ["Ghost Terminal Horror UI"]
        Boot["Boot Sequence<br/>(INITIALIZING GHOST PROTOCOL)"] --> Dashboard["Terminal Dashboard"]
        Dashboard --> Archaeology["Archaeology Observatory<br/>(Timeline & Evidence)"]
        Dashboard --> Interview["Interview the Ghost<br/>(Grounded Chat & Citations)"]
        Dashboard --> Obituary["Last Transmission<br/>(Digital Obituary & Voice)"]
        Dashboard --> Revival["Revival Lab<br/>(Prioritized Checklist)"]
        Dashboard --> Vault["Memory Vault<br/>(Saved Investigations)"]
        Dashboard --> Settings["Settings<br/>(Provider & Privacy Controls)"]
    end

    subgraph Ingest ["Safe Ingestion & Security"]
        InputURL["GitHub URL"] --> SSRFGuard["SSRF & Schema Validator"]
        InputZIP["ZIP Upload"] --> ZipSlipGuard["Zip Slip & Bomb Protection"]
        InputSample["Historic Samples"] --> SampleRepo["samples/canvas-nest-legacy<br/>samples/phantom-cli-py"]
        SSRFGuard --> Loader["Repository Loader"]
        ZipSlipGuard --> Loader
        SampleRepo --> Loader
    end

    subgraph CoreEngine ["Archaeological Engine"]
        Loader --> Extractor["Evidence Extractor<br/>(Git Logs, Manifests, READMEs)"]
        Extractor --> Health["Health Observatory<br/>(Activity, Recency, Test Indicators)"]
        Extractor --> Chunks["Verifiable Evidence Chunks"]
        Chunks --> Retriever["TF-IDF Evidence Retriever"]
    end

    subgraph AIProviders ["Dual AI Provider Architecture"]
        Retriever --> Factory["Provider Factory"]
        Factory -->|Hosted AI| Groq["Groq API<br/>(Llama 3.3 70B Versatile)"]
        Factory -->|Local Offline AI| Ollama["Gemma via Ollama<br/>(gemma3 on localhost:11434)"]
        Factory -->|Zero Credentials| Heuristic["Heuristic Fallback Provider<br/>(Deterministic Facts)"]
    end

    subgraph Grounding ["Verifiable Communication"]
        Groq --> GhostEngine["Ghost Engine & System Prompt"]
        Ollama --> GhostEngine
        Heuristic --> GhostEngine
        GhostEngine --> Validator["Citation Validator<br/>([Source: <commit_or_file>])"]
        Validator --> Output["Grounded Interview & Obituary"]
    end

    subgraph Storage ["Persistent Memory Layer"]
        Output --> StorageMgr["Storage Manager"]
        StorageMgr -->|Local Mode (Default)| SQLite["Local SQLite Vault<br/>(Zero Cloud Setup)"]
        StorageMgr -->|Atlas Mode (Consent Required)| Atlas["MongoDB Atlas<br/>(Cloud Memory & Vector Search)"]
    end

    subgraph Integrations ["Observability & External Services"]
        Extractor -.-> Sentry["Sentry Agent Tracing<br/>(6 Pipeline Stages)"]
        Extractor -.-> SerpApi["SerpApi<br/>(CVEs & Migration Guides)"]
        Obituary -.-> ElevenLabs["ElevenLabs<br/>(Voice Narration)"]
        CoreEngine -.-> DevRelay["DevRelay MCP Gateway<br/>(Port 5001 / priyank_dev)"]
    end
```

---

## 3. Visual Design — Ghost Terminal Horror UI

Echoes.exe delivers an atmospheric interface inspired by abandoned developer workstations, CRT monitors, and digital archaeology:

- **Color Palette:** Near-black obsidian (`#06090d`), deep charcoal glass panels (`#0e151e`), phosphor green terminal text (`#00ff88`), muted amber warnings (`#f5a623`), ghostly cyan highlights (`#00f0ff`), and blood-red errors (`#ff5555`).
- **Typography:** Refined heading font (`Cinzel`) paired with developer monospaced typography (`Fira Code`).
- **Atmospheric Effects:** Authentic CRT scanlines, subtle screen grain, gentle flicker, pulsating phosphor cursors, floating particle canvas, and corrupted text glitch transitions.
- **Audio Pulses:** Synthesized Web Audio API retro CRT tones with a quick-toggle mute button (`🔇`/`🔊`).
- **Accessibility:** Respects system `prefers-reduced-motion` and provides an in-app toggle for both Reduced Motion and CRT effects.
- **Responsive:** Fluid layout supporting mobile, tablet, and widescreen developer displays.

---

## 4. Key Application Views

1. **Boot Screen:** Mysterious animated initialization sequence (`INITIALIZING GHOST PROTOCOL...`, memory sector check, communicator bootstrap) with instant skip capability.
2. **Ghost Terminal Dashboard:** Ingestion controls for GitHub URLs, ZIP archives, packaged historic samples, or local folders, with real-time telemetry badges.
3. **Archaeology View:** Verifiable project metadata, genesis and silence commits, lifespan metrics, interactive monthly commit frequency chart, detected language breakdown, manifest dependencies, and inspectable evidence chunks.
4. **Interview the Ghost:** Interactive terminal chat with the project's digital ghost. Every answer retrieves relevant evidence chunks and cites exact commit hashes, dates, authors, or manifest files (`[Source: <path_or_commit>]`). Epistemic labels clearly mark `[FACT]`, `[INTERPRETATION]`, `[HYPOTHESIS]`, and `[UNRESOLVED]`.
5. **Last Transmission:** A digital obituary presenting the project's last observed activity, surviving components, technical debt, the Ghost's poetic closing farewell, and one-click export to Markdown (`.md`) or JSON (`.json`). Includes optional ElevenLabs voice narration.
6. **Revival Lab:** Actionable, prioritized engineering recommendations:
   - 🔴 **Critical:** Runtime environment isolation and vulnerable dependency audits.
   - 🟠 **High Priority:** Test suite regression resurrection.
   - 🟡 **Medium Priority:** Continuous integration restoration and contributing guidelines.
   - 🔵 **Optional Improvement:** Static typing annotations and containerization.
   *(Echoes.exe never executes repository code or runs arbitrary commands against uploaded projects).*
7. **Memory Vault:** Persistent SQLite and MongoDB Atlas archive. Allows re-opening past investigations, filtering by project name, or purging records.
8. **Settings:** Dynamic AI provider switching (Groq hosted vs. Gemma local), model ID overrides, live connectivity verification, and MongoDB Atlas privacy consent controls.

---

## 5. Dual AI Provider Architecture

Echoes.exe features a clean provider abstraction (`providers/base.py`) supporting seamless switching:

### Provider 1: Groq API (Hosted AI)
- Recommended for hosted demos and rapid cloud execution.
- Configured via server-side environment variables:
  ```env
  AI_PROVIDER=groq
  GROQ_API_KEY=gsk_your_key_here
  GROQ_MODEL=llama-3.3-70b-versatile
  ```
- Keys are strictly isolated on the backend and never leaked to frontend logs or client responses.

### Provider 2: Gemma via Ollama (100% Private, Local AI)
- Enables developers to run Google's **Gemma** models completely offline on their own hardware.
- No cloud API keys or external internet connectivity required.
- Configured via:
  ```env
  AI_PROVIDER=ollama
  OLLAMA_BASE_URL=http://localhost:11434
  OLLAMA_MODEL=gemma3
  ```
- The settings panel includes live ping diagnostics and setup instructions (`ollama run gemma3`).

### Heuristic Fallback Provider (Zero Credentials)
- When neither Groq nor Ollama are configured, Echoes.exe activates a deterministic heuristic provider.
- It derives answers directly from extracted evidence and clearly labels that an LLM key is needed for fluent conversational narration.

---

## 6. Persistent Memory & Vector Search (MongoDB Atlas & SQLite)

Echoes.exe implements a dual-layer storage architecture:

### Local Storage (Default, Zero-Config)
- Driven by SQLite (`data/echoes.db`).
- Requires zero external database setup. Persists investigations, evidence chunks, and conversation histories offline.

### MongoDB Atlas Cloud Storage & Vector Search
- Connects via `MONGODB_URI` and `MONGODB_DB_NAME`.
- **Strict User Privacy Consent:** In accordance with security requirements, Echoes.exe **never uploads repository contents, chunks, or metadata to Atlas without explicit user consent** (`check-cloud-consent` in Settings or API).
- **Atlas Vector Search:** Chunks can be queried using cosine similarity aggregation pipelines over index `vector_index`.
- **Graceful Fallback:** If the Vector Search index is not yet built on the user's Atlas cluster, the application gracefully falls back to local TF-IDF chunk retrieval without crashing.

---

## 7. External Research, Observability & Voice

- **SerpApi Research (`core/web_research.py`):** Queries official framework documentation, migration guides, and CVE security advisories for detected legacy dependencies. Results are clearly labeled as external web claims.
- **Sentry Observability (`core/observability.py`):** Tracks agent lifecycle stages (`repo.ingest`, `evidence.extract`, `retrieval.search`, `ghost.interview`, `report.generate`, `storage.save`). Telemetry sanitizes secrets and excludes private repository code.
- **ElevenLabs Voice Narration (`core/voice.py`):** Synthesizes the Ghost's final words using configurable voice IDs. Autoplay is strictly disabled.

---

## 8. DevRelay Integration & Verifiable Development Evidence

Echoes.exe was built using a genuine development workflow integrated with **DevRelay** (gateway version `0.1.26` running on Windows with local telemetry listening on port `5001`).

### Summary of DevRelay Contributions:
1. **Developer Identity Verification:** Authenticated as DEV user `priyank_dev` (Priyank Saxena, ID `4152477`) via `get_authenticated_user`.
2. **Challenge Alignment:** Aligned project directly with the active DEV challenge: **Hacktoberfest Open-Source AI Challenge: Week 4** (*"Ghost in the Machine"*, October 26–31, 2026), verified via `get_challenges` and registered event `hacktoberfest-open-source-ai-challenge-week-4` via `list_my_mlh_events`.
3. **Semantic Knowledge Gathering:** Used `search_dev_to_semantic` to consult real developer experiences on git history analysis and MongoDB Atlas RAG failure modes, ensuring our chunking, citation rules, and fallback mechanisms were informed by published community practices.
4. **Real Defect Resolution:** Used automated test backpressure to catch and correct parameter handling in test clients and added resilient error handling for missing AI credentials.
5. **Demonstration Guide:** Full step-by-step instructions for judges are provided in [`docs/DEVRELAY_DEMO.md`](docs/DEVRELAY_DEMO.md).

---

## 9. Quickstart & Local Setup

### Prerequisites
- Python 3.12 or 3.15
- Git CLI installed on system path

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/Echoes.git
cd Echoes
python -m pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` with your preferred settings:
```env
PORT=5000
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
STORAGE_MODE=local
```
*(To run 100% offline without Groq, set `AI_PROVIDER=ollama` and ensure `ollama run gemma3` is active).*

### 3. Generate Historical Sample Repositories (For Offline Testing)
```bash
python scripts/create_samples.py
```
This prepares:
- `samples/canvas-nest-legacy`: A dormant 2017 JavaScript particle canvas library with 2 historical commits.
- `samples/phantom-cli-py`: An unmaintained 2018 Python CLI tool with 4 pinned dependencies.

### 4. Run the Application
```bash
python app.py
```
Open your browser to: **`http://localhost:5000`**

---

## 10. Automated Testing

Echoes.exe includes comprehensive unit and integration tests covering evidence extraction, citation validation, AI providers, storage, SSRF security, and Flask API endpoints:

```bash
python -m pytest tests/
```

**Test Coverage Summary:**
- `test_evidence.py`: Git commit extraction, lifespan, dormancy duration, and manifest parsing.
- `test_citations.py`: Citation tag extraction, cross-referencing against indexed chunks, and TF-IDF ranker.
- `test_providers.py`: Groq connection handling, Ollama tags inspection, and factory dynamic switching.
- `test_storage.py`: Local SQLite CRUD operations and MongoDB Atlas cloud-consent privacy enforcement.
- `test_security.py`: SSRF blocking for GitHub URLs and Zip Slip path traversal rejection.
- `test_api.py`: Full end-to-end testing of Flask HTTP endpoints and report export.

---

## 11. Deployment on Render

Echoes.exe is configured for seamless deployment on Render using the included `render.yaml` and `Procfile`:

1. Connect your repository to Render.
2. Select **Web Service** or use **Blueprint** pointing to `render.yaml`.
3. Set your environment variables in the Render Dashboard:
   - `GROQ_API_KEY`: Your Groq API key.
   - `AI_PROVIDER`: `groq`
   - `STORAGE_MODE`: `local` (or `atlas` with `MONGODB_URI`).
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
6. Health check path: `/api/health`

---

## 12. Security & Privacy Safeguards

- **No Code Execution:** Echoes.exe never executes repository code, imports untrusted modules, runs arbitrary shell commands, or installs dependencies from uploaded projects.
- **SSRF Protection:** GitHub repository URLs are strictly validated. Internal networks, loopbacks, file URLs, and cloud metadata endpoints (`169.254.169.254`) are blocked.
- **Zip Slip & Bomb Defense:** Uploaded archives are inspected for path traversal sequences (`../../`) and checked for uncompressed file limits (max 5,000 files, max 90MB uncompressed).
- **Secret Isolation:** API keys remain strictly server-side. Public configuration endpoints expose only non-sensitive flags.
- **Explicit Cloud Consent:** Repository contents are never forwarded to MongoDB Atlas without explicit user opt-in.

---

## 13. License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
