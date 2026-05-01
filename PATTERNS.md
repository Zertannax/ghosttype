# GhostType — AI Slop Pattern Taxonomy

> Reference document for the heuristic engine.
> Each pattern has: **ID**, **category**, **examples**, **severity**, **rationale**.

The full machine-readable definitions live in `ghosttype/heuristics/patterns/`. This document explains the design intent and the cross-cutting rules.

---

## Severity scale

| Severity | Meaning |
|---:|---|
| `+0.9` | High-confidence AI tell (rare in human prose) |
| `+0.7–0.8` | Strong AI signal (very common in LLM output) |
| `+0.5–0.6` | Medium signal (frequent in AI, occasional in humans) |
| `+0.3–0.4` | Weak / contextual signal |
| `−0.2 to −0.5` | **Human indicator** — reduces the document score |

---

## Categories

### 1. Generic Openers · `OP-XX` · 10 patterns

Phrases that start text with zero information density. Classic AI tell.
**Average severity: 0.8**

| ID | Pattern | Examples |
|---|---|---|
| OP-01 | Temporal universalism | "In today's world", "In the modern era" |
| OP-02 | Importance declaration | "It is important to note that" |
| OP-03 | Topic announcement | "When it comes to X", "In the realm of X" |
| OP-04 | Rhetorical question opener | "Have you ever wondered…", "Imagine a world…" |
| OP-05 | Definition stall | "X is defined as…", "By definition…" |
| OP-06–10 | Variants ("In an era of…", "Let us…", "Before we begin…", etc.) |

---

### 2. Hedge Fillers · `HE-XX` · 10 patterns

Qualifiers that add words without adding meaning.
**Severity: 0.5 (medium)**

| ID | Pattern | Examples |
|---|---|---|
| HE-01 | Epistemic hedges | "It is worth noting", "It should be noted" |
| HE-02 | Soft assertions | "One could argue", "Some might say" |
| HE-03 | Temporal hedges | "At the end of the day", "Ultimately" |
| HE-04 | Scope limiters | "To some extent", "In a sense" |
| HE-05 | Affirmation starters | "Certainly," / "Absolutely," at sentence start |
| HE-06–10 | Variants ("broadly speaking", etc.) |

---

### 3. Buzzword Clusters · `BZ-XX` · 16 patterns

Corporate / AI vocabulary that replaces concrete description.
**Average severity: 0.6, with BZ-05 and BZ-14 at 0.9**

| ID | Pattern | Examples |
|---|---|---|
| BZ-01 | Synergy vocab | `synergy`, `leverage`, `paradigm shift`, `game-changer` |
| BZ-02 | Comprehensiveness | `comprehensive solution`, `holistic`, `robust framework` |
| BZ-03 | Impact theater | `transformative`, `groundbreaking`, `revolutionary` |
| BZ-04 | Process language | `facilitate`, `utilize`, `implement solutions` |
| **BZ-05** | **AI self-description (high confidence)** | **`delve`, `tapestry`, `nuanced understanding`, `multifaceted`** |
| BZ-06 | Business value | `value-added`, `actionable`, `impactful` |
| BZ-07 | Tech startup | `disruptive`, `scalable`, `sustainable`, `data-driven` |
| BZ-08 | Abstract systems | `paradigm`, `conceptual framework`, `evolving landscape` |
| BZ-09 | Process improvement | `streamline`, `optimize`, `enhance`, `maximize` |
| BZ-10 | Corporate keys | `key stakeholders`, `core competencies` |
| BZ-11–16 | Variants (corporate process / architecture / vision) |

---

### 4. Over-Structure · `ST-XX` · 6 patterns

Artificial enumeration and signposting that breaks natural flow.
**Severity: 0.7**

| ID | Pattern | Examples |
|---|---|---|
| ST-01 | Ordinal sequencing | "Firstly… Secondly… Thirdly… Finally…" |
| ST-02 | Aspect listing | "There are X key aspects: 1) … 2) … 3) …" |
| ST-03 | Paragraph signposting | "In this section we will explore…" |
| ST-04 | Conclusion markers | "In conclusion,", "To summarize,", "In summary," |
| ST-05 | Transition narration | "Having established X, we can now turn to Y" |
| ST-06 | Other emphasis ("It is important…") |

