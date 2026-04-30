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
    """Test analyze with empty input."""
    result = runner.invoke(app, ["analyze", "-"], input="")
    assert result.exit_code == 0
    assert "Empty" in result.output or "Warning" in result.output


def test_cli_analyze_clean_text() -> None:
    """Test analyze with clean text."""
    result = runner.invoke(app, ["analyze", "-"], input="The cat sat on the mat.")
    assert result.exit_code == 0
    assert "GhostType" in result.output


def test_cli_analyze_slop_text() -> None:
    """Test analyze with slop text."""
    text = "In today's world, we must leverage synergy."
    result = runner.invoke(app, ["analyze", "-"], input=text)
    assert result.exit_code in [0, 1, 2]
    assert "GhostType" in result.output


def test_cli_analyze_json() -> None:
    """Test analyze with JSON output."""
    text = "In today's world, we must leverage synergy."
    result = runner.invoke(app, ["analyze", "-", "--json"], input=text)
    assert result.exit_code in [0, 1, 2]
    # Verify JSON is valid
    data = json.loads(result.output)
    assert "score" in data
    assert "label" in data
    assert "passages" in data


def test_cli_analyze_file() -> None:
    """Test analyze with file input."""
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("In today's world, we must leverage synergy.\n")
        temp_path = Path(f.name)

    try:
        result = runner.invoke(app, ["analyze", str(temp_path)])
        assert result.exit_code in [0, 1, 2]
        assert "GhostType" in result.output
    finally:
        temp_path.unlink()
