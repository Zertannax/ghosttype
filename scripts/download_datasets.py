"""Download raw datasets for GhostType corpus building."""

import json
import random
from pathlib import Path

from datasets import load_dataset

# Output directories
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def download_raid_human():
    """Download human passages from RAID benchmark."""
    print("Downloading RAID human passages...")
    ds = load_dataset("liamdugan/raid", split="train", streaming=True)
    
    passages = []
    for row in ds:
        if row["model"] == "human" and row["attack"] == "none":
            text = row["generation"].strip()
            if 30 <= len(text.split()) <= 500:
                passages.append({
                    "text": text,
                    "source": "raid",
                    "model": "human",
                    "domain": row.get("domain", "unknown"),
                })
        if len(passages) >= 1500:  # Extra for filtering
            break
    
    output = RAW_DIR / "raid_human.jsonl"
    with open(output, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    
    print(f"  Saved {len(passages)} passages to {output}")
    return len(passages)


def download_raid_ai():
    """Download AI passages from RAID benchmark."""
    print("Downloading RAID AI passages...")
    ds = load_dataset("liamdugan/raid", split="train", streaming=True)
    
    passages = []
    models_seen = set()
    
    for row in ds:
        if row["model"] != "human" and row["attack"] == "none":
            text = row["generation"].strip()
            if 30 <= len(text.split()) <= 500:
                passages.append({
                    "text": text,
                    "source": "raid",
                    "model": row["model"],
                    "domain": row.get("domain", "unknown"),
                })
                models_seen.add(row["model"])
        if len(passages) >= 1500:
            break
    
    output = RAW_DIR / "raid_ai.jsonl"
    with open(output, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    
    print(f"  Saved {len(passages)} passages to {output}")
    print(f"  Models represented: {models_seen}")
    return len(passages)


def download_hc3():
    """Download HC3 paired dataset."""
    print("Downloading HC3 dataset...")
    ds = load_dataset("Hello-SimpleAI/HC3", "all", split="train")
    
    human_passages = []
    ai_passages = []
    
    for row in ds:
        # Human answers
        if row["human_answers"]:
            for ans in row["human_answers"]:
                text = ans.strip()
                if 30 <= len(text.split()) <= 500:
                    human_passages.append({
                        "text": text,
                        "source": "hc3",
                        "model": "human",
                        "domain": row.get("source", "unknown"),
                    })
        
        # ChatGPT answers
        if row["chatgpt_answers"]:
            for ans in row["chatgpt_answers"]:
                text = ans.strip()
                if 30 <= len(text.split()) <= 500:
                    ai_passages.append({
                        "text": text,
                        "source": "hc3",
                        "model": "chatgpt",
                        "domain": row.get("source", "unknown"),
                    })
        
        if len(human_passages) >= 800 and len(ai_passages) >= 800:
            break
    
    # Save human
    output_human = RAW_DIR / "hc3_human.jsonl"
    with open(output_human, "w", encoding="utf-8") as f:
        for p in human_passages[:800]:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"  Saved {len(human_passages[:800])} human passages to {output_human}")
    
    # Save AI
    output_ai = RAW_DIR / "hc3_ai.jsonl"
    with open(output_ai, "w", encoding="utf-8") as f:
        for p in ai_passages[:800]:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"  Saved {len(ai_passages[:800])} AI passages to {output_ai}")
    
    return len(human_passages[:800]), len(ai_passages[:800])


def download_falcon_sample():
    """Download a sample from Falcon RefinedWeb for human baseline."""
    print("Downloading Falcon RefinedWeb sample...")
    ds = load_dataset("tiiuae/falcon-refinedweb", split="train", streaming=True)
    
    passages = []
    for row in ds:
        text = row["content"].strip()
        # Basic quality filter
        if 50 <= len(text.split()) <= 500:
            # Reject if too much HTML/markdown
            if "<" not in text and "http" not in text[:100]:
                passages.append({
                    "text": text,
                    "source": "falcon",
                    "model": "human",
                    "domain": "web",
                })
        if len(passages) >= 800:
            break
    
    output = RAW_DIR / "falcon_human.jsonl"
    with open(output, "w", encoding="utf-8") as f:
        for p in passages:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    
    print(f"  Saved {len(passages)} passages to {output}")
    return len(passages)


if __name__ == "__main__":
    print("=" * 60)
    print("GhostType Dataset Downloader")
    print("=" * 60)
    
    total = 0
    total += download_raid_human()
    total += download_raid_ai()
    h, a = download_hc3()
    total += h + a
    total += download_falcon_sample()
    
    print("\n" + "=" * 60)
    print(f"Total passages downloaded: {total}")
    print(f"Output directory: {RAW_DIR}")
    print("=" * 60)
