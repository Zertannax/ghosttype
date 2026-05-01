# GhostType — Datasets Reference

> Where the reference embeddings come from, how to rebuild them, and what the licenses allow.

GhostType ships **embeddings only** (`.npz` files). Raw text is never committed to the repo — that keeps the package small and side-steps the licensing questions around redistributing dataset content.

---

## Current corpus (v0.5.0)

`ghosttype/data/corpus_meta.json` is the source of truth at runtime:

```json
{
  "version": "0.5.0",
  "date": "2026-05-02",
  "model": "BAAI/bge-small-en-v1.5",
  "dimensions": 384,
  "slop_corpus": {
    "n_passages": 2000,
    "sources": {
      "raid": 893,
      "ollama_qwen3_14b": 926,
      "ollama_qwen2.5_3b_seed43": 91,
      "ollama_qwen2.5_3b": 90
    },
    "models": {
      "llama-chat": 674,
      "qwen3:14b": 926,
      "mpt": 219,
      "qwen2.5:3b": 181
    }
  },
  "human_corpus": {
    "n_passages": 1000,
    "sources": { "raid": 500, "falcon": 500 }
  }
}
```

---

## Sources used

### 1. RAID Benchmark *(used for both AI and human corpora)*

**What:** Large-scale multi-model AI detection benchmark covering GPT-4, Claude, Llama, Mistral, MPT, etc. across 11 domains and 4 attack types (paraphrase, synonym substitution, etc.).

**Why:** Diverse, multi-model, contains a parallel human-written set, and has a permissive license.

**Where:** [https://huggingface.co/datasets/liamdugan/raid](https://huggingface.co/datasets/liamdugan/raid)

**How GhostType uses it:**
- AI side: `llama-chat` and `mpt` model outputs → `data/raw/raid_ai.jsonl`
- Human side: parallel human text → `data/raw/raid_human.jsonl`
- Filtered to 50–300-word passages, deduplicated, sampled balanced by source/model

**License:** CC BY 4.0 ✓ ship embeddings + cite

---

### 2. Falcon RefinedWeb *(human corpus only)*

**What:** Large-scale web-scraped corpus, the public dataset behind Falcon's pre-training.

**Why:** High-volume source of pre-2022 human text — unambiguous human-authored material from the open web.

**Where:** [https://huggingface.co/datasets/tiiuae/falcon-refinedweb](https://huggingface.co/datasets/tiiuae/falcon-refinedweb)

**How GhostType uses it:**
- Sampled, filtered to 50–300-word passages → `data/raw/falcon_human.jsonl`
- Used to balance the human corpus (500 RAID + 500 Falcon)

**License:** ODC-BY ✓ ship embeddings + cite

---

### 3. Ollama-generated AI corpus *(AI corpus only)*

**What:** Locally-generated AI text from `qwen3:14b` and `qwen2.5:3b` running through `scripts/generate_ai_corpus.py`. Covers 5 prompt domains × 20 prompts each: corporate, academic, technical, conversational, creative.

**Why:** Provides recent-model AI output (the v0.5.0 LLM generation) that RAID's older snapshots don't cover. The qwen3:14b run in particular catches modern AI tells (cleaner prose, subtler buzzword use) that older RAID models don't exhibit.

**Where:** Generated locally, not redistributed. Each user can re-generate their own:

```bash
ollama pull qwen3:14b
python scripts/generate_ai_corpus.py \
       --model qwen3:14b \
       --output data/datasets/ollama_qwen3_14b/ \
       --count 1000
```

The script supports resume — re-running it after a partial run picks up where it left off, so an 8-hour generation session can be paused and resumed safely.

**License:** Generated content has no upstream license obligation (locally produced from your prompts). Embeddings are distributed under MIT with the rest of the repo.

---

### 4. Project Gutenberg *(reserved for future human baseline)*

Not currently used in v0.5.0, but the human corpus could be extended with public-domain pre-LLM text:

```python
import gutenbergpy.textget as gt
text = gt.get_text_by_id(1342)  # Pride and Prejudice
```

Useful as a hard-negative source: text from before any LLM existed cannot possibly be AI-generated.

**License:** Public domain ✓

---

## Building the reference corpus

The shipped `.npz` files are pre-embedded so users don't need to run any embedding step at install time.

```bash
# 1. Download the raw datasets (one-off, large)
python scripts/download_datasets.py    # RAID
python scripts/download_falcon.py      # Falcon RefinedWeb sample

# 2. (Optional) Generate fresh AI samples via Ollama
python scripts/generate_ai_corpus.py \
       --model qwen3:14b \
       --output data/datasets/ollama_qwen3_14b/ \
       --count 1000

# 3. Build the .npz corpus
python scripts/build_corpus.py
```

The build script:
- Loads RAID + Falcon + every `data/datasets/ollama_*/generated_*.jsonl`
- Filters to 30–500-word passages, drops markdown / link-heavy / low-uniqueness text
- Deduplicates by 80% word-overlap
- Samples 2000 AI (balanced across sources) + 1000 human (balanced RAID/Falcon)
- Embeds with `BAAI/bge-small-en-v1.5`, batch size 32 (avoids ONNXRuntime OOM on Windows)
- Writes `slop_corpus.npz`, `human_corpus.npz`, `corpus_meta.json`

End-to-end takes ~10–15 minutes on a modern CPU after raw data is downloaded.

---

## Datasets NOT used and why

| Dataset | Reason excluded |
|---|---|
| HC3 | Considered for v0.1.0; superseded by RAID which is more diverse and current |
| GPTZero training data | Proprietary, not auditable |
| OpenAI detector dataset | Deprecated, poor quality |
| TuringBench | Too small (~200 samples), outdated |
| ArguGPT | Academic only, too narrow domain |
| AuTextification | Multilingual (FR / ES) — out of scope per English-only roadmap |
| Reddit WritingPrompts | Reddit API ToS issues; post-2023 contamination risk |

---

## Updating the corpus

When new major models drop (GPT-5, Claude 5, etc.) the slop corpus should be refreshed.

1. Generate fresh samples via Ollama (or pull from RAID updates):
   ```bash
   python scripts/generate_ai_corpus.py --model <new-model> \
          --output data/datasets/ollama_<new-model>/ --count 1000
   ```
2. Re-run `python scripts/build_corpus.py` (it auto-detects every `data/datasets/ollama_*/` subfolder).
3. Bump `CORPUS_VERSION` in the script.
4. Run `python scripts/benchmark.py` to confirm F1 doesn't regress.
5. Commit the new `.npz` files and `corpus_meta.json` together; tag a new release.

---

## License summary

| Component | License | Status |
|---|---|---|
| RAID | CC BY 4.0 | ✅ ship embeddings, cite source |
| Falcon RefinedWeb | ODC-BY | ✅ ship embeddings, cite source |
| Ollama-generated text (qwen3:14b, qwen2.5:3b) | locally produced | ✅ ship embeddings |
| Project Gutenberg (if added) | Public Domain | ✅ ship embeddings |
| GhostType code + embeddings | MIT | ✅ permissive |

We ship **embeddings only** (`.npz`) — never the raw text. This avoids ToS issues with web-scraped corpora and keeps the install size tractable (~5 MB of `.npz` files vs gigabytes of raw text).
