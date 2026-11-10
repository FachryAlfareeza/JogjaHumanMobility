# Anti-AI-Slop Guidelines

These rules apply to everything in this repo: docs, notebooks, code, figure titles, the video script and the slides. They apply whether a person or an AI tool wrote the first draft. Whoever commits a change is responsible for it and must be able to explain every line during the presentation.

"Slop" means text or code that looks finished but says little, claims more than the data shows, or was pasted without being checked.

## 1. Claims and numbers

1. Every number in a doc, slide or script comes from a notebook cell or a cited source. If you can't point to where it came from, delete it.
2. Report the effect size and the method together: "Spearman r = 0.31 (151 days, same-weekday deviation)", not "the sources agree strongly".
3. Match the wording to the evidence. For our data, r around 0.3 is "weak to moderate", not "strong". A single holiday spike is "an example", not "proof".
4. Say "likely" when something is an interpretation (for example "the lattice cells are likely rounded coordinates"). Drop "likely" only when it has been checked.
5. Name the limitation next to the result, not in a separate section nobody reads. Devices are not people. The panel shrinks and shifts. OD for March–April is reduced quality.
6. No invented sources, dates or citations. If a fact (holiday date, PPKM level, population year) isn't verified, mark it `unverified` in the table.

## 2. Writing

Cut these on sight:

| Pattern | Example | Write instead |
|---|---|---|
| Filler openers and closers | "In today's data-driven world…", "In conclusion, this shows…" | Start with the point; stop when it's made |
| Hype words | robust, seamless, crucial, comprehensive, delve, leverage, powerful, insightful, game-changer | The plain word, or nothing |
| Empty contrasts | "This isn't just data, it's a story" | Say what the data shows |
| Reflexive threes | "fast, reliable, and scalable" | Only the items that are true and matter |
| Emoji and status icons | ✅ ❌ 🟡 🚀 | "done", "not usable", "to check" |
| Bold everywhere | Several bold phrases per paragraph | At most one bold phrase per section, for a warning or a deadline |
| Arrow chains in prose | "raw → clean → insight → impact" | A sentence, or a table |
| Restating the heading | "## Results" followed by "This section presents the results" | Go straight to the results |
| Vague quantities | "a lot", "significant", "many" | The number |

Other rules:
- Prefer tables for comparisons and short sentences for reasoning.
- One term per thing. Use "device", not "user"/"person"/"MAID" interchangeably. Use "kapanewon" for all 78 units, including the city's kemantren.
- Indonesian place names keep their normal spelling (Gunungkidul, Kulon Progo).

## 3. Figures

- The title states what the figure shows ("Share of DIY device-hours by kabupaten"), or the finding if the figure proves it. It doesn't sell.
- Axis labels include units. Color scales say what they encode and whether they're log-scaled.
- If a figure relies on a normalization (shares, weekday deviation), the subtitle or caption says so.
- Don't show raw device counts over time as if they were mobility. The panel changes size.

## 4. Code

- No placeholder or dead code in committed files: no `pass  # TODO`, no unused imports, no commented-out blocks.
- Comments explain why, not what. `# mean over all days, so rarely published cells don't rank high` is useful; `# compute the mean` is not.
- Check data assumptions with `assert` or a raised error (row counts, unique keys, date ranges, no unmatched joins). Never silence errors with a bare `except`.
- One copy of each rule. Constants such as panel breaks, the lattice rule and paths live in `src/config.py`; notebooks import them instead of redefining them.
- Every output file is produced by a script or notebook in the repo. Nothing is hand-edited after it's generated.
- Scripts are rerunnable: running `clean.py` then `build_features.py` twice gives identical outputs.

## 5. AI tools

Using AI assistants is allowed. These conditions apply:

1. Read and run everything it produces before committing. If you can't explain it, don't commit it.
2. Check every fact it states (dates, sources, method claims) against the data or a real source. AI tools invent plausible citations and holiday dates.
3. Rewrite generated prose with section 2 in mind; first drafts from AI tools hit most of the patterns in that table.
4. Don't paste AI output into the video script or slides without checking the numbers against the notebooks.

## 6. Checklist before committing

- [ ] Every number traces to a cell or a source
- [ ] Wording matches effect size; limitations sit next to results
- [ ] No hype words, emoji, filler, or bold-heavy paragraphs
- [ ] Figures have units, honest titles, and normalization noted
- [ ] No dead code, no duplicated constants, assertions on joins and row counts
- [ ] Notebook runs top to bottom from a clean kernel
