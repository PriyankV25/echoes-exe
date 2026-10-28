/**
 * Echoes.exe — The Ghost Terminal Client Engine
 * Open-Source AI Digital Archaeologist
 */

document.addEventListener("DOMContentLoaded", () => {
    // Application State
    const state = {
        activeTab: "dashboard",
        activeSessionId: null,
        activeEvidence: null,
        activeReport: null,
        activeProvider: "groq",
        storageMode: "local",
        cloudConsent: false,
        crtEnabled: true,
        reducedMotion: false,
        audioEnabled: false,
        chatHistory: []
    };

    // Synthesized Sound Generator (Web Audio API)
    let audioCtx = null;
    function playTerminalTone(freq = 440, type = "sine", duration = 0.08, gainVal = 0.04) {
        if (!state.audioEnabled) return;
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) {
            console.debug("Audio pulse muted:", e);
        }
    }

    // 1. BOOT SEQUENCE INITIALIZATION
    function initBootSequence() {
        const bootScreen = document.getElementById("boot-screen");
        const bootProgress = document.getElementById("boot-progress");
        const skipBtn = document.getElementById("boot-skip-btn");

        let progress = 0;
        const interval = setInterval(() => {
            progress += 15;
            if (bootProgress) bootProgress.style.width = `${progress}%`;
            playTerminalTone(200 + progress * 8, "square", 0.03, 0.015);

            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(dismissBootScreen, 400);
            }
        }, 120);

        function dismissBootScreen() {
            clearInterval(interval);
            if (bootScreen) {
                bootScreen.classList.add("hidden");
                playTerminalTone(880, "sine", 0.2, 0.05);
            }
        }

        if (skipBtn) skipBtn.addEventListener("click", dismissBootScreen);
    }

    // 2. PARTICLE DUST BACKGROUND CANVAS
    function initParticleCanvas() {
        const canvas = document.getElementById("particle-canvas");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        let particles = [];

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener("resize", resize);
        resize();

        for (let i = 0; i < 45; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.4,
                size: Math.random() * 2 + 0.8,
                alpha: Math.random() * 0.5 + 0.2
            });
        }

        function render() {
            if (state.reducedMotion) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "#00ff88";

            for (let p of particles) {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;

                ctx.globalAlpha = p.alpha;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();
            }
            requestAnimationFrame(render);
        }
        render();
    }

    // 3. TAB NAVIGATION
    function initTabs() {
        const navTabs = document.querySelectorAll(".nav-tab");
        navTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const target = tab.dataset.tab;
                switchTab(target);
            });
        });
    }

    function switchTab(tabId) {
        state.activeTab = tabId;
        document.querySelectorAll(".nav-tab").forEach(t => {
            t.classList.toggle("active", t.dataset.tab === tabId);
        });
        document.querySelectorAll(".tab-view").forEach(v => {
            v.classList.toggle("active", v.id === `tab-${tabId}`);
        });
        playTerminalTone(520, "sine", 0.05);

        if (tabId === "memory-vault") {
            loadVaultRecords();
        }
    }

    // 4. SCAN OVERLAY CONTROLS
    const scanOverlay = document.getElementById("scan-overlay");
    const scanStatusText = document.getElementById("scan-status-text");
    const scanDetailText = document.getElementById("scan-detail-text");
    const scanLines = document.getElementById("scan-terminal-lines");

    function showScan(title, detail) {
        if (!scanOverlay) return;
        scanStatusText.textContent = title || "SCANNING ARCHIVE...";
        scanDetailText.textContent = detail || "Recovering commit history and syntax specters...";
        scanLines.innerHTML = `<div>> Initializing archaeological probe...</div>`;
        scanOverlay.classList.remove("hidden");
    }

    function updateScanLog(msg) {
        if (!scanLines) return;
        const line = document.createElement("div");
        line.textContent = `> ${msg}`;
        scanLines.appendChild(line);
        scanLines.scrollTop = scanLines.scrollHeight;
    }

    function hideScan() {
        if (scanOverlay) scanOverlay.classList.add("hidden");
    }

    // 5. INGESTION HANDLING (URL, ZIP, SAMPLES, LOCAL)
    function initIngestion() {
        // Mode buttons
        const modeBtns = document.querySelectorAll(".mode-btn");
        modeBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                modeBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const mode = btn.dataset.mode;
                document.querySelectorAll(".mode-panel").forEach(p => p.classList.remove("active"));
                const targetPanel = document.getElementById(`mode-panel-${mode}`);
                if (targetPanel) targetPanel.classList.add("active");
                playTerminalTone(600, "sine", 0.04);
            });
        });

        // Mode 1: GitHub URL
        const btnUrl = document.getElementById("btn-analyze-url");
        const inputUrl = document.getElementById("input-repo-url");
        if (btnUrl && inputUrl) {
            btnUrl.addEventListener("click", async () => {
                const url = inputUrl.value.trim();
                if (!url) {
                    alert("Please enter a valid GitHub repository URL.");
                    return;
                }
                showScan("INGESTING GITHUB REPOSITORY...", "Verifying URL and executing shallow git clone...");
                updateScanLog(`Validating format: ${url}`);
                try {
                    const resp = await fetch("/api/analyze/url", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url })
                    });
                    const data = await resp.json();
                    if (!resp.ok) throw new Error(data.error || "Analysis failed.");
                    handleAnalysisSuccess(data);
                } catch (err) {
                    alert(`Excavation Failed: ${err.message}`);
                } finally {
                    hideScan();
                }
            });
        }

        // Mode 2: ZIP Upload
        const dropZone = document.getElementById("zip-drop-zone");
        const fileInput = document.getElementById("file-zip-input");
        const btnUpload = document.getElementById("btn-analyze-upload");
        const selectedFileDisplay = document.getElementById("selected-file-name");
        let selectedFile = null;

        if (dropZone && fileInput) {
            dropZone.addEventListener("click", () => fileInput.click());
            dropZone.addEventListener("dragover", (e) => {
                e.preventDefault();
                dropZone.classList.add("dragover");
            });
            dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
            dropZone.addEventListener("drop", (e) => {
                e.preventDefault();
                dropZone.classList.remove("dragover");
                if (e.dataTransfer.files.length > 0) {
                    handleFileSelect(e.dataTransfer.files[0]);
                }
            });
            fileInput.addEventListener("change", () => {
                if (fileInput.files.length > 0) {
                    handleFileSelect(fileInput.files[0]);
                }
            });
        }

        function handleFileSelect(file) {
            selectedFile = file;
            selectedFileDisplay.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
            selectedFileDisplay.classList.remove("hidden");
            btnUpload.disabled = false;
            playTerminalTone(700, "sine", 0.05);
        }

        if (btnUpload) {
            btnUpload.addEventListener("click", async () => {
                if (!selectedFile) return;
                showScan("UNPACKING ARCHIVE...", "Verifying path boundaries and extracting evidence...");
                updateScanLog(`Unpacking ${selectedFile.name}...`);
                const formData = new FormData();
                formData.append("archive", selectedFile);

                try {
                    const resp = await fetch("/api/analyze/upload", {
                        method: "POST",
                        body: formData
                    });
                    const data = await resp.json();
                    if (!resp.ok) throw new Error(data.error || "Upload analysis failed.");
                    handleAnalysisSuccess(data);
                } catch (err) {
                    alert(`Archive Excavation Failed: ${err.message}`);
                } finally {
                    hideScan();
                }
            });
        }

        // Mode 3: Historic Samples
        document.querySelectorAll(".sample-card").forEach(card => {
            const btn = card.querySelector(".sample-select-btn");
            if (btn) {
                btn.addEventListener("click", async () => {
                    const sampleId = card.dataset.sample;
                    showScan(`EXCAVATING HISTORIC SAMPLE [${sampleId}]...`, "Recovering commit history from packaged snapshot...");
                    updateScanLog(`Loading sample ${sampleId}...`);
                    try {
                        const resp = await fetch("/api/analyze/sample", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ sample_id: sampleId })
                        });
                        const data = await resp.json();
                        if (!resp.ok) throw new Error(data.error || "Sample analysis failed.");
                        handleAnalysisSuccess(data);
                    } catch (err) {
                        alert(`Sample Load Error: ${err.message}`);
                    } finally {
                        hideScan();
                    }
                });
            }
        });

        // Mode 4: Local Directory Path
        const btnLocal = document.getElementById("btn-analyze-local");
        const inputLocal = document.getElementById("input-local-path");
        if (btnLocal && inputLocal) {
            btnLocal.addEventListener("click", async () => {
                const path = inputLocal.value.trim();
                if (!path) {
                    alert("Please enter a local directory path.");
                    return;
                }
                showScan("INSPECTING LOCAL DIRECTORY...", "Scanning files and local git history...");
                try {
                    const resp = await fetch("/api/analyze/local", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ path })
                    });
                    const data = await resp.json();
                    if (!resp.ok) throw new Error(data.error || "Local analysis failed.");
                    handleAnalysisSuccess(data);
                } catch (err) {
                    alert(`Local Analysis Failed: ${err.message}`);
                } finally {
                    hideScan();
                }
            });
        }
    }

    // 6. POPULATE INVESTIGATION DATA ACROSS ALL VIEWS
    function handleAnalysisSuccess(data) {
        state.activeSessionId = data.session_id;
        state.activeEvidence = data.evidence;
        state.activeReport = data.report;

        // Update Header Pill
        const pill = document.getElementById("active-project-name");
        if (pill) pill.textContent = `ACTIVE // ${data.evidence.project_name.toUpperCase()}`;

        // Populate Archaeology View
        renderArchaeologyView(data.evidence, data.report);

        // Populate Ghost Interview
        initGhostInterview(data.evidence, data.suggested_questions);

        // Populate Last Transmission (Digital Obituary)
        renderLastTransmission(data.report);

        // Populate Revival Lab
        renderRevivalLab(data.report.revival_lab);

        // Automatically switch to Archaeology tab
        switchTab("archaeology");
        playTerminalTone(950, "sine", 0.15);
    }

    // 7. RENDER ARCHAEOLOGY VIEW
    function renderArchaeologyView(evidence, report) {
        const titleEl = document.getElementById("arch-repo-title");
        const tagsEl = document.getElementById("arch-repo-tags");
        const scoreEl = document.getElementById("arch-health-score");
        const labelEl = document.getElementById("arch-health-label");

        if (titleEl) titleEl.textContent = evidence.project_name;
        if (tagsEl) {
            tagsEl.innerHTML = `
                <span class="meta-pill highlight">${evidence.primary_language || 'Unknown'}</span>
                <span class="meta-pill">${evidence.total_files} files</span>
                <span class="meta-pill">${(evidence.total_loc || 0).toLocaleString()} lines of code</span>
                <span class="meta-pill">Source: ${evidence.source_type}</span>
            `;
        }

        const health = report.health_indicators || {};
        if (scoreEl) scoreEl.textContent = health.overall_health_score || "--";
        if (labelEl) labelEl.textContent = health.activity?.label || "EVIDENCE INDEXED";

        // Timeline Metrics
        const git = evidence.git_evidence || {};
        const fc = git.first_commit;
        const lc = git.latest_commit;

        const tmGenDate = document.getElementById("tm-genesis-date");
        const tmGenSub = document.getElementById("tm-genesis-sub");
        const tmSilDate = document.getElementById("tm-silence-date");
        const tmSilSub = document.getElementById("tm-silence-sub");
        const tmLifespan = document.getElementById("tm-lifespan");
        const tmTotalCommits = document.getElementById("tm-total-commits");
        const tmDormancy = document.getElementById("tm-dormancy");

        if (tmGenDate) tmGenDate.textContent = fc ? fc.date.slice(0, 10) : "Unrecorded";
        if (tmGenSub) tmGenSub.textContent = fc ? `Commit ${fc.short_hash} by ${fc.author}` : "No genesis commit found";
        if (tmSilDate) tmSilDate.textContent = lc ? lc.date.slice(0, 10) : "Unrecorded";
        if (tmSilSub) tmSilSub.textContent = lc ? `Commit ${lc.short_hash} by ${lc.author}` : "No final commit found";
        if (tmLifespan) tmLifespan.textContent = git.lifespan_days != null ? `${git.lifespan_days} days` : "Unknown";
        if (tmTotalCommits) tmTotalCommits.textContent = `${git.total_commits || 0} commits recorded`;
        if (tmDormancy) tmDormancy.textContent = git.days_since_last_commit != null ? `${git.days_since_last_commit}` : "--";

        // Activity Bar Chart
        const chartEl = document.getElementById("activity-chart");
        if (chartEl) {
            chartEl.innerHTML = "";
            const activity = git.commit_activity || {};
            const entries = Object.entries(activity);
            if (entries.length === 0) {
                chartEl.innerHTML = `<div style="color:var(--text-muted);font-size:0.75rem;padding:20px;">No monthly commit cadences recorded.</div>`;
            } else {
                const maxCount = Math.max(...entries.map(e => e[1]), 1);
                entries.slice(-14).forEach(([month, count]) => {
                    const col = document.createElement("div");
                    col.className = "chart-bar-col";
                    const heightPercent = Math.max(12, (count / maxCount) * 85);
                    col.innerHTML = `
                        <div class="chart-bar-fill" style="height:${heightPercent}px;" title="${month}: ${count} commits"></div>
                        <div class="chart-bar-label">${month.slice(2)}</div>
                    `;
                    chartEl.appendChild(col);
                });
            }
        }

        // Tech Stack & Manifests
        const stackEl = document.getElementById("stack-breakdown-list");
        if (stackEl) {
            const langs = evidence.language_breakdown || {};
            stackEl.innerHTML = Object.entries(langs).map(([lang, count]) => `
                <div style="display:flex;justify-content:space-between;padding:4px 0;font-family:var(--font-mono);font-size:0.8rem;">
                    <span style="color:var(--text-phosphor);">${lang}</span>
                    <span style="color:var(--text-muted);">${count} files</span>
                </div>
            `).join("") || "No code files detected.";
        }

        const manifestBox = document.getElementById("manifest-content-box");
        if (manifestBox) {
            const manifests = evidence.manifests || {};
            let mText = [];
            if (manifests.package_json) {
                mText.push(`package.json: ${Object.keys(manifests.package_json.dependencies || {}).length} dependencies`);
                mText.push(JSON.stringify(manifests.package_json.dependencies || {}, null, 2));
            }
            if (manifests.requirements_txt) {
                mText.push(`requirements.txt: ${manifests.requirements_txt.count} dependencies`);
                mText.push(Object.entries(manifests.requirements_txt.dependencies || {}).map(([k, v]) => `${k}==${v}`).join("\n"));
            }
            manifestBox.textContent = mText.join("\n\n") || "No package manifests detected in root.";
        }

        // Evidence Chunks
        const chunkCountEl = document.getElementById("chunk-count-badge");
        const chunkListEl = document.getElementById("evidence-chunks-list");
        const chunks = evidence.evidence_chunks || [];
        if (chunkCountEl) chunkCountEl.textContent = chunks.length;
        if (chunkListEl) {
            chunkListEl.innerHTML = chunks.map(c => `
                <div class="evidence-chunk-item">
                    <div class="chunk-header">
                        <span class="chunk-id">${c.chunk_id}</span>
                        <span class="chunk-source">${c.citation}</span>
                        <span class="chunk-cat">${c.category}</span>
                    </div>
                    <div class="chunk-text">${escapeHtml(c.content.slice(0, 300))}${c.content.length > 300 ? '...' : ''}</div>
                </div>
            `).join("");
        }
    }

    // 8. INTERVIEW THE GHOST
    function initGhostInterview(evidence, suggested) {
        const pillsContainer = document.getElementById("suggested-pills");
        const ghostTitle = document.getElementById("ghost-title-name");
        if (ghostTitle) ghostTitle.textContent = `SPECTRAL MANIFESTATION OF ${evidence.project_name.toUpperCase()}`;

        if (pillsContainer && suggested) {
            pillsContainer.innerHTML = suggested.map(q => `
                <button type="button" class="sugg-pill">${escapeHtml(q)}</button>
            `).join("");

            pillsContainer.querySelectorAll(".sugg-pill").forEach(p => {
                p.addEventListener("click", () => {
                    const chatInput = document.getElementById("chat-user-input");
                    if (chatInput) {
                        chatInput.value = p.textContent;
                        chatInput.focus();
                    }
                });
            });
        }
    }

    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-user-input");
    const chatMessages = document.getElementById("chat-messages");

    if (chatForm && chatInput) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const question = chatInput.value.trim();
            if (!question || !state.activeSessionId) return;

            // Append User Message
            appendChatMessage("USER", question, "user-msg");
            chatInput.value = "";
            state.chatHistory.push({ role: "user", content: question });

            // Create Ghost Placeholder
            const ghostMsgEl = appendChatMessage("THE GHOST", "Communing with the void...", "ghost-msg");
            const bodyEl = ghostMsgEl.querySelector(".msg-body");

            try {
                const resp = await fetch("/api/interview", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: state.activeSessionId,
                        question: question,
                        history: state.chatHistory
                    })
                });
                const data = await resp.json();
                if (!resp.ok) throw new Error(data.error || "Ghost communication severed.");

                // Render Answer
                bodyEl.innerHTML = formatGhostText(data.answer);
                state.chatHistory.push({ role: "assistant", content: data.answer });

                // Update Citations Inspector
                renderCitationsInspector(data);
                playTerminalTone(440, "sine", 0.08);

            } catch (err) {
                bodyEl.textContent = `[Spectral Malfunction: ${err.message}]`;
            }
        });
    }

    function appendChatMessage(sender, text, className) {
        const msg = document.createElement("div");
        msg.className = `chat-msg ${className}`;
        const timeStr = new Date().toTimeString().slice(0, 8);
        msg.innerHTML = `
            <div class="msg-header">
                <span class="msg-sender">[${sender}]</span>
                <span class="msg-time">${timeStr}</span>
            </div>
            <div class="msg-body">${escapeHtml(text)}</div>
        `;
        chatMessages.appendChild(msg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msg;
    }

    function formatGhostText(raw) {
        let text = escapeHtml(raw);
        // Highlight citation tags
        text = text.replace(/\[Source:\s*([^\]]+)\]/gi, '<span style="color:var(--text-cyan);font-weight:700;">[Source: $1]</span>');
        text = text.replace(/\[FACT\]/g, '<span style="color:var(--text-phosphor);font-weight:700;">[FACT]</span>');
        text = text.replace(/\[INTERPRETATION\]/g, '<span style="color:var(--text-cyan);font-weight:700;">[INTERPRETATION]</span>');
        text = text.replace(/\[HYPOTHESIS\]/g, '<span style="color:var(--text-amber);font-weight:700;">[HYPOTHESIS]</span>');
        text = text.replace(/\[UNRESOLVED\]/g, '<span style="color:var(--text-red);font-weight:700;">[UNRESOLVED]</span>');
        return text.replace(/\n/g, "<br>");
    }

    function renderCitationsInspector(data) {
        const confEl = document.getElementById("inspect-confidence");
        const chunksContainer = document.getElementById("inspector-chunks");

        if (confEl) confEl.textContent = `${Math.round((data.confidence_score || 0.9) * 100)}% Grounded`;

        if (chunksContainer && data.supporting_evidence) {
            chunksContainer.innerHTML = data.supporting_evidence.map(item => `
                <div class="insp-excerpt-card">
                    <div class="iec-source">📌 ${escapeHtml(item.source)}</div>
                    <div class="iec-text">${escapeHtml(item.excerpt)}</div>
                </div>
            `).join("");
        }
    }

    // 9. RENDER LAST TRANSMISSION (DIGITAL OBITUARY)
    function renderLastTransmission(report) {
        const ident = report.identity || {};
        const time = report.timeline || {};
        const ghost = report.spectral_transmission || {};

        document.getElementById("obit-title").textContent = report.project_name;
        document.getElementById("obit-subtitle").textContent = ident.synopsis || "Last known voice of a forgotten repository";

        document.getElementById("obit-meta-row").innerHTML = `
            <span>PRIMARY: ${ident.primary_language || 'Unknown'}</span>
            <span>FILES: ${ident.total_files}</span>
            <span>ACTIVE LIFESPAN: ${time.lifespan_days || 'N/A'} DAYS</span>
            <span>STATUS: ${report.health_indicators?.activity?.label || 'DORMANT'}</span>
        `;

        const fc = time.genesis_commit || {};
        document.getElementById("obit-genesis-content").innerHTML = `
            <strong>Hash:</strong> <code>${fc.short_hash}</code><br>
            <strong>Date:</strong> ${fc.date}<br>
            <strong>Author:</strong> ${escapeHtml(fc.author)}<br>
            <strong>Message:</strong> <em>"${escapeHtml(fc.message)}"</em>
        `;

        const lc = time.silence_commit || {};
        document.getElementById("obit-silence-content").innerHTML = `
            <strong>Hash:</strong> <code>${lc.short_hash}</code><br>
            <strong>Date:</strong> ${lc.date}<br>
            <strong>Author:</strong> ${escapeHtml(lc.author)}<br>
            <strong>Message:</strong> <em>"${escapeHtml(lc.message)}"</em>
        `;

        document.getElementById("obit-synopsis-content").textContent = ident.synopsis || "No README synopsis available.";

        const healthFindings = report.health_indicators?.documentation?.findings || [];
        document.getElementById("obit-health-content").innerHTML = healthFindings.map(f => `<div>• ${escapeHtml(f)}</div>`).join("") || "Evidence analysis completed.";

        document.getElementById("obit-final-message").textContent = ghost.final_message || "";
        document.getElementById("obit-disclaimer").textContent = ghost.disclaimer || "";
    }

    // Export Buttons
    const btnMd = document.getElementById("btn-export-markdown");
    const btnJson = document.getElementById("btn-export-json");
    const btnSaveVault = document.getElementById("btn-save-vault");

    if (btnMd) {
        btnMd.addEventListener("click", async () => {
            if (!state.activeReport) return;
            const resp = await fetch("/api/export/markdown", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ report: state.activeReport })
            });
            const blob = await resp.blob();
            downloadBlob(blob, `last_transmission_${state.activeReport.project_name}.md`);
        });
    }

    if (btnJson) {
        btnJson.addEventListener("click", async () => {
            if (!state.activeReport) return;
            const resp = await fetch("/api/export/json", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ report: state.activeReport })
            });
            const blob = await resp.blob();
            downloadBlob(blob, `last_transmission_${state.activeReport.project_name}.json`);
        });
    }

    if (btnSaveVault) {
        btnSaveVault.addEventListener("click", async () => {
            if (!state.activeSessionId) return;
            try {
                const resp = await fetch("/api/investigations/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: state.activeSessionId,
                        cloud_consent: state.cloudConsent,
                        mode: state.storageMode
                    })
                });
                const data = await resp.json();
                if (data.success) {
                    alert("Investigation preserved safely in Memory Vault.");
                    playTerminalTone(880, "sine", 0.1);
                }
            } catch (e) {
                alert(`Save failed: ${e.message}`);
            }
        });
    }

    // Voice Narration (ElevenLabs)
    const btnVoice = document.getElementById("btn-voice-narrate");
    const audioPlayer = document.getElementById("ghost-audio-player");
    if (btnVoice && audioPlayer) {
        btnVoice.addEventListener("click", async () => {
            const text = document.getElementById("obit-final-message").textContent;
            if (!text) return;
            btnVoice.textContent = "SYNTHESIZING GHOST VOICE...";
            btnVoice.disabled = true;

            try {
                const resp = await fetch("/api/voice/synthesize", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text })
                });
                if (!resp.ok) {
                    const err = await resp.json();
                    throw new Error(err.error || "Voice synthesis failed.");
                }
                const audioBlob = await resp.blob();
                audioPlayer.src = URL.createObjectURL(audioBlob);
                audioPlayer.play();
                btnVoice.textContent = "⏹️ STOP TRANSMISSION";
                btnVoice.disabled = false;
            } catch (err) {
                alert(`Voice synthesis note: ${err.message}`);
                btnVoice.textContent = "🔊 HEAR THE GHOST";
                btnVoice.disabled = false;
            }
        });
    }

    function downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    // 10. RENDER REVIVAL LAB
    function renderRevivalLab(revivalLab) {
        const countsEl = document.getElementById("revival-priority-counts");
        const listEl = document.getElementById("revival-checklist-list");
        if (!revivalLab) return;

        const pCounts = revivalLab.priority_counts || {};
        if (countsEl) {
            countsEl.innerHTML = `
                <span class="ric-priority p-Critical">Critical: ${pCounts.critical || 0}</span>
                <span class="ric-priority p-High">High: ${pCounts.high || 0}</span>
                <span class="ric-priority p-Medium">Medium: ${pCounts.medium || 0}</span>
                <span class="ric-priority p-Optional">Optional: ${pCounts.optional || 0}</span>
            `;
        }

        const recs = revivalLab.recommendations || [];
        if (listEl) {
            listEl.innerHTML = recs.map(r => `
                <div class="revival-item-card p-${r.priority}">
                    <div class="ric-top">
                        <span class="ric-priority">${r.priority}</span>
                        <span class="ric-id">${r.id}</span>
                    </div>
                    <div class="ric-title">${escapeHtml(r.title)}</div>
                    <div class="ric-evidence">Evidence Grounding: <code>${escapeHtml(r.evidence_source)}</code></div>
                    <div class="ric-rationale">${escapeHtml(r.rationale)}</div>
                    <div class="ric-action">>_ Advisory Action: ${escapeHtml(r.action)}</div>
                </div>
            `).join("");
        }
    }

    // 11. MEMORY VAULT RECORDS
    async function loadVaultRecords() {
        const grid = document.getElementById("vault-records-grid");
        if (!grid) return;
        try {
            const resp = await fetch("/api/investigations");
            const data = await resp.json();
            const items = data.investigations || [];

            if (items.length === 0) {
                grid.innerHTML = `
                    <div class="vault-empty-state">
                        <span class="empty-icon">🪦</span>
                        <div class="empty-title">THE VAULT IS QUIET</div>
                        <div class="empty-sub">No investigations saved yet. Ingest a repository and click 'PRESERVE IN VAULT'.</div>
                    </div>
                `;
                return;
            }

            grid.innerHTML = items.map(inv => `
                <div class="vault-card" data-id="${inv.id}">
                    <div>
                        <div class="vc-title">${escapeHtml(inv.project_name)}</div>
                        <div class="vc-meta">
                            <span>Health: ${inv.health_score}/100</span> • 
                            <span>Lang: ${inv.primary_language}</span> • 
                            <span>${inv.created_at.slice(0, 10)}</span>
                        </div>
                    </div>
                    <div class="vc-actions">
                        <button class="ghost-btn-sm ghost-btn-primary btn-load-vault" data-id="${inv.id}">
                            LOAD ARCHIVE
                        </button>
                        <button class="ghost-btn-sm ghost-btn-secondary btn-del-vault" data-id="${inv.id}">
                            DELETE
                        </button>
                    </div>
                </div>
            `).join("");

            grid.querySelectorAll(".btn-load-vault").forEach(btn => {
                btn.addEventListener("click", () => loadInvestigationFromVault(btn.dataset.id));
            });

            grid.querySelectorAll(".btn-del-vault").forEach(btn => {
                btn.addEventListener("click", () => deleteInvestigationFromVault(btn.dataset.id));
            });

        } catch (e) {
            console.error("Failed to load vault:", e);
        }
    }

    async function loadInvestigationFromVault(invId) {
        showScan("RETRIEVING FROM MEMORY VAULT...", `Loading investigation ${invId}...`);
        try {
            const resp = await fetch(`/api/investigations/${invId}`);
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error || "Load failed.");
            handleAnalysisSuccess(data);
        } catch (e) {
            alert(e.message);
        } finally {
            hideScan();
        }
    }

    async function deleteInvestigationFromVault(invId) {
        if (!confirm("Permanently erase this investigation from the Vault?")) return;
        try {
            await fetch(`/api/investigations/${invId}`, { method: "DELETE" });
            loadVaultRecords();
        } catch (e) {
            alert(e.message);
        }
    }

    // 12. SETTINGS & PROVIDER CONTROLS
    function initSettings() {
        const radioGroq = document.getElementById("radio-prov-groq");
        const radioOllama = document.getElementById("radio-prov-ollama");
        const fieldsGroq = document.getElementById("fields-groq");
        const fieldsOllama = document.getElementById("fields-ollama");
        const btnSave = document.getElementById("btn-save-settings");
        const btnTest = document.getElementById("btn-test-providers");
        const testResults = document.getElementById("provider-test-results");

        function updateFieldsVisibility() {
            const isGroq = radioGroq && radioGroq.checked;
            if (fieldsGroq) fieldsGroq.classList.toggle("hidden", !isGroq);
            if (fieldsOllama) fieldsOllama.classList.toggle("hidden", isGroq);
        }

        if (radioGroq) radioGroq.addEventListener("change", updateFieldsVisibility);
        if (radioOllama) radioOllama.addEventListener("change", updateFieldsVisibility);

        if (btnSave) {
            btnSave.addEventListener("click", async () => {
                const choice = radioGroq && radioGroq.checked ? "groq" : "ollama";
                const groqModel = document.getElementById("input-groq-model")?.value;
                const ollamaUrl = document.getElementById("input-ollama-url")?.value;
                const ollamaModel = document.getElementById("input-ollama-model")?.value;
                const storageChoice = document.getElementById("select-storage-mode")?.value;

                try {
                    const resp = await fetch("/api/settings", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            ai_provider: choice,
                            groq_model: groqModel,
                            ollama_base_url: ollamaUrl,
                            ollama_model: ollamaModel,
                            storage_mode: storageChoice
                        })
                    });
                    const res = await resp.json();
                    if (res.success) {
                        state.activeProvider = choice;
                        document.getElementById("header-provider-val").textContent = choice.toUpperCase();
                        alert(res.message);
                    }
                } catch (e) {
                    alert(`Failed to save settings: ${e.message}`);
                }
            });
        }

        if (btnTest) {
            btnTest.addEventListener("click", async () => {
                testResults.classList.remove("hidden");
                testResults.innerHTML = "Testing Groq API and local Ollama connections...";
                try {
                    const resp = await fetch("/api/providers/test");
                    const data = await resp.json();
                    testResults.innerHTML = `
                        <div><strong>Groq Status:</strong> ${data.groq.status ? '✓ Connected' : '✗ ' + data.groq.message}</div>
                        <div><strong>Ollama Status:</strong> ${data.ollama.status ? '✓ Connected' : '✗ ' + data.ollama.message}</div>
                    `;
                } catch (e) {
                    testResults.textContent = `Connection test error: ${e.message}`;
                }
            });
        }

        // Cloud consent toggle
        const consentCheckbox = document.getElementById("check-cloud-consent");
        if (consentCheckbox) {
            consentCheckbox.addEventListener("change", (e) => {
                state.cloudConsent = e.target.checked;
            });
        }
    }

    // 13. EXTERNAL SERPAPI RESEARCH
    const btnResearch = document.getElementById("btn-run-research");
    const inputPkg = document.getElementById("input-research-pkg");
    const researchResults = document.getElementById("research-results-container");

    if (btnResearch && inputPkg) {
        btnResearch.addEventListener("click", async () => {
            const pkg = inputPkg.value.trim();
            if (!pkg) return;
            researchResults.innerHTML = "Querying SerpApi for official advisories...";

            try {
                const resp = await fetch(`/api/research/advisories?package=${encodeURIComponent(pkg)}`);
                const data = await resp.json();
                if (!data.available) {
                    researchResults.innerHTML = `<div style="color:var(--text-amber);padding:6px 0;">${data.reason}</div>`;
                    return;
                }
                researchResults.innerHTML = data.results.map(r => `
                    <div style="border-bottom:1px solid var(--border-dim);padding:6px 0;">
                        <a href="${r.link}" target="_blank" rel="noopener" style="color:var(--text-cyan);text-decoration:none;font-weight:700;">${escapeHtml(r.title)}</a>
                        <div style="color:var(--text-muted);font-size:0.7rem;">${escapeHtml(r.snippet)}</div>
                    </div>
                `).join("");
            } catch (e) {
                researchResults.textContent = `Search error: ${e.message}`;
            }
        });
    }

    // 14. ACCESSIBILITY TOGGLES (CRT & REDUCED MOTION)
    const toggleCrtBtn = document.getElementById("toggle-crt-btn");
    const toggleAudioBtn = document.getElementById("toggle-audio-btn");
    const audioIcon = document.getElementById("audio-icon-text");

    if (toggleCrtBtn) {
        toggleCrtBtn.addEventListener("click", () => {
            state.crtEnabled = !state.crtEnabled;
            document.documentElement.setAttribute("data-crt", state.crtEnabled ? "true" : "false");
            toggleCrtBtn.style.color = state.crtEnabled ? "var(--text-phosphor)" : "var(--text-muted)";
        });
    }

    if (toggleAudioBtn) {
        toggleAudioBtn.addEventListener("click", () => {
            state.audioEnabled = !state.audioEnabled;
            if (audioIcon) audioIcon.textContent = state.audioEnabled ? "🔊" : "🔇";
            if (state.audioEnabled) playTerminalTone(660, "sine", 0.1);
        });
    }

    // Check system prefers-reduced-motion
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        state.reducedMotion = true;
        document.documentElement.setAttribute("data-reduced-motion", "true");
        const pill = document.getElementById("motion-mode-pill");
        if (pill) pill.textContent = "REDUCED MOTION: ON";
    }

    // Clock
    setInterval(() => {
        const clock = document.getElementById("footer-clock");
        if (clock) clock.textContent = new Date().toUTCString().slice(17, 25) + " UTC";
    }, 1000);

    // Initial system status probe
    async function probeSystemStatus() {
        try {
            const resp = await fetch("/api/config");
            const data = await resp.json();
            const teleGroq = document.getElementById("tele-groq-status");
            const teleOllama = document.getElementById("tele-ollama-status");
            if (teleGroq) teleGroq.textContent = data.groq_configured ? "Ready (Key Configured)" : "Unconfigured (Set GROQ_API_KEY)";
            if (teleOllama) teleOllama.textContent = `${data.ollama_model} (${data.ollama_base_url})`;
        } catch (e) {
            console.debug("Config probe failed:", e);
        }
    }

    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Boot Everything
    initBootSequence();
    initParticleCanvas();
    initTabs();
    initIngestion();
    initSettings();
    probeSystemStatus();
});
