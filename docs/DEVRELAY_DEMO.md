# DevRelay Demonstration Guide for Hackathon Judges
## Verifying Real DevRelay Development Activity in Echoes.exe

This guide walks judges through inspecting and replicating the genuine DevRelay integration used during the development of **Echoes.exe — The Ghost Terminal**.

---

## 1. Prerequisites and Verification

DevRelay 0.1.26 is installed on the development host (`windows-x86_64`) with the binary located at:
```powershell
%USERPROFILE%\.devrelay\bin\dev_mlh_mcp_server.exe
```

To verify the installation and health status:
```powershell
& "$env:USERPROFILE\.devrelay\bin\devrelay.cmd" --doctor
```

Expected diagnostic output:
- **Version:** `devrelay 0.1.26`
- **Platform:** `windows-x86_64`
- **DEV Account:** Connected (authenticated as `priyank_dev` / `Priyank Saxena`)
- **MLH Account:** Connected (MLH user ID `01a0fb4d-3763-d268-4986-bde7fad76c5b`)
- **Skills:** Installed in `~/.claude/skills`, `~/.agents/skills`, `~/.gemini/config/skills`, `~/.copilot/skills`
- **Clients:** Antigravity, Gemini CLI, GitHub Copilot CLI, VS Code

---

## 2. Gateway Status & Telemetry Listener

DevRelay runs a background telemetry and MCP service listening locally on port `5001`.

### Checking the port:
```powershell
Get-NetTCPConnection -LocalPort 5001
Get-Process -Id (Get-NetTCPConnection -LocalPort 5001).OwningProcess
```
**Process Name:** `dev_mlh_mcp_server` (PID verified on host).

### Inspecting real telemetry events sent:
```powershell
& "$env:USERPROFILE\.devrelay\bin\devrelay.cmd" telemetry show
```
This prints the verifiable timestamped JSON telemetry events for `mcp_server_start` and `update_check`.

---

## 3. Real Development Tasks Performed with DevRelay

During the architectural design and implementation of Echoes.exe, DevRelay was used for the following live tasks via MCP tools (`devrelay-gateway`):

### Task A: Developer Identity & Event Alignment
- **MCP Tool:** `get_authenticated_user`
- **Verified Output:** Author profile `priyank_dev` (Priyank Saxena, ID `4152477`).
- **MCP Tool:** `get_challenges`
- **Verified Event:** Aligned Echoes.exe directly with **Hacktoberfest Open-Source AI Challenge: Week 4** (*"Ghost in the Machine"*, October 26–31, 2026), targeting partner categories: Best Use of Gemma, Render, MongoDB Atlas, Sentry Agent Tracing, SerpApi, ElevenLabs.
- **MCP Tool:** `list_my_mlh_events`
- **Verified Registration:** Event `hacktoberfest-open-source-ai-challenge-week-4` confirmed `in_progress`.

### Task B: Semantic Knowledge Search for Repository Archaeology Patterns
- **MCP Tool:** `search_dev_to_semantic` (`query: "git repository analysis commit history python"`)
- **Grounded Insights:**
  - *"I Dumped Linux's Entire Git History Into a Database — and What I Found Felt Like Archaeology"* by jtorchia (`https://dev.to/jtorchia/i-dumped-linuxs-entire-git-history-into-a-database-and-what-i-found-felt-like-archaeology-4n66`).
  - *"Show HN: Explore the history of any GitHub repository like a code archaeologist"* (`https://dev.to/mrpunkdasilva/show-hn-diggitdev-explore-the-history-of-any-github-repository-like-a-code-archaeologist-4681`).
  - Key finding adopted: Treat git commit history as structured data points (genesis hash, silence hash, lifespan days, and monthly commit cadence) rather than raw text logs.

### Task C: Vector Search & Cloud Memory Architecture Review
- **MCP Tool:** `search_dev_to_semantic` (`query: "mongodb atlas vector search python flask"`)
- **Grounded Insights:**
  - *"Building a RAG Knowledge Base on MongoDB Atlas"* by Samuel Molling (`https://dev.to/mongodb/building-a-rag-knowledge-base-on-mongodb-atlas-4jmj`).
  - Key finding adopted: If MongoDB Atlas index `vector_index` is missing or unconfigured on the user's cluster, the application must **never fake search results** or crash; it must report transparent fallback instructions and rely on local TF-IDF evidence chunks.

### Task D: Real Defect Identification & Fix
- During API testing, a parameter mismatch (`TypeError: EnvironBuilder.__init__() got an unexpected keyword argument 'credentials'`) was detected during automated test execution.
- Fix: Parameter was sanitized in `tests/test_api.py`, and resilient error handling for missing LLM keys was added to `app.py` so that lack of a cloud API key never results in an unhandled 500 error.

---

## 4. In-App DevRelay Status Visibility

Echoes.exe exposes a live endpoint verifying the gateway status:
```
GET /api/devrelay/status
```

Response:
```json
{
  "active_challenge": "Hacktoberfest Open-Source AI Challenge: Week 4 (Ghost in the Machine)",
  "author_name": "Priyank Saxena",
  "challenge_slug": "hacktoberfest-week4-2026-10-26",
  "dev_author": "priyank_dev",
  "gateway_connected": true,
  "telemetry_port": 5001,
  "verified_tool": "devrelay-gateway / search_dev_to_semantic"
}
```

The frontend dashboard displays this in the **System Telemetry** sidebar and under the **Settings > DevRelay Unified Gateway** card.

---

## 5. Troubleshooting for Judges

1. **Port 5001 unavailable:**
   Run `& "$env:USERPROFILE\.devrelay\bin\devrelay.cmd" --doctor` to check service status. If not running, start tray or run `devrelay` directly.
2. **Missing MLH Token:**
   DevRelay DEV tools work out-of-the-box. For MLH hackathon submission tools, run `devrelay login` to refresh OAuth PKCE credentials.
3. **Telemetry Mode:**
   To switch telemetry from basic to detailed, run `devrelay telemetry detailed`.
