# GhostType — Datasets Reference

> Where to get training/reference data, what to use it for, how to prepare it.

---

## Datasets used in GhostType

### 1. HC3 — Human ChatGPT Comparison Corpus

**What:** Paired human/ChatGPT answers to the same questions across multiple domains (medicine, finance, open QA, Wikipedia, Reddit ELI5).

**Why:** Gold standard for human vs AI text. Well-balanced, multi-domain, widely cited.

**Where:** https://huggingface.co/datasets/Hello-SimpleAI/HC3

**Size:** ~58k QA pairs (~24k human, ~24k ChatGPT)

**How to use in GhostType:**
- Extract ChatGPT answers → `slop_corpus` (positive examples)
- Extract human answers → `human_corpus` (negative examples)
- Balance to ~500 passages each for the shipped `.npz` reference vectors

```python
from datasets import load_dataset
ds = load_dataset("Hello-SimpleAI/HC3", "all")
human = [row["human_answers"][0] for row in ds["train"] if row["human_answers"]]
ai    = [row["chatgpt_answers"][0] for row in ds["train"] if row["chatgpt_answers"]]
```

---

### 2. RAID Benchmark

**What:** Large-scale multi-model AI detection benchmark. Covers GPT-4, Claude, Llama, Mistral, etc. across 11 domains and 4 attack types (paraphrase, synonym substitution, etc.).

**Why:** More diverse than HC3. Tests robustness against evasion techniques.

**Where:** https://huggingface.co/datasets/liamdugan/raid

**Size:** ~6M passages

**How to use in GhostType:**
- Use for validation only (don't mix with HC3 in training corpus)
- Particularly useful: `paraphrase` split — tests if your detector catches AI text that's been lightly edited

---

### 3. AuTextification

**What:** Multilingual human vs AI detection dataset. Includes **French** (important for us).

**Why:** The only well-structured multilingual dataset. French support matters for broader adoption.

**Where:** https://huggingface.co/datasets/symanto/autextification2023

**How to use in GhostType:**
- French subset → basis for a future `--lang fr` mode
- Keep separate from English corpus, don't mix embeddings

---

### 4. Project Gutenberg (human baseline)

**What:** Public domain books — unambiguously human-written, pre-LLM.

**Why:** High-quality negative examples. No risk of contamination.

**Where:** https://www.gutenberg.org / `gutenbergpy` library

**How to use:**
- Extract random 200–500 word passages
- Filter to 20th century and earlier (avoid style drift)
- Use as hard negatives in the human corpus

```python
import gutenbergpy.textget as gt
text = gt.get_text_by_id(1342)  # Pride and Prejudice
```

---

### 5. Reddit WritingPrompts (human creative)

**What:** Human-written creative fiction responses to prompts.

**Why:** Captures informal, creative human voice. Contrasts with formal AI writing style.

**Where:** https://huggingface.co/datasets/euclaise/writingprompts

**Caution:** Post-2023 data may contain AI-generated text. Filter to pre-2023 if possible.

---

## Building the reference corpus (`.npz` files)

The shipped corpus is pre-embedded to avoid requiring users to run embedding at install time.

```bash
# Run once during development, output committed to repo
python scripts/build_corpus.py \
  --slop-sources hc3,raid \
  --human-sources gutenberg,writingprompts \
  --n-passages 500 \
  --model BAAI/bge-small-en-v1.5 \
  --output ghosttype/data/
```

Output:
- `slop_corpus.npz` — shape: (500, 384)
- `human_corpus.npz` — shape: (500, 384)
- `corpus_meta.json` — sources, date, model used

---

## Datasets NOT used and why

| Dataset | Reason excluded |
|---------|----------------|
| GPTZero training data | Proprietary, not auditable |
| OpenAI detector dataset | Deprecated, poor quality |
| TuringBench | Too small (~200 samples), outdated |
| ArguGPT | Academic only, too narrow domain |

---

## Updating the corpus

When new major models drop (GPT-5, Claude 4, etc.) the slop corpus needs updating.

1. Collect 100+ passages from the new model via RAID benchmark updates or manual collection
2. Re-run `scripts/build_corpus.py` with `--append` flag
3. Bump version in `corpus_meta.json`
4. Run validation: `python scripts/validate_corpus.py` (target: >75% classification accuracy on HC3 test split)
5. Ship new `.npz` files in next release

---

## License notes

| Dataset | License | Can ship? |
|---------|---------|-----------|
| HC3 | CC BY 4.0 | ✅ Yes (with attribution) |
| RAID | CC BY 4.0 | ✅ Yes (with attribution) |
| AuTextification | CC BY 4.0 | ✅ Yes |
| Project Gutenberg | Public Domain | ✅ Yes |
| WritingPrompts | Reddit API ToS | ⚠️ Don't ship raw text, only embeddings |

We ship **embeddings only** (`.npz`), not raw text. This avoids ToS issues and keeps the package small.
