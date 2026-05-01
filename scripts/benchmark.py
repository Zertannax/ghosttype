"""Benchmark GhostType against real AI + human passages.

Usage:
    python scripts/benchmark.py --n 50
    python scripts/benchmark.py --n 100 --threshold 60 --seed 42 --output bench.csv

Loads AI samples from data/datasets/ollama_*/ and human samples from
data/raw/raid_human.jsonl + data/raw/falcon_human.jsonl. Runs each through the
full pipeline and reports precision/recall/F1/accuracy at the given threshold.

Exit code 0 if F1 >= 0.7, else 1 — useful for CI.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path

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

from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import preprocess
from ghosttype.scorer import aggregate
from ghosttype.semantic import semantic_score_passages
from ghosttype.stylistic import stylistic_score_passages

REPO_ROOT = Path(__file__).resolve().parent.parent
AI_GLOB = "data/datasets/ollama_*/*.jsonl"
HUMAN_FILES = ("data/raw/raid_human.jsonl", "data/raw/falcon_human.jsonl")

console = Console()


@dataclass
class Sample:
    label: str  # "ai" or "human"
    source: str
    text: str
    score: int = 0
    predicted_label: str = ""


# ---------- loaders ----------

def _load_jsonl_texts(path: Path) -> list[tuple[str, str]]:
    """Load (text, source_tag) pairs from a JSONL file. Skips entries without 'text'."""
    out: list[tuple[str, str]] = []
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = row.get("text")
            if text and isinstance(text, str) and len(text.split()) >= 30:
                out.append((text, path.name))
    return out


def load_ai_samples() -> list[tuple[str, str]]:
    """Gather all AI-labelled texts under data/datasets/ollama_*/*.jsonl."""
    samples: list[tuple[str, str]] = []
    for path in sorted(REPO_ROOT.glob(AI_GLOB)):
        samples.extend(_load_jsonl_texts(path))
    return samples


def load_human_samples() -> list[tuple[str, str]]:
    """Gather all human-labelled texts under data/raw/."""
    samples: list[tuple[str, str]] = []
    for rel in HUMAN_FILES:
        samples.extend(_load_jsonl_texts(REPO_ROOT / rel))
    return samples


# ---------- pipeline ----------

def score_text(engine: HeuristicEngine, text: str) -> int:
    """Run the full pipeline and return the document score."""
    passages = preprocess(text)
    if not passages:
        return 0
    hits = engine.analyze(passages)
    sem = semantic_score_passages(passages)
    sty = stylistic_score_passages(passages)
    result = aggregate(passages, hits, sem, sty)
    return result.score


# ---------- metrics ----------

@dataclass
class Metrics:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def total(self) -> int:
        return self.tp + self.fp + self.tn + self.fn

    @property
    def accuracy(self) -> float:
        return (self.tp + self.tn) / self.total if self.total else 0.0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0


def compute_metrics(samples: list[Sample], threshold: int) -> Metrics:
    """Confusion matrix at a score threshold (AI predicted when score > threshold)."""
    tp = fp = tn = fn = 0
    for s in samples:
        predicted_ai = s.score > threshold
        actual_ai = s.label == "ai"
        if actual_ai and predicted_ai:
            tp += 1
        elif actual_ai and not predicted_ai:
            fn += 1
        elif not actual_ai and predicted_ai:
            fp += 1
        else:
            tn += 1
    return Metrics(tp=tp, fp=fp, tn=tn, fn=fn)


# ---------- runner ----------

def run_benchmark(n_per_class: int, threshold: int, seed: int) -> tuple[list[Sample], Metrics]:
    rng = random.Random(seed)
    ai_pool = load_ai_samples()
    human_pool = load_human_samples()

    if not ai_pool:
        console.print(f"[red]No AI samples found under {AI_GLOB}[/red]")
        sys.exit(2)
    if not human_pool:
        console.print(f"[red]No human samples found under {HUMAN_FILES}[/red]")
        sys.exit(2)

    n_ai = min(n_per_class, len(ai_pool))
    n_human = min(n_per_class, len(human_pool))
    if n_ai < n_per_class or n_human < n_per_class:
        console.print(
            f"[yellow]Warning: requested {n_per_class}/class, "
            f"got {n_ai} AI and {n_human} human samples.[/yellow]"
        )

    ai_picked = rng.sample(ai_pool, n_ai)
    human_picked = rng.sample(human_pool, n_human)

    samples = (
        [Sample(label="ai", source=src, text=t) for t, src in ai_picked]
        + [Sample(label="human", source=src, text=t) for t, src in human_picked]
    )
    rng.shuffle(samples)

    engine = HeuristicEngine()
    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ]
    with Progress(*columns, console=console) as progress:
        task = progress.add_task("Scoring", total=len(samples))
        for sample in samples:
            sample.score = score_text(engine, sample.text)
            sample.predicted_label = "ai" if sample.score > threshold else "human"
            progress.advance(task)

    return samples, compute_metrics(samples, threshold)


def render_summary(metrics: Metrics, threshold: int, n_per_class: int) -> None:
    table = Table(
        title=f"Benchmark — {n_per_class}/class, threshold > {threshold}",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("True positives  (AI flagged)", str(metrics.tp))
    table.add_row("False positives (human flagged)", str(metrics.fp))
    table.add_row("True negatives  (human cleared)", str(metrics.tn))
    table.add_row("False negatives (AI missed)", str(metrics.fn))
    table.add_row("[bold]Precision[/bold]", f"{metrics.precision:.3f}")
    table.add_row("[bold]Recall[/bold]", f"{metrics.recall:.3f}")
    table.add_row("[bold]F1[/bold]", f"{metrics.f1:.3f}")
    table.add_row("[bold]Accuracy[/bold]", f"{metrics.accuracy:.3f}")
    console.print(table)


def write_csv(samples: list[Sample], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "predicted", "score", "source", "text_preview"])
        for s in samples:
            preview = s.text[:120].replace("\n", " ")
            writer.writerow([s.label, s.predicted_label, s.score, s.source, preview])


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark GhostType classifier.")
    parser.add_argument("--n", type=int, default=50, help="Samples per class (default 50)")
    parser.add_argument("--threshold", type=int, default=50, help="Score > threshold = AI (default 50)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default 42)")
    parser.add_argument("--output", type=Path, help="Optional CSV output path")
    parser.add_argument("--min-f1", type=float, default=0.7, help="Exit 1 if F1 < this (default 0.7)")
    args = parser.parse_args()

    samples, metrics = run_benchmark(args.n, args.threshold, args.seed)
    render_summary(metrics, args.threshold, args.n)
    if args.output:
        write_csv(samples, args.output)
        console.print(f"[green]Wrote {len(samples)} rows to {args.output}[/green]")

    return 0 if metrics.f1 >= args.min_f1 else 1


if __name__ == "__main__":
    sys.exit(main())
