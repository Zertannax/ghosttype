"""GhostType CLI."""

import csv
import glob as _glob
import io
import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from ghosttype import __version__
from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import preprocess
from ghosttype.scorer import AnalysisResult, aggregate
from ghosttype.semantic import semantic_score_passages
from ghosttype.stylistic import stylistic_score_passages

app = typer.Typer(
    name="GhostType",
    help="Detect AI-generated slop in any text. Score it. Rewrite it.",
    no_args_is_help=True,
)
console = Console()

DEFAULT_EXTENSIONS = (".txt", ".md")
STDIN_TOKEN = "-"
VALID_FORMATS = ("rich", "json", "csv", "md")


# ---------- pipeline ----------

def _read_input(path: Path) -> str:
    """Read text from a file path. Stdin is handled by the caller."""
    return path.read_text(encoding="utf-8")


def _analyze_text(text: str) -> AnalysisResult | None:
    """Run the full pipeline on a text. Returns None for whitespace-only input."""
    if not text.strip():
        return None
    passages = preprocess(text)
    engine = HeuristicEngine()
    hits_by_passage = engine.analyze(passages)
    semantic = semantic_score_passages(passages)
    stylistic = stylistic_score_passages(passages)
    return aggregate(passages, hits_by_passage, semantic, stylistic)


# ---------- path resolution ----------

def _normalize_extensions(raw: str | None) -> tuple[str, ...]:
    """Parse '--ext txt,md' or '--ext .txt,.md' into a tuple of dotted extensions."""
    if not raw:
        return DEFAULT_EXTENSIONS
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    return tuple(p if p.startswith(".") else f".{p}" for p in parts)


def _walk_directory(directory: Path, recursive: bool, exts: tuple[str, ...]) -> list[Path]:
    """List files under a directory matching the given extensions."""
    pattern = "**/*" if recursive else "*"
    return sorted(
        p for p in directory.glob(pattern)
        if p.is_file() and p.suffix.lower() in exts
    )


def _resolve_target(target: str, recursive: bool, exts: tuple[str, ...]) -> list[Path]:
    """Resolve the analyze argument into a list of concrete file paths.

    Stdin is signalled by the special STDIN_TOKEN ("-") and handled separately by
    the caller — this function never returns it. Glob patterns and directories
    fan out to the matching files; a plain file path returns a single-element list.
    """
    if _glob.has_magic(target):
        # Glob pattern: e.g. "*.txt", "essays/**/*.md"
        matches = sorted(Path(p) for p in _glob.glob(target, recursive=recursive))
        return [m for m in matches if m.is_file()]

    path = Path(target)
    if path.is_dir():
        return _walk_directory(path, recursive=recursive, exts=exts)

    # Single file (or non-existent — let the caller surface the error).
    return [path]