---

### 5. Fake Balance · `FB-XX` · 4 patterns

Artificial both-sidesing that signals no actual position.
**Severity: 0.6**

| ID | Pattern | Examples |
|---|---|---|
| FB-01 | Classic both-sides | "On one hand… on the other hand…" |
| FB-02 | Pros/cons frame | "While X has advantages, it also has disadvantages" |
| FB-03 | Proponents/critics | "Proponents argue… Critics contend…" (no resolution) |
| FB-04 | Complexity acknowledgment | "The issue is complex and multifaceted" (without unpacking) |

---

### 6. AI Transitions · `TR-XX` · 6 patterns

Filler transitions overused by LLMs.
**Severity: 0.5**

| ID | Pattern | Examples |
|---|---|---|
| TR-01 | Additive transitions | "Furthermore,", "Moreover," (clustered) |
| TR-02 | Contrastive fillers | "However, it is important to…" |
| TR-03 | Elaboration signals | "To elaborate on this point…" |
| TR-04 | Consequence chains | "Consequently,", "Therefore," (overused) |
| TR-05–06 | Variants |

---

### 7. Journalist Patterns · `JR-XX` · 12 patterns

Modern AI-journalism style + classical-oratory negative-severity detectors.
**Mixed severities (positive 0.5–0.8, negative −0.3 to −0.5)**

| ID | Pattern | Examples / Notes |
|---|---|---|
| JR-02 | Journalistic setup | "Here's why", "Let me explain" |
| JR-04 | Journalistic revelation | "What nobody tells you", "The real signal" |
| JR-06 | Rhetorical question | "Why now?", "What if?", "Have you noticed?" |
| JR-08 | Journalistic conclusion | "The takeaway", "Bottom line", "Long story short" |
| JR-10 | Implicit assertion | "It goes without saying", "Nobody can deny" |
| JR-20 | EN statistics dump | `12% on`, `3 out of 10`, `5x faster`, `2-fold` |
| **JR-21** | **Classical oratory address** (−0.4) | "My fellow Americans", "Fellow citizens", "Dear friends" |
| **JR-23** | **Self-correcting construction** (−0.3) | "I do not say X — I say Y", "Not X, but Y", "I tell you" |
| **JR-24** | **Famous oratorical formulas** (−0.5) | "We shall fight", "I have a dream", "Blood, toil, tears", "Ask not what" |
| JR-25 | Listicle format | "Top 10", "5 ways to", "3 reasons" |
| JR-26 | AI emoji formatting | 👉💡⚠️🔥🚀✅❌📊 |
| JR-27 | Bullet point formatting | `^[-*•]` lines |

The negative-severity oratory detectors fire the **human-indicator bonus** in the aggregator (up to −50 to the document score).

---

### 8. Conversational Slop · `CS-XX` · 15 patterns

ChatGPT / Claude neutral, hedged, over-agreeable style.
**Severity: 0.5**

15 patterns covering setup framing, fake humility, neutrality signals, journey metaphors, value reframing, etc.

---

### 9. Academic Markers · `AC-XX` · 15 patterns

AI-generated research-paper conventions.
**Severity: 0.4–0.7**

15 patterns covering thesis statements, findings, literature review, transition words (excluding `however`/`therefore` which are too common in human prose), passive voice, methodology buzzwords, etc.

---

### 10. Technical Markers · `TC-XX` · 15 patterns

AI-generated documentation / tutorial conventions.
**Severity: 0.4–0.6**

15 patterns covering section introductions, step-by-step procedures, prerequisites, command instructions, callout boxes, troubleshooting, performance metrics, etc.

---

### 11. Creative Writing · `CR-XX` · 15 patterns

Fiction / storytelling AI tells.
**Severity: 0.5–0.8**

