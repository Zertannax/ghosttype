"""Generate AI text corpus using local LLM via Ollama.

Usage:
    python scripts/generate_ai_corpus.py --model qwen3:14b --output data/datasets/ollama_qwen3_14b/ --count 50 --pilot
    python scripts/generate_ai_corpus.py --model qwen3:14b --output data/datasets/ollama_qwen3_14b/ --count 1000
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

OLLAMA_URL = "http://localhost:11434/api/chat"

# 100 prompts across 5 domains × 20 prompts each
PROMPTS = {
    "corporate": [
        "Write an email to a client about project delays.",
        "Write a LinkedIn post about leadership in tech.",
        "Write a quarterly report introduction for a SaaS company.",
        "Write a job description for a senior software engineer.",
        "Write a press release announcing a new product feature.",
        "Write a meeting agenda for a team retrospective.",
        "Write a proposal for implementing agile methodology.",
        "Write an apology email to customers for a service outage.",
        "Write a company blog post about diversity and inclusion.",
        "Write a pitch deck introduction for investors.",
        "Write a performance review for an employee.",
        "Write a partnership proposal between two tech companies.",
        "Write an announcement about office policy changes.",
        "Write a customer success story for a B2B software.",
        "Write a memo about budget cuts to department heads.",
        "Write a welcome message for new hires.",
        "Write a competitive analysis of two market leaders.",
        "Write a request for proposal (RFP) for IT services.",
        "Write an internal newsletter about company achievements.",
        "Write a crisis communication statement for stakeholders.",
    ],
    "academic": [
        "Write an abstract for a paper on machine learning in healthcare.",
        "Write a literature review paragraph about climate change mitigation.",
        "Write a methodology section for a psychology experiment.",
        "Write a discussion section analyzing unexpected results.",
        "Write an introduction to a thesis on renewable energy.",
        "Write a conclusion summarizing findings on urban planning.",
        "Write a paragraph comparing two theories of motivation.",
        "Write a research proposal for studying social media effects.",
        "Write a peer review comment on a submitted manuscript.",
        "Write a grant application abstract for neuroscience research.",
        "Write a case study analysis of a failed business strategy.",
        "Write a paragraph explaining statistical significance to laypeople.",
        "Write a critical analysis of a published economic model.",
        "Write a section on limitations of a survey study.",
        "Write an annotated bibliography entry for a key source.",
        "Write a hypothesis statement for an educational intervention.",
        "Write a paragraph on ethical considerations in AI research.",
        "Write a data analysis interpretation for a biology experiment.",
        "Write a synthesis of conflicting studies on nutrition.",
        "Write a recommendations section for policy makers.",
    ],
    "technical": [
        "Write a README introduction for a Python CLI tool.",
        "Write a troubleshooting guide for a common Docker error.",
        "Write API documentation for a REST endpoint.",
        "Write a step-by-step tutorial for setting up a CI/CD pipeline.",
        "Write a code review comment explaining a bug fix.",
        "Write a changelog entry for a minor version update.",
        "Write an architecture decision record (ADR) for microservices.",
        "Write a performance optimization guide for database queries.",
        "Write a security advisory for a vulnerability patch.",
        "Write a configuration guide for a reverse proxy.",
        "Write a deprecation notice for an old API version.",
        "Write a migration guide for upgrading a framework.",
        "Write an incident postmortem for a production outage.",
        "Write a comparison of two cloud deployment strategies.",
        "Write a getting started guide for new contributors.",
        "Write a best practices document for code reviews.",
        "Write a monitoring and alerting strategy document.",
        "Write a load testing plan for a web application.",
        "Write a release notes summary for version 2.0.",
        "Write a debugging checklist for memory leaks.",
    ],
    "conversational": [
        "Write a Reddit comment giving advice about career change.",
        "Write a forum reply explaining a complex topic simply.",
        "Write a Quora answer about productivity tips.",
        "Write a Stack Overflow answer to a beginner question.",
        "Write a Twitter thread about a recent tech controversy.",
        "Write a casual email to a friend about weekend plans.",
        "Write a Discord message explaining a new feature.",
        "Write a blog comment agreeing with an opinion piece.",
        "Write a product review for a recent purchase.",
        "Write a response to a negative customer review.",
        "Write a dating app bio for a software engineer.",
        "Write a podcast transcript introduction about AI ethics.",
        "Write a newsletter subscriber welcome message.",
        "Write a FAQ answer about return policies.",
        "Write a community guidelines update for a forum.",
        "Write a thank-you note to a mentor.",
        "Write an invitation to a virtual meetup.",
        "Write a poll question for a community survey.",
        "Write an introduction for a guest blog post.",
        "Write a response to 'Tell me about yourself' in an interview.",
    ],
    "creative": [
        "Write a short story opening about a mysterious letter.",
        "Write a poem about autumn in a city.",
        "Write a character description for a fantasy novel.",
        "Write a dialogue between two strangers on a train.",
        "Write a scene description of a rainy market.",
        "Write a flash fiction piece about time travel.",
        "Write a monologue from a villain's perspective.",
        "Write a travel blog entry about an unexpected adventure.",
        "Write a diary entry from a future colonist on Mars.",
        "Write a myth about how the stars were created.",
        "Write a restaurant review with vivid sensory details.",
        "Write a letter from a soldier to their family.",
        "Write a comedic sketch about a tech support call.",
        "Write a ghost story set in an abandoned library.",
        "Write a personal essay about learning to cook.",
        "Write a science fiction scene about first contact.",
        "Write a romance scene in a coffee shop.",
        "Write a horror story opening with no supernatural elements.",
        "Write a children's story about a brave mouse.",
        "Write a reflective piece about a childhood memory.",
    ],
}

ALL_PROMPTS = []
for domain, prompts in PROMPTS.items():
    for prompt in prompts:
        ALL_PROMPTS.append({"domain": domain, "prompt": prompt})


def generate_passage(client: httpx.Client, prompt: str, model: str) -> str | None:
    """Generate a single passage via Ollama chat API."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Write responses as plain text without markdown formatting, code blocks, or bullet points. Write natural, flowing prose of at least 100 words. Be detailed and expansive."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 800,
        },
    }
    try:
        response = client.post(OLLAMA_URL, json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        print(f"Error generating: {e}", file=sys.stderr)
        return None


def quality_filter(text: str) -> bool:
    """Basic quality check."""
    words = text.split()
    n_words = len(words)
    if n_words < 30 or n_words > 500:
        return False
    if "http" in text.lower():
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI corpus via Ollama")
    parser.add_argument("--model", default="qwen3:14b", help="Ollama model name")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--count", type=int, default=50, help="Number of passages")
    parser.add_argument("--pilot", action="store_true", help="Pilot mode (saves as pilot)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select prompts
    random.seed(args.seed)
    selected = random.sample(ALL_PROMPTS, min(args.count, len(ALL_PROMPTS)))

    # Resume support
    suffix = "pilot" if args.pilot else "full"
    output_file = output_dir / f"generated_{suffix}.jsonl"
    existing = set()
    if output_file.exists():
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                existing.add(data["prompt"])
        print(f"Resuming: {len(existing)} passages already generated")

    client = httpx.Client()
    generated = []
    skipped = 0

    print(f"Generating {len(selected)} passages with {args.model}...")
    print(f"Output: {output_file}")

    for i, item in enumerate(selected, 1):
        if item["prompt"] in existing:
            print(f"[{i}/{len(selected)}] SKIP (already exists)")
            continue

        print(f"[{i}/{len(selected)}] {item['domain']}: {item['prompt'][:50]}...", end=" ")
        start = time.time()
        text = generate_passage(client, item["prompt"], args.model)
        elapsed = time.time() - start

        if text is None or not quality_filter(text):
            print(f"FAIL ({elapsed:.1f}s)")
            skipped += 1
            continue

        record = {
            "text": text,
            "prompt": item["prompt"],
            "domain": item["domain"],
            "model": args.model,
            "timestamp": datetime.utcnow().isoformat(),
            "word_count": len(text.split()),
        }
        generated.append(record)

        # Append immediately
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"OK ({len(text.split())} words, {elapsed:.1f}s)")

    print(f"\nDone! Generated: {len(generated)}, Skipped: {skipped}")
    print(f"Total in file: {len(existing) + len(generated)}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
