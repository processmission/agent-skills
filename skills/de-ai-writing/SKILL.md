---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: de-ai-writing
description: >-
  Detect, mark, and remove AI writing tics from Chinese and English drafts, so the text
  reads normally: denser, clearer, free of phrasing that obstructs reading. Use to de-AI
  a text, strip filler or clichés, or clear editing notes out of the body. Applies
  language- and model-specific rule tables and keeps the editing process out of the
  article. It rewrites style; personality and authorship stay out of scope.
---

# De-AI Writing

**What this is.** It marks the passages that read as machine-written and removes them, so the text
becomes denser and clearer to read. Work happens in five passes: scan, mark, judge, remove, rescan. Each
pass yields style evidence, and authorship stays out of scope. The result reads ordinary rather than
personable, and it keeps every fact, mechanism, number, condition, sourced uncertainty, term, and failed
attempt in place. The information survives the cleanup intact.

**The standard** is the two rule tables: [rules-zh.md](references/rules-zh.md) and
[rules-en.md](references/rules-en.md). Each row is one pattern with its kind, probe, model family,
evidence key, and advice: the scanner executes every row to mark the text, and the agent reads the same
rows to judge each mark, and each table's header defines its kinds.

Clear tics by these tables. Every ban sits in a row with its evidence before the edit starts, and taste
adds nothing mid-edit. A fixed shape they do not list is measured by the discovery pass (part 3) and
becomes a new row once it proves to be a real tic. Each table covers its own language and lists its
contested tells at the top, to be reported rather than enforced; a pattern from one table applies to that
language only.

## 1. Judgment rules

### 1.1 Keep the editing process out of the body

Hard rule: while reading, keep three things apart.

- **Article facts** — objects, events, mechanisms, data, sources, supportable causal claims.
- **Writing instructions** — banned shapes, name corrections, structure, tone.
- **Editorial findings** — a confused concept, a claim outranking its evidence, a passage to add or cut.

The body uses the facts, the instructions govern how it is written, and the findings are resolved by the
edit. The last two never appear in the body, title, caption, table, or source note: no correction notes,
rule statements, rewrite orders, repeated reminders, draft history, or defensive commentary. Never raise
an overstatement the article does not need in order to reject it.

| Case | Handling |
| --- | --- |
| Only instructs the writer or answers the author | Delete the sentence. |
| Carries a usable fact | Keep the object, action, condition, or number; rebuild it as a positive statement. |
| Concept was wrong | Use the correct concept; do not restate the wrong version and the reason for the fix. |
| The same limit keeps recurring | State it once, where the fact it qualifies appears. |
| Unverifiable and indispensable | Ask the user, or list it outside the body. Never invent, never line the body with disclaimers. |

Clearing corrections does **not** mean deleting factual boundaries: test hardware, peak windows, sample
scope, reference implementation, and unfinished work stay when they affect the conclusion, preferably
inside the fact sentence. A conclusion with solid grounds does not need "possibly", "to some extent", or
"worth watching" in every sentence. Exception: when the user asks for an erratum, a concept distinction,
or a terminology statement, that correction *is* the content.

### 1.2 Bans and their exceptions

A ban covers every variant with the same meaning and function — swapping the connective is not a fix.
Quotations, code, proper nouns, and text the user wants verbatim are never silently altered, and quoting
is not a way around a rule.

### 1.3 Review candidates

Two uses in one paragraph can be emphasis, contrast, or deliberate parallelism; the same turn in every
paragraph is mechanical. Count, sentence share, density, paragraph spread, and information gain are
evidence, not verdicts. `--max-uses` raises review priority only, and family shares are never summed into
an "AI score".

### 1.4 Rewrite the structure, not the words

If the draft advances by announcing a judgement, revealing it in layers, closing each section with a
zinger, and uplifting at the end, reconnect facts, mechanisms, and results instead. Enter from the
concrete scenario the user supplied; technical articles usually move through problem, existing options,
implementation, measurement, and next choices, with no fixed template.

- Put a judgement after the facts that support it: what changed, under which conditions it helped, how the measurement affected the next step.
- Show division of labour through what happened: who proposed, ran, or changed direction, taken from the record.
- Keep failed experiments, local-versus-whole-system differences, and regressions. Do not append "this shows the same lesson" after each case.
- Keep causal sentences adjacent; avoid one-sentence paragraphs, consecutive zingers, dense bolding, and headings with no information gain.
- Tables compare real items and figures explain relations; never manufacture a table or a fixed number of bullets to look complete.
- Keep established terminology stable; do not cycle synonyms to dodge repetition.
- Delete evaluations the mechanism does not support; where the fact exists, write the fact. End on a concrete result, a real open question, or the next step the user already has.

### 1.5 Facts and voice

Voice here means only this: invent nothing and sand away nothing real. Removing filler must not flatten
the article into a summary or fact list, or delete background, cases, or derivation a reader needs.
Technical analysis uses the observer position the user chose: what we see in the sources and how we read
it, and it leaves the project team's motives and success out of scope.