| ID | Pattern | Examples |
|---|---|---|
| CR-01 | Cliché story opener | "Once upon a time", "In a world where", "It was a dark and stormy night" |
| CR-02 | Purple-prose colour | "cerulean eyes", "emerald gaze", "obsidian hair", "crimson lips" |
| CR-03 | Told-not-shown emotion | "She felt a wave of sadness", "A surge of relief" |
| CR-04 | Body-action beat | "his heart skipped a beat", "her eyes hitched" |
| CR-05 | Generic metaphor | "like an ancient X", "as if the world itself…" |
| CR-06 | Stock atmosphere | "an eerie silence", "the air hung thick", "time seemed to stand still" |
| CR-07 | Adverbial dialogue tag | "she whispered softly", "voice barely above a whisper" |
| CR-08 | Eye-contact cliché | "their eyes met", "gazes locked" |
| CR-09 | Aesthetic landscape | "bathed in golden light", "drenched in moonlight" |
| CR-10 | Cheap revelation | "in that moment she knew", "everything changed in an instant" |
| CR-11 | Hedged narration | "she couldn't help but…", "she found herself…" |
| CR-12 | Internal monologue | "thoughts swirled", "her mind raced" |
| CR-13 | Sensory formula | "the scent of X filled the air" |
| CR-14 | Storybook ending | "and so, her journey began", "and that was how it all began" |
| CR-15 | Body-horror cliché | "shiver ran down her spine", "blood ran cold", "heart pounded in her chest" |

---

## Cross-cutting rules

### Deduplication

Multiple patterns can match the same span (e.g. "in summary" lives in ST-04, AC-05, and TC-08). The engine deduplicates hits sharing the same `(matched_text.lower(), start_char)` and keeps the one with the largest absolute severity. This prevents triple-counting.

### Cluster bonus

When a passage has hits in **3 or more distinct positive-severity categories**, the raw passage score is multiplied by **1.15** (per `CLUSTER_BONUS_MULTIPLIER` in `scorer.py`). Clustered patterns are more diagnostic than isolated ones — text that simultaneously triggers buzzwords + transitions + academic markers is much more likely to be AI than text triggering one of those three times.

Negative-severity (human indicator) categories don't count toward cluster.

### BZ-05 special rule

When **2 or more BZ-05 hits** appear in the same passage (any combination of `delve`, `tapestry`, `nuanced understanding`, `multifaceted`), the passage score is **floored at 70** (HIGH). These four phrases are near-zero false-positive AI tells; their co-occurrence is essentially a signature.

### Length normalization

Passage scores are normalized by **word count**, with a floor at 10 words:

```
length_factor = sqrt(max(10, word_count)) / 3.0
score = (sum(severities) / length_factor) * 100  →  clamp [0, 100]
```

This prevents short passages from accumulating disproportionate scores per hit, while keeping density signals intact for medium-length text.

### `re.IGNORECASE | re.MULTILINE`

All patterns are compiled with both flags. Inline `(?i)` prefixes have been removed (redundant). MULTILINE means `^` and `$` anchor to line boundaries — important for patterns like ST-04 ("In conclusion,") that should match at paragraph starts, not just at the start of the entire input.

---

## Patterns NOT included (intentionally)

These tells exist but are excluded because their false-positive rate on legitimate human writing is too high:

- **Passive voice** alone — common in academic, technical, legal text
- **Long sentences** — common in literary prose (Faulkner, Joyce, etc.)
- **Formal vocabulary** — legitimate in many human registers
- **Absence of contractions** — too context-dependent

---

## Contributing new patterns

When proposing a new pattern:

1. Assign an ID following `CATEGORY-##` (e.g. `BZ-17`, `CR-16`).
2. Test the false-positive rate against `tests/fixtures/sample_human.txt` — should not fire.
3. Test the true-positive rate against the AI corpus (`data/datasets/ollama_*/`) — should fire on a meaningful subset.
4. Add a description that explains *why* it's an AI tell, not just what it matches.
5. Run `scripts/benchmark.py` before/after to confirm the F1 doesn't regress.
6. Document the rationale in this file under the matching category.
