"""GhostType CLI."""

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import preprocess
from ghosttype.scorer import AnalysisResult, aggregate

app = typer.Typer(
    name="GhostType",
    help="Detect AI-generated slop in any text. Score it. Rewrite it.",
    no_args_is_help=True,
)
console = Console()


def _read_input(file: Path) -> str:
    """Read text from file or stdin."""
    if str(file) == "-":
        return sys.stdin.read()
    return file.read_text(encoding="utf-8")


def _get_score_style(score: int) -> str:
    """Get rich style for score display."""
    if score <= 20:
        return "bold green"
    if score <= 40:
        return "yellow"
    if score <= 60:
        return "dark_orange"
    if score <= 80:
        return "red"
    return "bold red reverse"


def _render_rich_output(result: AnalysisResult) -> None:
    """Render analysis result with rich formatting."""
    # Header
    console.print()
    console.print("â”" * 50)
    console.print("  [bold]GhostType[/bold] â€” AI Slop Detector v0.1.0")
    console.print("â”" * 50)
    console.print()

    # Score display
    score_style = _get_score_style(result.score)
    score_bar = "â–ˆ" * (result.score // 10) + "â–‘" * (10 - result.score // 10)

    console.print(f"  Slop Score : [{score_style}]{result.score}/100[/{score_style}]  {score_bar}  {result.label.upper()}")
    console.print(f"  Patterns   : {result.total_hits} detected")
    console.print(f"  Passages   : {len(result.passages)} analyzed")
    console.print()

    # Flagged passages table
    if result.total_hits > 0:
        table = Table(title="Flagged Passages", show_header=True, header_style="bold magenta")
        table.add_column("Passage", style="dim", width=4)
        table.add_column("Text", width=50, no_wrap=False)
        table.add_column("Score", width=6)
        table.add_column("Hits", width=4)

        for pr in result.passages:
            if pr.hits:
                text_preview = pr.passage.text[:80] + "..." if len(pr.passage.text) > 80 else pr.passage.text
                score_style = _get_score_style(pr.score)
                table.add_row(
                    str(pr.passage.index + 1),
                    text_preview,
                    f"[{score_style}]{pr.score}[/{score_style}]",
                    str(len(pr.hits)),
                )

        console.print(table)
        console.print()

        # Pattern details
        hits_table = Table(title="Pattern Details", show_header=True, header_style="bold cyan")
        hits_table.add_column("Pattern", width=8)
        hits_table.add_column("Category", width=12)
        hits_table.add_column("Matched Text", width=40)
        hits_table.add_column("Severity", width=8)

        for pr in result.passages:
            for hit in pr.hits:
                hits_table.add_row(
                    hit.pattern_id,
                    hit.category,
                    hit.matched_text[:37] + "..." if len(hit.matched_text) > 40 else hit.matched_text,
                    f"{hit.severity:.1f}",
                )

        console.print(hits_table)
        console.print()
    else:
        console.print("[green]âœ“[/green] No AI slop patterns detected. Text looks clean!")
        console.print()

    console.print("â”" * 50)
    console.print()


def _render_json_output(result: AnalysisResult) -> None:
    """Render analysis result as JSON."""
    output = {
        "score": result.score,
        "label": result.label,
        "total_hits": result.total_hits,
        "passages": [
            {
                "index": pr.passage.index,
                "text": pr.passage.text,
                "score": pr.score,
                "label": pr.label,
                "hits": [
                    {
                        "pattern_id": hit.pattern_id,
                        "category": hit.category,
                        "matched_text": hit.matched_text,
                        "severity": hit.severity,
                    }
                    for hit in pr.hits
                ],
            }
            for pr in result.passages
        ],
    }
    console.print(json.dumps(output, indent=2))


_file_arg = typer.Argument(..., help="Text file to analyze (use - for stdin)")
_json_opt = typer.Option(False, "--json", help="Output JSON instead of rich text")

@app.command()
def analyze(
    file: Path = _file_arg,
    json_output: bool = _json_opt,
) -> None:
    """Analyze a text file for AI slop patterns."""
    try:
        text = _read_input(file)
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        raise typer.Exit(code=1) from e

    if not text.strip():
        console.print("[yellow]Warning: Empty input[/yellow]")
        raise typer.Exit(code=0)

    # Pipeline
    passages = preprocess(text)
    engine = HeuristicEngine()
    hits_by_passage = engine.analyze(passages)
    result = aggregate(passages, hits_by_passage)

    # Output
    if json_output:
        _render_json_output(result)
    else:
        _render_rich_output(result)

    # Exit code based on score
    raise typer.Exit(code=result.exit_code)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("GhostType v0.1.0")


if __name__ == "__main__":
    app()
