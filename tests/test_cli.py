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
    assert "not found" in result.output.lower() or "error" in result.output.lower()


# ---------- batch / glob / directory ----------


def test_cli_analyze_directory(tmp_path) -> None:
    """A directory analyzes all matching files and prints a summary table."""
    (tmp_path / "clean.txt").write_text("The cat sat on the mat. It was warm.", encoding="utf-8")
    (tmp_path / "slop.txt").write_text(
        "In today's rapidly evolving landscape, organizations must leverage transformative methodologies. "
        "Furthermore, the integration of holistic frameworks enables stakeholders.",
        encoding="utf-8",
    )
    (tmp_path / "ignored.log").write_text("not analyzed", encoding="utf-8")

    result = runner.invoke(app, ["analyze", str(tmp_path)])
    assert result.exit_code == 2, f"Expected exit 2 (max of children), got {result.exit_code}"
    assert "clean.txt" in result.output
    assert "slop.txt" in result.output
    # .log file not in default extensions → not listed
    assert "ignored.log" not in result.output


def test_cli_analyze_directory_recursive(tmp_path) -> None:
    """--recursive picks up files in subdirectories."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "nested.txt").write_text("Plain neutral text here.", encoding="utf-8")
    (tmp_path / "top.txt").write_text("Plain neutral text on top.", encoding="utf-8")

    flat = runner.invoke(app, ["analyze", str(tmp_path)])
    rec = runner.invoke(app, ["analyze", str(tmp_path), "--recursive"])

    assert "nested.txt" not in flat.output
    assert "nested.txt" in rec.output
    assert "top.txt" in rec.output


def test_cli_analyze_directory_custom_ext(tmp_path) -> None:
    """--ext overrides the default txt/md extensions."""
    (tmp_path / "kept_a.rst").write_text("Plain prose one.", encoding="utf-8")
    (tmp_path / "kept_b.rst").write_text("Plain prose two.", encoding="utf-8")
    (tmp_path / "skipped.txt").write_text("Other prose.", encoding="utf-8")

    result = runner.invoke(app, ["analyze", str(tmp_path), "--ext", "rst"])
    assert "kept_a.rst" in result.output
    assert "kept_b.rst" in result.output
    assert "skipped.txt" not in result.output


def test_cli_analyze_glob_pattern(tmp_path, monkeypatch) -> None:
    """A glob pattern fans out to matching files."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("Plain text one.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Plain text two.", encoding="utf-8")
    (tmp_path / "c.md").write_text("Markdown text.", encoding="utf-8")

    result = runner.invoke(app, ["analyze", "*.txt"])
    assert "a.txt" in result.output
    assert "b.txt" in result.output
    assert "c.md" not in result.output


def test_cli_analyze_directory_json(tmp_path) -> None:
    """--json on a directory emits a JSON array of per-file results."""
    (tmp_path / "one.txt").write_text("In today's world, we leverage synergy.", encoding="utf-8")
    (tmp_path / "two.txt").write_text("Plain text here.", encoding="utf-8")

    result = runner.invoke(app, ["analyze", str(tmp_path), "--json"])
    assert result.exit_code in (0, 1, 2)
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 2
    for entry in data:
        assert "path" in entry
        assert "result" in entry
        assert entry["result"] is None or "score" in entry["result"]


def test_cli_analyze_empty_directory(tmp_path) -> None:
    """Directory with no matching files yields a clear error and exit 1."""
    result = runner.invoke(app, ["analyze", str(tmp_path)])
    assert result.exit_code == 1
    assert "no files matched" in result.output.lower()


# ---------- output format flag ----------


def test_cli_format_csv_single_file(tmp_path) -> None:
    """--format csv on a single file emits a parseable CSV row."""
    f = tmp_path / "input.txt"
    f.write_text("In today's world, we leverage synergy.", encoding="utf-8")
    result = runner.invoke(app, ["analyze", str(f), "--format", "csv"])
    assert result.exit_code == 2
    rows = [line for line in result.output.splitlines() if line.strip()]
    assert rows[0].startswith("path,score,label")
    # Parse the data row
    import csv as _csv
    reader = _csv.reader(rows)
    next(reader)  # header
    data_row = next(reader)
    assert data_row[0] == str(f)
    assert int(data_row[1]) >= 50  # score is parseable integer
    assert data_row[2] in ("High", "Critical")


def test_cli_format_csv_batch(tmp_path) -> None:
    """--format csv on a directory emits one CSV row per file."""
    (tmp_path / "a.txt").write_text("Plain text one.", encoding="utf-8")
    (tmp_path / "b.txt").write_text("Plain text two.", encoding="utf-8")
    result = runner.invoke(app, ["analyze", str(tmp_path), "--format", "csv"])
    rows = [line for line in result.output.splitlines() if line.strip()]
    assert rows[0].startswith("path,")
    # 2 files = 2 data rows + 1 header
    assert len(rows) == 3


def test_cli_format_md_single_file(tmp_path) -> None:
    """--format md emits a Markdown report with summary table."""
    f = tmp_path / "input.txt"
    f.write_text("In today's world, we leverage synergy and innovation.", encoding="utf-8")
    result = runner.invoke(app, ["analyze", str(f), "--format", "md"])
    assert "# GhostType report" in result.output
    assert "| File | Score |" in result.output
    assert str(f) in result.output


def test_cli_format_md_batch_includes_pattern_details(tmp_path) -> None:
    """Markdown batch report lists per-file pattern details for files with hits."""
    (tmp_path / "slop.txt").write_text(
        "In today's evolving landscape, we must leverage synergy and transformative paradigms.",
        encoding="utf-8",
    )
    (tmp_path / "clean.txt").write_text("Plain text.", encoding="utf-8")
    result = runner.invoke(app, ["analyze", str(tmp_path), "--format", "md"])
    assert "# GhostType report (2 files)" in result.output
    # Per-file detail section for the slop file
    assert "## " in result.output  # at least one h2
    assert "| Pattern | Category | Severity | Match |" in result.output


def test_cli_format_invalid_rejected() -> None:
    """An unknown --format value exits non-zero with a clear error."""
    result = runner.invoke(app, ["analyze", "-", "--format", "yaml"], input="text")
    assert result.exit_code != 0
    assert "unknown format" in result.output.lower()


def test_cli_json_flag_still_works_as_alias(tmp_path) -> None:
    """The legacy --json flag stays equivalent to --format json."""
    f = tmp_path / "x.txt"
    f.write_text("In today's world, we leverage synergy.", encoding="utf-8")
    result = runner.invoke(app, ["analyze", str(f), "--json"])
    data = json.loads(result.output)
    assert "score" in data
    assert "passages" in data
