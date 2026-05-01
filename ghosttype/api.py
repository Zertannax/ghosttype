"""FastAPI application powering `ghosttype serve`.

Local-first design: serves an embedded HTML/CSS/JS bundle at /, exposes the
analysis pipeline at /api/*, and never makes outbound calls. Drop a file or
paste text in the browser; everything runs on the loopback interface.
"""

from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ghosttype import __version__
from ghosttype.pipeline import analyze_text, result_to_dict


WEB_DIR = Path(__file__).parent / "web"


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")


def _markdown_for_result(label: str, payload: dict) -> str:
    """Format a single analysis result as a Markdown report (matches CLI --format md)."""
    lines: list[str] = []
    lines.append(f"# GhostType report — `{label}`")
    lines.append("")
    lines.append(f"**Score:** {payload['score']}/100  ")
    lines.append(f"**Label:** {payload['label']}  ")
    lines.append(f"**Hits:** {payload['total_hits']}  ")
    lines.append(f"**Passages:** {len(payload['passages'])}")
    lines.append("")

    for pr in payload["passages"]:
        if not pr["hits"]:
            continue
        flags = []
        if pr.get("cluster_bonus_applied"):
            flags.append("cluster bonus ×1.15")
        if pr.get("bz05_rule_applied"):
            flags.append("BZ-05 floor → 70")
        flag_str = f"  _({', '.join(flags)})_" if flags else ""

        lines.append(f"## Passage #{pr['index'] + 1} — {pr['score']}/100{flag_str}")
        lines.append("")
        lines.append("| Pattern | Category | Severity | Match |")
        lines.append("|---|---|---:|---|")
        for hit in pr["hits"]:
            snippet = hit["matched_text"].replace("|", "\\|").strip()
            if len(snippet) > 60:
                snippet = snippet[:57] + "..."
            lines.append(
                f"| {hit['pattern_id']} | {hit['category']} | "
                f"{hit['severity']:.1f} | {snippet} |"
            )
        lines.append("")
    return "\n".join(lines)


def create_app() -> FastAPI:
    app = FastAPI(
        title="GhostType",
        description="AI slop detector",
        version=__version__,
    )

    # Static assets (CSS, JS) — only mount if the directory exists so tests can
    # run without the /web/ folder present yet.
    if (WEB_DIR / "style.css").exists():
        app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def root() -> HTMLResponse:
        index = WEB_DIR / "index.html"
        if not index.exists():
            return HTMLResponse(
                "<h1>GhostType API</h1><p>Web UI not bundled. POST text to /api/analyze.</p>",
                status_code=200,
            )
        return HTMLResponse(index.read_text(encoding="utf-8"))

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "version": __version__}

    @app.post("/api/analyze")
    async def analyze(request: AnalyzeRequest) -> dict:
        result = analyze_text(request.text)
        if result is None:
            raise HTTPException(status_code=422, detail="Empty input")
        return result_to_dict(result)

    @app.post("/api/analyze-file")
    async def analyze_file(file: UploadFile = File(...)) -> dict:
        raw = await file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File is not valid UTF-8") from None
        result = analyze_text(text)
        if result is None:
            raise HTTPException(status_code=422, detail="Empty input")
        payload = result_to_dict(result)
        payload["filename"] = file.filename
        return payload

    @app.post("/api/analyze.md", response_class=PlainTextResponse)
    async def analyze_md(request: AnalyzeRequest) -> str:
        result = analyze_text(request.text)
        if result is None:
            raise HTTPException(status_code=422, detail="Empty input")
        payload = result_to_dict(result)
        return _markdown_for_result(label="(pasted text)", payload=payload)

    @app.get("/favicon.ico", response_model=None)
    async def favicon():  # type: ignore[no-untyped-def]
        # Prefer the PNG logo; fall back to the SVG emoji if logo isn't bundled.
        png = WEB_DIR / "logo.png"
        if png.exists():
            return FileResponse(str(png), media_type="image/png")
        svg = WEB_DIR / "favicon.svg"
        if svg.exists():
            return FileResponse(str(svg), media_type="image/svg+xml")
        return PlainTextResponse("", status_code=204)

    return app


def serve(host: str = "127.0.0.1", port: int = 8080, reload: bool = False) -> None:
    """Boot the FastAPI app with uvicorn."""
    try:
        import uvicorn
    except ImportError as e:
        raise ImportError(
            "Web extras not installed. Run: poetry install --with web "
            "(or pip install fastapi uvicorn python-multipart)"
        ) from e

    uvicorn.run(
        "ghosttype.api:create_app" if reload else create_app(),
        host=host,
        port=port,
        reload=reload,
        factory=reload,
        log_level="info",
    )
