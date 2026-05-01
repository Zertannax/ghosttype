"""Tests for the FastAPI web layer."""

import json

import pytest
from fastapi.testclient import TestClient

import ghosttype.semantic as semantic
from ghosttype.api import create_app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """TestClient with offline (keyword fallback) semantic for deterministic tests."""
    monkeypatch.setattr(semantic, "FASTEMBED_AVAILABLE", False)
    semantic._model_cache = None
    semantic._corpus_cache = {}
    return TestClient(create_app())


# ---------- health ----------

def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    payload = r.json()
    assert payload["status"] == "ok"
    assert "version" in payload


# ---------- index page ----------

def test_root_serves_html_when_bundled(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    body = r.text
    # Either the real bundled UI or the fallback notice — both are acceptable.
    assert "GhostType" in body


def test_static_css_served(client: TestClient) -> None:
    r = client.get("/static/style.css")
    assert r.status_code == 200
    assert "text/css" in r.headers["content-type"]
    assert "--bg" in r.text  # signature of our pure-black theme


def test_static_js_served(client: TestClient) -> None:
    r = client.get("/static/app.js")
    assert r.status_code == 200
    assert "javascript" in r.headers["content-type"].lower()
    assert "runAnalyze" in r.text


# ---------- /api/analyze ----------

def test_analyze_clean_text(client: TestClient) -> None:
    r = client.post("/api/analyze", json={"text": "The cat sat on the mat. It was warm."})
    assert r.status_code == 200
    data = r.json()
    assert "score" in data
    assert "label" in data
    assert "passages" in data
    assert "breakdown" in data
    assert 0 <= data["score"] <= 100


def test_analyze_slop_text_scores_high(client: TestClient) -> None:
    text = (
        "In today's rapidly evolving landscape, organizations must leverage "
        "transformative methodologies. Furthermore, the integration of "
        "holistic frameworks enables stakeholders."
    )
    r = client.post("/api/analyze", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert data["score"] >= 50
    assert data["label"] in ("Moderate", "High", "Critical")
    assert data["total_hits"] >= 3


def test_analyze_includes_breakdown_with_weights(client: TestClient) -> None:
    r = client.post("/api/analyze", json={"text": "Plain enough text to analyze for scoring."})
    data = r.json()
    bd = data["breakdown"]
    assert "weights" in bd
    assert {"heuristic", "semantic", "stylistic"} <= bd["weights"].keys()
    weight_sum = sum(bd["weights"].values())
    assert abs(weight_sum - 1.0) < 0.01


def test_analyze_empty_input_rejected(client: TestClient) -> None:
    r = client.post("/api/analyze", json={"text": "   \n  "})
    assert r.status_code == 422
    assert "Empty" in r.json()["detail"]


def test_analyze_missing_text_field(client: TestClient) -> None:
    r = client.post("/api/analyze", json={})
    assert r.status_code == 422


# ---------- /api/analyze-file ----------

def test_analyze_file_upload(client: TestClient) -> None:
    text = "In today's world, we leverage synergy and innovation."
    r = client.post(
        "/api/analyze-file",
        files={"file": ("essay.txt", text.encode("utf-8"), "text/plain")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["filename"] == "essay.txt"
    assert data["score"] > 0


def test_analyze_file_non_utf8_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/analyze-file",
        files={"file": ("bad.bin", b"\xff\xfe\x00invalid", "application/octet-stream")},
    )
    assert r.status_code == 400
    assert "UTF-8" in r.json()["detail"]


def test_analyze_file_empty_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/analyze-file",
        files={"file": ("empty.txt", b"   \n  ", "text/plain")},
    )
    assert r.status_code == 422


# ---------- /api/analyze.md ----------

def test_analyze_md_returns_markdown(client: TestClient) -> None:
    r = client.post("/api/analyze.md", json={"text": "In today's world, we leverage synergy."})
    assert r.status_code == 200
    assert "text/plain" in r.headers["content-type"]
    body = r.text
    assert body.startswith("# GhostType report")
    assert "**Score:**" in body


def test_analyze_md_empty_rejected(client: TestClient) -> None:
    r = client.post("/api/analyze.md", json={"text": ""})
    assert r.status_code == 422


# ---------- favicon ----------

def test_favicon_served(client: TestClient) -> None:
    r = client.get("/favicon.ico")
    # Either the SVG file or the empty 204 — both are acceptable.
    assert r.status_code in (200, 204)
