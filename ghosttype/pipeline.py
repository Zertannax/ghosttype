"""Shared analysis pipeline used by both the CLI and the web API.

A single source of truth for: preprocess → engine → semantic + stylistic →
aggregate. Both surfaces serialize results identically through `result_to_dict`.
"""

from ghosttype.heuristics.engine import HeuristicEngine
from ghosttype.preprocessor import preprocess
from ghosttype.scorer import AnalysisResult, aggregate
from ghosttype.semantic import semantic_score_passages
from ghosttype.stylistic import stylistic_score_passages


def analyze_text(text: str) -> AnalysisResult | None:
    """Run the full analysis pipeline. Returns None for whitespace-only input."""
    if not text.strip():
        return None
    passages = preprocess(text)
    engine = HeuristicEngine()
    hits_by_passage = engine.analyze(passages)
    semantic = semantic_score_passages(passages)
    stylistic = stylistic_score_passages(passages)
    return aggregate(passages, hits_by_passage, semantic, stylistic)


def result_to_dict(result: AnalysisResult) -> dict:
    """Convert AnalysisResult to a JSON-serializable dict.

    Includes the score breakdown when present so the web UI can render the
    same explanation panel as the CLI's --explain flag.
    """
    payload: dict = {
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
                "cluster_bonus_applied": pr.cluster_bonus_applied,
                "bz05_rule_applied": pr.bz05_rule_applied,
                "hits": [
                    {
                        "pattern_id": hit.pattern_id,
                        "category": hit.category,
                        "matched_text": hit.matched_text,
                        "severity": hit.severity,
                        "start_char": hit.start_char,
                        "end_char": hit.end_char,
                    }
                    for hit in pr.hits
                ],
            }
            for pr in result.passages
        ],
    }
    if result.breakdown is not None:
        b = result.breakdown
        payload["breakdown"] = {
            "heuristic_doc_score": b.heuristic_doc_score,
            "semantic_score": b.semantic_score,
            "stylistic_score": b.stylistic_score,
            "human_indicators": b.human_indicators,
            "human_bonus": b.human_bonus,
            "weights": {
                "heuristic": b.h_weight,
                "semantic": b.s_weight,
                "stylistic": b.st_weight,
            },
        }
    return payload