# ---------- single-file rendering ----------

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
    """Render single-file analysis result with rich formatting."""
    console.print()
    console.print("=" * 50)
    console.print(f"  [bold]GhostType[/bold] - AI Slop Detector v{__version__}")
    console.print("=" * 50)
    console.print()

    score_style = _get_score_style(result.score)
    score_bar = "█" * (result.score // 10) + "░" * (10 - result.score // 10)

    console.print(f"  Slop Score : [{score_style}]{result.score}/100[/{score_style}]  {score_bar}  {result.label.upper()}")
    console.print(f"  Patterns   : {result.total_hits} detected")
    console.print(f"  Passages   : {len(result.passages)} analyzed")
    console.print()

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
        console.print("[green]✓[/green] No AI slop patterns detected. Text looks clean!")
        console.print()

    console.print("=" * 50)
    console.print()


def _result_to_dict(result: AnalysisResult) -> dict:
    """Convert AnalysisResult to a JSON-serializable dict."""
    return {
        "score": result.score,
        "label": result.label,
        "total_hits": result.total_hits,
        "exit_code": result.exit_code,
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


def _render_json_output(result: AnalysisResult) -> None:
    """Render single-file analysis result as JSON."""
    print(json.dumps(_result_to_dict(result), indent=2))


# ---------- CSV / Markdown rendering ----------

CSV_COLUMNS = ("path", "score", "label", "exit_code", "total_hits", "passages")


def _render_csv_output(results: list[tuple[Path | str, AnalysisResult | None]]) -> None:
    """Print one CSV row per file (or stdin). Empty inputs get blank score columns."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_COLUMNS)
    for path, result in results:
        if result is None:
            writer.writerow([str(path), "", "", "", "", ""])
        else:
            writer.writerow([
                str(path),
                result.score,
                result.label,
                result.exit_code,
                result.total_hits,
                len(result.passages),
            ])
    print(buf.getvalue(), end="")


def _render_md_output(results: list[tuple[Path | str, AnalysisResult | None]]) -> None:
    """Print a Markdown report — summary table at the top, per-file pattern details below."""
    lines: list[str] = []
    lines.append(f"# GhostType report ({len(results)} file{'s' if len(results) != 1 else ''})")
    lines.append("")
    lines.append("| File | Score | Label | Exit | Hits | Passages |")
    lines.append("|---|---:|---|---:|---:|---:|")
    for path, result in results:
        if result is None:
            lines.append(f"| `{path}` | — | _empty_ | — | — | — |")
        else:
            lines.append(
                f"| `{path}` | {result.score} | {result.label} | "
                f"{result.exit_code} | {result.total_hits} | {len(result.passages)} |"
            )
    lines.append("")

    scored = [(p, r) for p, r in results if r is not None]
    if scored:
        avg = sum(r.score for _, r in scored) / len(scored)
        lines.append(f"**Average score:** {avg:.1f}/100")
        lines.append("")

    # Per-file pattern detail (only files with hits).
    for path, result in scored:
        if result.total_hits == 0:
            continue
        lines.append(f"## `{path}` — {result.score}/100 ({result.label})")
        lines.append("")
        lines.append("| Pattern | Category | Severity | Match |")
        lines.append("|---|---|---:|---|")
        for pr in result.passages:
            for hit in pr.hits:
                snippet = hit.matched_text.replace("|", "\\|").strip()
                if len(snippet) > 60:
                    snippet = snippet[:57] + "..."
                lines.append(
                    f"| {hit.pattern_id} | {hit.category} | {hit.severity:.1f} | {snippet} |"
                )
        lines.append("")

    print("\n".join(lines))


# ---------- batch rendering ----------

def _render_batch_summary(results: list[tuple[Path, AnalysisResult | None]]) -> None:
    """Print a summary table for multi-file analysis."""
    console.print()
    console.print("=" * 70)
    console.print(f"  [bold]GhostType[/bold] - AI Slop Detector v{__version__}  ({len(results)} files)")
    console.print("=" * 70)
    console.print()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File", overflow="fold")
    table.add_column("Score", width=6, justify="right")
    table.add_column("Label", width=10)
    table.add_column("Hits", width=5, justify="right")
    table.add_column("Passages", width=8, justify="right")

    scored = [(p, r) for p, r in results if r is not None]
    skipped = [p for p, r in results if r is None]

    for path, result in results:
        if result is None:
            table.add_row(str(path), "—", "[dim]empty[/dim]", "—", "—")
            continue
        style = _get_score_style(result.score)
        table.add_row(
            str(path),
            f"[{style}]{result.score}[/{style}]",
            f"[{style}]{result.label}[/{style}]",
            str(result.total_hits),
            str(len(result.passages)),
        )

    console.print(table)
    console.print()

    if scored:
        avg = sum(r.score for _, r in scored) / len(scored)
        worst = max(scored, key=lambda x: x[1].score)
        cleanest = min(scored, key=lambda x: x[1].score)
        console.print(
            f"  [bold]Average score:[/bold] {avg:.1f}/100  "
            f"[bold]Worst:[/bold] {worst[0]} ({worst[1].score})  "
            f"[bold]Cleanest:[/bold] {cleanest[0]} ({cleanest[1].score})"
        )
    if skipped:
        console.print(f"  [dim]Skipped {len(skipped)} empty file(s).[/dim]")
    console.print()


def _render_batch_json(results: list[tuple[Path, AnalysisResult | None]]) -> None:
    """Print multi-file results as a JSON array."""
    payload = [
        {
            "path": str(path),
            "result": _result_to_dict(r) if r is not None else None,
        }
        for path, r in results
    ]
    print(json.dumps(payload, indent=2))


# ---------- analyze command ----------

_target_arg = typer.Argument(..., help="File, directory, glob pattern, or - for stdin")
_format_opt = typer.Option("rich", "--format", "-f", help="Output format: rich, json, csv, md")
_json_opt = typer.Option(False, "--json", help="Shortcut for --format json")
_recursive_opt = typer.Option(False, "--recursive", "-r", help="Recurse into subdirectories")
_ext_opt = typer.Option(None, "--ext", help="Comma-separated extensions for directory mode (default: txt,md)")


@app.command()
def analyze(
    target: str = _target_arg,
    output_format: str = _format_opt,
    json_output: bool = _json_opt,
    recursive: bool = _recursive_opt,
    ext: str = _ext_opt,
) -> None:
    """Analyze a file, directory, or glob pattern for AI slop patterns.

    Examples:
      ghosttype analyze essay.txt
      ghosttype analyze -                            # stdin
      ghosttype analyze ./essays/                    # directory (.txt + .md)
      ghosttype analyze ./essays/ -r                 # recursive
      ghosttype analyze "drafts/*.md"                # glob
      ghosttype analyze ./essays/ --format csv > report.csv
      ghosttype analyze ./essays/ --format md > report.md
    """
    extensions = _normalize_extensions(ext)
    fmt = _resolve_format(output_format, json_output)

    # Stdin path is always single-source.
    if target == STDIN_TOKEN:
        try:
            text = sys.stdin.read()
        except Exception as e:
            console.print(f"[red]Error reading stdin: {e}[/red]")
            raise typer.Exit(code=1) from e
        result = _analyze_text(text)
        if result is None:
            console.print("[yellow]Warning: Empty input[/yellow]")
            raise typer.Exit(code=0)
        _emit_single(result, fmt, label="-")
        raise typer.Exit(code=result.exit_code)

    paths = _resolve_target(target, recursive=recursive, exts=extensions)
    if not paths:
        console.print(f"[red]No files matched '{target}'.[/red]")
        raise typer.Exit(code=1)

    if len(paths) == 1 and not paths[0].exists():
        console.print(f"[red]Error: file not found: {paths[0]}[/red]")
        raise typer.Exit(code=1)

    # Single-file path keeps the original rich/JSON rendering verbatim.
    if len(paths) == 1 and paths[0].is_file():
        path = paths[0]
        try:
            text = _read_input(path)
        except Exception as e:
            console.print(f"[red]Error reading file {path}: {e}[/red]")
            raise typer.Exit(code=1) from e

        result = _analyze_text(text)
        if result is None:
            console.print(f"[yellow]Warning: {path} is empty.[/yellow]")
            raise typer.Exit(code=0)

        _emit_single(result, fmt, label=str(path))
        raise typer.Exit(code=result.exit_code)

    # Batch path: progress bar (only in rich mode) + chosen formatter.
    results: list[tuple[Path, AnalysisResult | None]] = []
    show_progress = fmt == "rich"

    if show_progress:
        progress_columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ]
        with Progress(*progress_columns, console=console) as progress:
            task_id = progress.add_task("Analyzing", total=len(paths))
            for path in paths:
                results.append((path, _analyze_one_file(path)))
                progress.advance(task_id)
    else:
        results = [(path, _analyze_one_file(path)) for path in paths]

    _emit_batch(results, fmt)

    scored_exits = [r.exit_code for _, r in results if r is not None]
    raise typer.Exit(code=max(scored_exits) if scored_exits else 0)


def _resolve_format(fmt: str, json_flag: bool) -> str:
    """Validate and normalize the output format. --json overrides --format."""
    if json_flag:
        return "json"
    fmt = fmt.lower()
    if fmt not in VALID_FORMATS:
        console.print(
            f"[red]Unknown format '{fmt}'. Valid: {', '.join(VALID_FORMATS)}[/red]"
        )
        raise typer.Exit(code=2)
    return fmt


def _emit_single(result: AnalysisResult, fmt: str, label: str) -> None:
    """Emit a single-file result in the chosen format."""
    if fmt == "json":
        _render_json_output(result)
    elif fmt == "csv":
        _render_csv_output([(label, result)])
    elif fmt == "md":
        _render_md_output([(label, result)])
    else:
        _render_rich_output(result)


def _emit_batch(results: list[tuple[Path, AnalysisResult | None]], fmt: str) -> None:
    """Emit a batch result in the chosen format."""
    if fmt == "json":
        _render_batch_json(results)
    elif fmt == "csv":
        _render_csv_output([(p, r) for p, r in results])
    elif fmt == "md":
        _render_md_output([(p, r) for p, r in results])
    else:
        _render_batch_summary(results)


def _analyze_one_file(path: Path) -> AnalysisResult | None:
    """Read + analyze a single file. Returns None for empty/unreadable files."""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[red]Skipping {path}: {e}[/red]")
        return None
    return _analyze_text(text)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"GhostType v{__version__}")


if __name__ == "__main__":
    app()
