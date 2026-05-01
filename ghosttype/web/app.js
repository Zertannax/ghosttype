/* GhostType web client.
   Vanilla JS, no build step, no external deps. Stays on localhost. */

(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);

  const dropzone = $("#dropzone");
  const fileInput = $("#file-input");
  const textInput = $("#text-input");
  const analyzeBtn = $("#analyze-btn");
  const clearBtn = $("#clear-btn");
  const errorMsg = $("#error-msg");
  const resultPanel = $("#result-panel");
  const scoreNum = $("#score-num");
  const scoreLabel = $("#score-label");
  const scoreBarFill = $("#score-bar-fill");
  const statHits = $("#stat-hits");
  const statPassages = $("#stat-passages");
  const statFlags = $("#stat-flags");
  const breakdown = $("#breakdown");
  const passages = $("#passages");
  const downloadMd = $("#download-md");
  const versionEl = $("#version");

  let lastResult = null;
  let lastText = null;

  // ==== utilities ====

  const SCORE_COLORS = [
    { max: 20,  cssVar: "--clean",     label: "CLEAN",    glow: "rgba(16, 185, 129, 0.4)" },
    { max: 40,  cssVar: "--mild",      label: "MILD",     glow: "rgba(234, 179, 8, 0.4)" },
    { max: 60,  cssVar: "--moderate",  label: "MODERATE", glow: "rgba(249, 115, 22, 0.4)" },
    { max: 80,  cssVar: "--high",      label: "HIGH",     glow: "rgba(239, 68, 68, 0.4)" },
    { max: 100, cssVar: "--critical",  label: "CRITICAL", glow: "rgba(220, 38, 38, 0.5)" },
  ];

  const colorFor = (score) => {
    for (const tier of SCORE_COLORS) {
      if (score <= tier.max) return tier;
    }
    return SCORE_COLORS[SCORE_COLORS.length - 1];
  };

  const showError = (msg) => {
    errorMsg.textContent = msg;
    setTimeout(() => { if (errorMsg.textContent === msg) errorMsg.textContent = ""; }, 5000);
  };

  const clearError = () => { errorMsg.textContent = ""; };

  const easeOutQuad = (t) => 1 - (1 - t) * (1 - t);

  const animateNumber = (el, from, to, duration = 800) => {
    const start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / duration);
      const v = from + (to - from) * easeOutQuad(t);
      el.textContent = Math.round(v);
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  // ==== version ====

  fetch("/api/health")
    .then((r) => r.json())
    .then((d) => { if (versionEl) versionEl.textContent = d.version; })
    .catch(() => { if (versionEl) versionEl.textContent = "?"; });

  // ==== drag-drop ====

  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    })
  );

  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      if (evt === "dragleave" && e.target !== dropzone) return;
      dropzone.classList.remove("dragover");
    })
  );

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;
    dropzone.classList.add("dropped");
    setTimeout(() => dropzone.classList.remove("dropped"), 400);
    handleFile(file);
  });

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
  });

  const handleFile = (file) => {
    if (file.size > 5 * 1024 * 1024) {
      showError("File too large (max 5 MB).");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      textInput.value = reader.result;
      runAnalyze();
    };
    reader.onerror = () => showError("Could not read file.");
    reader.readAsText(file);
  };

  // ==== analyze ====

  analyzeBtn.addEventListener("click", runAnalyze);
  clearBtn.addEventListener("click", () => {
    textInput.value = "";
    resultPanel.classList.add("hidden");
    clearError();
    textInput.focus();
  });

  textInput.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      runAnalyze();
    }
  });

  async function runAnalyze() {
    const text = textInput.value;
    if (!text.trim()) {
      showError("Please paste some text or drop a file first.");
      return;
    }
    clearError();
    analyzeBtn.classList.add("loading");
    analyzeBtn.disabled = true;
    try {
      const r = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!r.ok) {
        const { detail } = await r.json().catch(() => ({}));
        throw new Error(detail || `HTTP ${r.status}`);
      }
      const data = await r.json();
      lastResult = data;
      lastText = text;
      renderResult(data);
    } catch (err) {
      showError(err.message || "Analysis failed.");
    } finally {
      analyzeBtn.classList.remove("loading");
      analyzeBtn.disabled = false;
    }
  }

  // ==== render ====

  function renderResult(data) {
    const tier = colorFor(data.score);
    const root = document.documentElement;
    const colorVar = `var(${tier.cssVar})`;
    const colorBright = colorVar; // single-tone for now; could add gradient later

    document.querySelector(".score-block").style.setProperty("--score-color", colorVar);
    document.querySelector(".score-block").style.setProperty("--score-glow", tier.glow);
    scoreLabel.style.color = colorVar;
    scoreBarFill.style.setProperty("--score-color", colorVar);
    scoreBarFill.style.setProperty("--score-color-bright", colorBright);
    scoreBarFill.style.setProperty("--score-glow", tier.glow);

    resultPanel.classList.remove("hidden");
    animateNumber(scoreNum, 0, data.score);
    scoreLabel.textContent = data.label.toUpperCase();
    statHits.textContent = `${data.total_hits} pattern${data.total_hits === 1 ? "" : "s"}`;
    statPassages.textContent = `${data.passages.length} passage${data.passages.length === 1 ? "" : "s"}`;

    // Score bar — start at 0 then animate via reflow
    scoreBarFill.style.width = "0%";
    requestAnimationFrame(() => {
      scoreBarFill.style.width = `${data.score}%`;
    });

    // Cluster / BZ-05 flags
    const clusterCount = data.passages.filter((p) => p.cluster_bonus_applied).length;
    const bz05Count = data.passages.filter((p) => p.bz05_rule_applied).length;
    const flags = [];
    if (clusterCount > 0) flags.push(`<span class="flag-pill cluster">${clusterCount}× cluster bonus</span>`);
    if (bz05Count > 0) flags.push(`<span class="flag-pill bz05">${bz05Count}× BZ-05 floor</span>`);
    statFlags.innerHTML = flags.join("");

    renderBreakdown(data.breakdown);
    renderPassages(data.passages);

    resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderBreakdown(b) {
    if (!b) {
      breakdown.innerHTML = "";
      return;
    }
    const items = [
      {
        label: "Heuristic",
        value: b.heuristic_doc_score.toFixed(0),
        detail: `weight ${b.weights.heuristic.toFixed(2)}`,
      },
      {
        label: "Semantic",
        value: b.semantic_score == null ? "—" : (b.semantic_score * 100).toFixed(0),
        detail: `weight ${b.weights.semantic.toFixed(2)}`,
      },
      {
        label: "Stylistic",
        value: b.stylistic_score == null ? "—" : (b.stylistic_score * 100).toFixed(0),
        detail: `weight ${b.weights.stylistic.toFixed(2)}`,
      },
      {
        label: "Human bonus",
        value: b.human_bonus >= 0 ? `+${b.human_bonus}` : `${b.human_bonus}`,
        detail: `${b.human_indicators} indicators`,
      },
    ];
    breakdown.innerHTML = items.map((it) => `
      <div class="breakdown-item">
        <div class="breakdown-label">${it.label}</div>
        <div class="breakdown-value">${it.value}</div>
        <div class="breakdown-detail">${it.detail}</div>
      </div>
    `).join("");
  }

  function renderPassages(passageList) {
    if (!passageList || passageList.length === 0) {
      passages.innerHTML = "";
      return;
    }
    const flagged = passageList.filter((p) => p.score > 60 || p.cluster_bonus_applied || p.bz05_rule_applied).length;

    let html = `
      <div class="passages-header">
        <div class="passages-title">Passages</div>
        <button id="expand-all" class="expand-toggle">Expand all</button>
      </div>
    `;

    html += passageList.map((p, idx) => {
      const tier = colorFor(p.score);
      const open = (p.score > 60 || p.cluster_bonus_applied || p.bz05_rule_applied) ? "open" : "";
      const preview = p.text.length > 90 ? p.text.slice(0, 90) + "…" : p.text;
      const flagBits = [];
      if (p.cluster_bonus_applied) flagBits.push(`<span class="flag-pill cluster">cluster</span>`);
      if (p.bz05_rule_applied) flagBits.push(`<span class="flag-pill bz05">BZ-05</span>`);

      const hits = p.hits.map((h) => {
        const cls = h.severity < 0 ? "negative" : h.severity >= 0.7 ? "high" : "";
        const sevStr = h.severity >= 0 ? `+${h.severity.toFixed(1)}` : h.severity.toFixed(1);
        return `
          <div class="hit">
            <span class="hit-id">${h.pattern_id}</span>
            <span class="hit-cat">${h.category}</span>
            <span class="hit-match">${escapeHtml(h.matched_text)}</span>
            <span class="hit-sev ${cls}">${sevStr}</span>
          </div>
        `;
      }).join("");

      return `
        <details class="passage" ${open} style="animation-delay: ${idx * 60}ms">
          <summary class="passage-summary">
            <div class="passage-meta">
              <span class="passage-num">#${p.index + 1}</span>
              <span class="passage-score" style="color: var(${tier.cssVar})">${p.score}</span>
              <span class="passage-preview">${escapeHtml(preview)}</span>
              ${flagBits.join("")}
            </div>
            <span class="passage-chevron">›</span>
          </summary>
          <div class="passage-body">
            <div class="passage-text">${escapeHtml(p.text)}</div>
            <div class="hits-list">${hits || '<div class="dim" style="font-size: 0.85rem; padding: 8px 12px;">No patterns flagged in this passage.</div>'}</div>
          </div>
        </details>
      `;
    }).join("");

    passages.innerHTML = html;

    const expandBtn = $("#expand-all");
    if (expandBtn) {
      expandBtn.addEventListener("click", () => {
        const all = passages.querySelectorAll("details");
        const allOpen = Array.from(all).every((d) => d.open);
        all.forEach((d) => { d.open = !allOpen; });
        expandBtn.textContent = allOpen ? "Expand all" : "Collapse all";
      });
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  // ==== download .md ====

  downloadMd.addEventListener("click", async () => {
    if (!lastText) return;
    try {
      const r = await fetch("/api/analyze.md", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: lastText }),
      });
      if (!r.ok) throw new Error("Could not generate markdown.");
      const md = await r.text();
      const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ghosttype-report-${Date.now()}.md`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      showError(err.message);
    }
  });
})();