- The user's latest explicit correction wins: re-read before editing, and keep wording they already fixed and orderings they changed deliberately.
- Never invent first-person experience, emotion, meetings, arguments, motives, timelines, test results, or team behaviour — and no gut-feel comparisons such as "an engineer can only do a few of these a day".
- Distinguish source reports, independent verification, and the author's inference; put attribution next to the fact it supports.
- Do not turn a tuning order into a general rule, one hardware configuration into a universal limit, or a passing test into unconditional correctness.
- First-person narration is the observer position the user chose, and it stays: "we measured", "we have not reproduced this", "from our reading". What goes is first-person narration of the *writing act* — "we will now look at", "let me continue with the third row", "this is worth expanding" — and any performed reaction such as "this gives one pause".
- Keep the user's register otherwise: colloquialisms, concrete detail, apt metaphor, and sourced uncertainty stay where the draft already has them. Add no jokes, self-deprecation, performed hesitation, or fresh decoration; do not prefix every section with "I think", and do not add metaphors to a quota.
- When the text reads too dry, restore what the source supports instead of padding with vague emotion; this skill restores what is real, it does not decorate.
- With a personal style guide, this skill's bans and its separation of editing from the body outrank the guide's general permission for those expressions; register and taste come from the user, not from here.

### 1.6 What may change, and what may not

Editing is deleting meta text, reordering, and removing patterns a table row names. It is not
paraphrase, and tighter wording is not a goal by itself.

- **May change:** delete process and editing text; delete a repetition whose fact survives once; reorder or split a sentence; remove a pattern a table row names; replace an evaluation the mechanism does not support with the fact it does.
- **May not change: the author's propositions.** Modality (must, must not, should, may, can, usually, as much as possible), scope (which cases, which objects), quantifiers (all, some, any, exactly one, only), subject (who is responsible), conditions (when it applies), and negation polarity all stay as written. Never `not verified` → `unsupported`, `outside the current capability` → `will be rejected`, `avoids inconsistency` → `is always consistent`, `as much as possible` → `must`, `explicit X` → `X` when explicitness is part of the requirement, one term → its synonym, or a boundary restated as a positive claim.
- **A sentence stating a requirement, a boundary, or a scope** stays verbatim; when it is meta text, the whole sentence goes. Do not smooth it.
- **Every edit needs a reason**: a table row that fired (name its key), or meta text (name which kind). An edit with neither is taste, and it goes back.

## 2. Workflow

1. **Identify the language and audience.** Match the article's primary language to its table; for a bilingual text, apply both per sentence.
2. **Read the whole text and the latest feedback.** Note the facts, the structural problems, and what the user already fixed.
3. **Mark.** Run the scanner and build the worksheet: every finding and every discovered candidate becomes a mark with its position and evidence.
4. **Review group by group.** Record keep / rewrite / merge / delete with a reason for every occurrence.
5. **Edit.** Apply the decisions, keeping facts and conditions. No regex deletion, no batch pass over whole sentences, and no rewording of a proposition (1.6).
6. **Compare claims.** Run `compare_claims.py` against the original. Every flagged change — number, modality, negation, quantifier, identifier, or a rewritten sentence the tables never flagged — is either justified in the change log by its rule key or reverted.
7. **Rescan.** Check that the old pattern was not exchanged for a new one running through the whole article, and do not delete necessary conditions, rename proper nouns, or flatten the text just to clear the report. A repeat that is genuinely needed is recorded as kept.
8. **Read through, not just search.** Out-of-chat leaks · banned shapes surviving a synonym swap · lost evidence or added unsourced facts · the same content in the introduction, a section end, a summary table, and the ending · a slogan after the last informative sentence · writing-act narration, which no rule catches · same-shaped section closers · lines that tell the reader how to feel.
9. **Deliver** the text, or edit the named file. Change notes go outside the body, brief and concrete, and they classify each edit: meta deletion, reorder, rule-driven removal, or tightening that keeps the proposition. No self-score, no "AI-ness percentage", no promise that it now reads as fully human, and never paste this checklist into the article.

## 3. Scripts

`scripts/scan_writing.py` marks the text: known tics from the tables, plus repeated shapes they do not
list. `scripts/render_review.py` turns its JSON into a per-group worksheet. `scripts/compare_claims.py`
diffs a revision against its original and flags every change to a number, a modality, a negation, a
quantifier, or a sentence no rule flagged. All three are standard-library Python 3.10+, read-only, and
leave their inputs untouched.

```bash
SKILL_DIR=/path/to/de-ai-writing
python3 "$SKILL_DIR/scripts/scan_writing.py" article.md --format json > article.scan.json
python3 "$SKILL_DIR/scripts/render_review.py" article.scan.json > article.review.md
python3 "$SKILL_DIR/scripts/compare_claims.py" article.md article.de-ai.md
```

Run the two commands separately, not with `&&`: the scanner exits 1 when a banned structure is found and
the report is still complete. The worksheet needs the unfiltered JSON.

- **Language routing is per sentence**, by weighed script evidence, so each sentence keeps the rules of its own language; other scripts count as `other` and are left unscanned.
- **Unlisted repetition is measured, not listed.** Normal prose scatters a repeated shape; machine prose runs it at a steady rate. The scanner reports repeated sentences and phrases with their count, density, paragraph spread, and gaps. Candidates only: the agent decides whether each is a term, a quotation, a refrain, or mechanical repetition.
- **The rules see surface structure only.** Implicit reversals, paraphrase, quotation intent, paragraph-level reasoning, and repeated proper nouns need a full read; a zero-hit report does not mean the text is clean.
- **Mechanics, flags, report fields, exit codes, and how to add a rule** are in [scripts/README.md](scripts/README.md).

Keep reports and worksheets out of the article; show the reasoning only when the user asks.
