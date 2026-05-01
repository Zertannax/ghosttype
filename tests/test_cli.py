"""Tests for GhostType CLI."""

import json

from typer.testing import CliRunner

from ghosttype.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "GhostType" in result.output


def test_cli_analyze_empty() -> None:
    """Empty input warns and exits clean."""
    result = runner.invoke(app, ["analyze", "-"], input="")
    assert result.exit_code == 0
    assert "Empty" in result.output


def test_cli_analyze_clean_text() -> None:
    """Plain neutral sentence stays in non-HIGH territory."""
    result = runner.invoke(app, ["analyze", "-"], input="The cat sat on the mat.")
    assert result.exit_code in [0, 1]
    assert "GhostType" in result.output


def test_cli_analyze_slop_text() -> None:
    """Obvious slop (opener + buzzwords) must trip exit code 2 (HIGH)."""
    text = "In today's world, we must leverage synergy."
    result = runner.invoke(app, ["analyze", "-"], input=text)
    assert result.exit_code == 2, f"Expected HIGH exit, got {result.exit_code}"
    assert "GhostType" in result.output


def test_cli_analyze_json() -> None:
    """JSON output is parseable and contains a score in slop territory."""
    text = "In today's world, we must leverage synergy."
    result = runner.invoke(app, ["analyze", "-", "--json"], input=text)
    assert result.exit_code == 2
    data = json.loads(result.output)
    assert isinstance(data["score"], int)
    assert data["score"] >= 50, f"Score {data['score']} too low for known slop"
    assert data["label"] in ("High", "Critical")
    assert len(data["passages"]) >= 1
    assert data["total_hits"] >= 2


def test_cli_analyze_file() -> None:
    """File input pipeline matches stdin pipeline output."""
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("In today's world, we must leverage synergy.\n")
        temp_path = Path(f.name)

    try:
        result = runner.invoke(app, ["analyze", str(temp_path)])
        assert result.exit_code == 2
        assert "GhostType" in result.output
    finally:
        try:
            temp_path.unlink()
        except (PermissionError, FileNotFoundError):
            pass


def test_cli_analyze_missing_file() -> None:
    """Missing file produces a non-zero exit and a readable error."""
    result = runner.invoke(app, ["analyze", "/nonexistent/path/that/does/not/exist.txt"])
    assert result.exit_code != 0
    assert "Error" in result.output or "error" in result.output
