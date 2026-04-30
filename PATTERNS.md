# GhostType â€” AI Slop Pattern Taxonomy

> Reference document for the heuristic engine.
> Each pattern has: ID, category, examples, severity, rationale.

---

## Category 1: Generic Openers

Phrases that start text with zero information density. Classic AI tell.

**Severity: HIGH (0.8)**

| ID | Pattern | Examples |
|----|---------|---------|
| OP-01 | Temporal universalism | "In today's world", "In the modern era", "In today's fast-paced society" |
| OP-02 | Importance declaration | "It is important to note that", "It is crucial to understand" |
| OP-03 | Topic announcement | "When it comes to X", "In the realm of X", "In the field of X" |
| OP-04 | Rhetorical question opener | "Have you ever wondered...", "What if I told you..." |
| OP-05 | Definition stall | "X is defined as", "According to Merriam-Webster", "By definition" |

---

## Category 2: Hedge Fillers

Qualifiers that add words without adding meaning. Signal uncertainty-avoidance.

**Severity: MEDIUM (0.5)**

| ID | Pattern | Examples |
|----|---------|---------|
| HE-01 | Epistemic hedges | "It is worth noting", "It should be noted", "It is important to mention" |
| HE-02 | Soft assertions | "One could argue", "Some might say", "Many would agree" |
| HE-03 | Temporal hedges | "At the end of the day", "When all is said and done", "Ultimately" (overused) |
| HE-04 | Scope limiters | "To some extent", "In many ways", "In a sense" |
| HE-05 | Affirmation starters | "Certainly", "Absolutely", "Of course" (at sentence start) |

---

## Category 3: Buzzword Clusters

Corporate/AI vocabulary that replaces concrete description.

**Severity: MEDIUM-HIGH (0.6)**

| ID | Pattern | Examples |
|----|---------|---------|
| BZ-01 | Synergy vocab | "synergy", "leverage", "paradigm shift", "game-changer" |
| BZ-02 | Comprehensiveness | "comprehensive", "holistic", "robust", "cutting-edge" |
| BZ-03 | Impact theater | "transformative", "groundbreaking", "revolutionary", "innovative" |
| BZ-04 | Process language | "facilitate", "utilize" (instead of "use"), "implement solutions" |
| BZ-05 | AI self-description | "delve into", "navigate", "tapestry", "nuanced understanding" |

> Note: BZ-05 patterns ("delve", "tapestry", "nuanced") are extremely high-confidence AI indicators. Severity can be bumped to 0.9 when clustered.

---

## Category 4: Over-Structure Patterns

Artificial enumeration and signposting that breaks natural prose flow.

**Severity: HIGH (0.7)**

| ID | Pattern | Examples |
|----|---------|---------|
| ST-01 | Ordinal sequencing | "Firstly... Secondly... Thirdly... Finally..." |
| ST-02 | Aspect listing | "There are X key aspects to consider: 1) ... 2) ... 3) ..." |
| ST-03 | Paragraph signposting | "In this section, we will explore...", "As discussed above..." |
| ST-04 | Conclusion markers | "In conclusion,", "To summarize,", "In summary," (at paragraph start) |
| ST-05 | Transition narration | "Having established X, we can now turn to Y" |

---

## Category 5: Fake Balance

Artificial both-sidesing that signals no actual position.

**Severity: MEDIUM-HIGH (0.6)**

| ID | Pattern | Examples |
|----|---------|---------|
| FB-01 | Classic both-sides | "On one hand... on the other hand..." |
| FB-02 | Advantages/disadvantages frame | "While X has advantages, it also has disadvantages" |
| FB-03 | Proponents/critics frame | "Proponents argue... Critics contend..." (with no resolution) |
| FB-04 | Complexity acknowledgment | "The issue is complex and multifaceted" (without unpacking) |

---

## Category 6: AI Transition Phrases

Filler transitions overused by LLMs to chain paragraphs.

**Severity: LOW-MEDIUM (0.5)**

| ID | Pattern | Examples |
|----|---------|---------|
| TR-01 | Additive transitions | "Furthermore,", "Moreover,", "Additionally," (clustered) |
| TR-02 | Contrastive fillers | "However, it is important to...", "Nevertheless, one must consider..." |
| TR-03 | Elaboration signals | "To elaborate on this point...", "To put it another way..." |
| TR-04 | Consequence chains | "As a result of this,", "Consequently,", "Therefore," (overused) |

---

## Scoring notes

### Clustering bonus
If 3+ patterns from different categories appear in a single passage, apply a **+0.15 severity bonus** to the passage score. Clustered patterns are more diagnostic than isolated ones.

### BZ-05 special rule
"delve", "tapestry", "nuanced understanding", "multifaceted" â€” when any 2 of these appear in the same passage, flag it as HIGH regardless of other scores. These are near-zero false-positive AI tells.

### Length normalization
Pattern hit rate is normalized by passage length. A 10-word passage with 1 hit â‰  a 200-word passage with 1 hit.

---

## Patterns NOT included (intentionally)

These exist but are excluded because false positive rate is too high:

- Passive voice â†’ common in academic writing, technical docs, legal text
- Long sentences â†’ common in literary prose
- Formal vocabulary â†’ legitimate in many contexts
- Absence of contractions â†’ too context-dependent

---

## Category 7: Journalist Patterns\n\n**Severity: MEDIUM-HIGH (0.6)**\n\nSee journalist.py for 27 patterns including conventional phrases, unsupported claims, accumulation, classical oratory (negative severity).\n\n---\n\n## Category 8: Conversational Slop\n\nChatGPT/Claude neutral, hedged, over-agreeable style.\n\n**Severity: MEDIUM (0.5)**\n\nSee conversational.py for 15 patterns including setup framing, fake humility, neutrality signals.\n\n---\n\n## Category 9: Academic Markers\n\nAI-generated research paper conventions.\n\n**Severity: MEDIUM-HIGH (0.6)**\n\nSee cademic.py for 15 patterns including thesis statements, literature review, passive voice.\n\n---\n\n## Category 10: Technical Markers\n\nAI-generated documentation/tutorial conventions.\n\n**Severity: MEDIUM (0.5)**\n\nSee 	echnical.py for 15 patterns including step procedures, command blocks, callout boxes.\n\n---\n\n## Contributing new patterns

When adding a pattern:
1. Assign an ID following the `CATEGORY-##` format
2. Test false positive rate on Project Gutenberg (target: <5%)
3. Test true positive rate on HC3 dataset (target: >60%)
4. Document rationale in this file
5. Add to appropriate `ghosttype/heuristics/patterns/` module
