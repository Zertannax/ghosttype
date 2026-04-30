"""Build GhostType reference corpus from downloaded datasets."""

import json
import random
import re
from collections import Counter
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("ghosttype/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_AI = 1000
TARGET_HUMAN = 1000

MIN_WORDS = 30
MAX_WORDS = 500
MIN_UNIQUE_RATIO = 0.5


def quality_filter(text):
    """Apply quality filters."""
    words = text.split()
    n_words = len(words)

    if n_words < MIN_WORDS or n_words > MAX_WORDS:
        return False

    if re.search(r'<[^\u003e]+>|```|\[.*?\]\(.*?\)', text):
        return False

    if len(re.findall(r'http[s]?://', text)) > 2:
        return False

    unique_words = set(w.lower() for w in words)
    if len(unique_words) / n_words < MIN_UNIQUE_RATIO:
        return False

    alpha_chars = sum(1 for c in text if c.isalpha() or c.isspace())
    if alpha_chars / len(text) < 0.7:
        return False

    return True


def deduplicate(passages, threshold=0.8):
    """Deduplicate based on word overlap."""
    unique = []
    for p in passages:
        text = p["text"]
        words = set(text.lower().split())

        is_duplicate = False
        for u in unique:
            u_words = set(u["text"].lower().split())
            if len(words & u_words) / max(len(words), len(u_words)) > threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append(p)

    return unique


def load_passages(filepath):
    """Load passages from jsonl."""
    passages = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            passages.append(json.loads(line))
    return passages


def sample_balanced(passages, target, key="domain"):
    """Sample balanced by key."""
    by_key = {}
    for p in passages:
        k = p.get(key, "unknown")
        by_key.setdefault(k, []).append(p)

    n_keys = len(by_key)
    per_key = target // n_keys

    sampled = []
    for k, items in by_key.items():
        if len(items) >= per_key:
            sampled.extend(random.sample(items, per_key))
        else:
            sampled.extend(items)

    remaining = target - len(sampled)
    if remaining > 0:
        pool = [p for p in passages if p not in sampled]
        sampled.extend(random.sample(pool, min(remaining, len(pool))))

    random.shuffle(sampled)
    return sampled[:target]


def embed_texts(texts, model_name="BAAI/bge-small-en-v1.5", batch_size=32):
    """Embed texts in batches to avoid OOM."""
    print(f"  Loading embedding model: {model_name}")
    model = TextEmbedding(model_name=model_name)

    print(f"  Embedding {len(texts)} passages in batches of {batch_size}...")
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = list(model.embed(batch))
        all_embeddings.extend(embeddings)
        if (i // batch_size + 1) % 10 == 0:
            print(f"    ... {len(all_embeddings)}/{len(texts)} done")

    return np.array(all_embeddings, dtype=np.float32)


def main():
    print("=" * 60)
    print("GhostType Corpus Builder")
    print("=" * 60)

    random.seed(42)

    print("\n1. Loading raw data...")
    raid_ai = load_passages(RAW_DIR / "raid_ai.jsonl")
    raid_human = load_passages(RAW_DIR / "raid_human.jsonl")
    falcon_human = load_passages(RAW_DIR / "falcon_human.jsonl")

    print(f"   RAID AI: {len(raid_ai)}")
    print(f"   RAID Human: {len(raid_human)}")
    print(f"   Falcon Human: {len(falcon_human)}")

    print("\n2. Applying quality filters...")
    raid_ai = [p for p in raid_ai if quality_filter(p["text"])]
    raid_human = [p for p in raid_human if quality_filter(p["text"])]
    falcon_human = [p for p in falcon_human if quality_filter(p["text"])]

    print(f"   RAID AI after filter: {len(raid_ai)}")
    print(f"   RAID Human after filter: {len(raid_human)}")
    print(f"   Falcon Human after filter: {len(falcon_human)}")

    print("\n3. Deduplicating...")
    raid_ai = deduplicate(raid_ai)
    raid_human = deduplicate(raid_human)
    falcon_human = deduplicate(falcon_human)

    print(f"   RAID AI after dedup: {len(raid_ai)}")
    print(f"   RAID Human after dedup: {len(raid_human)}")
    print(f"   Falcon Human after dedup: {len(falcon_human)}")

    print(f"\n4. Sampling {TARGET_AI} AI + {TARGET_HUMAN} human passages...")

    ai_passages = sample_balanced(raid_ai, TARGET_AI, key="model")
    human_pool = raid_human + falcon_human
    human_passages = sample_balanced(human_pool, TARGET_HUMAN, key="source")

    print(f"   AI passages: {len(ai_passages)}")
    print(f"   Human passages: {len(human_passages)}")

    ai_texts = [p["text"] for p in ai_passages]
    human_texts = [p["text"] for p in human_passages]

    print("\n5. Embedding AI passages...")
    ai_embeddings = embed_texts(ai_texts)

    print("\n6. Embedding human passages...")
    human_embeddings = embed_texts(human_texts)

    print("\n7. Saving embeddings...")
    np.savez(OUTPUT_DIR / "slop_corpus.npz", embeddings=ai_embeddings)
    np.savez(OUTPUT_DIR / "human_corpus.npz", embeddings=human_embeddings)

    meta = {
        "version": "0.4.0",
        "date": "2026-04-30",
        "model": "BAAI/bge-small-en-v1.5",
        "dimensions": 384,
        "slop_corpus": {
            "n_passages": len(ai_passages),
            "sources": dict(Counter(p["source"] for p in ai_passages)),
            "models": dict(Counter(p["model"] for p in ai_passages)),
        },
        "human_corpus": {
            "n_passages": len(human_passages),
            "sources": dict(Counter(p["source"] for p in human_passages)),
        },
    }

    with open(OUTPUT_DIR / "corpus_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\n   Saved: {OUTPUT_DIR}/slop_corpus.npz")
    print(f"   Saved: {OUTPUT_DIR}/human_corpus.npz")
    print(f"   Saved: {OUTPUT_DIR}/corpus_meta.json")

    print("\n" + "=" * 60)
    print("Corpus Statistics")
    print("=" * 60)
    print(f"AI corpus: {ai_embeddings.shape}")
    print(f"  Sources: {meta['slop_corpus']['sources']}")
    print(f"  Models: {meta['slop_corpus']['models']}")
    print(f"\nHuman corpus: {human_embeddings.shape}")
    print(f"  Sources: {meta['human_corpus']['sources']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
