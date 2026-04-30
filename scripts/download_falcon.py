"""Download Falcon RefinedWeb sample for human baseline."""

import json
from pathlib import Path

from datasets import load_dataset

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

print("Downloading Falcon RefinedWeb sample...")
ds = load_dataset("tiiuae/falcon-refinedweb", split="train", streaming=True)

passages = []
for row in ds:
    text = row["content"].strip()
    if 50 <= len(text.split()) <= 500:
        if "<" not in text and "http" not in text[:100]:
            passages.append({
                "text": text,
                "source": "falcon",
                "model": "human",
                "domain": "web",
            })
    if len(passages) >= 1000:
        break

output = RAW_DIR / "falcon_human.jsonl"
with open(output, "w", encoding="utf-8") as f:
    for p in passages:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

print(f"  Saved {len(passages)} passages to {output}")
