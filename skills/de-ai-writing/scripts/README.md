<!-- SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission -->
<!-- SPDX-License-Identifier: MIT -->

# Script reference

Mechanics for the two scan tools. The agent needs this when it runs them or reads their output; the
judgment rules stay in [SKILL.md](../SKILL.md), and the patterns stay in
[../references/rules-zh.md](../references/rules-zh.md) and
[../references/rules-en.md](../references/rules-en.md).

## Files

| File | Role |
| --- | --- |
| `writing_rules.py` | Parses and compiles the two rule tables; a broken row is reported as file, line, and key |
| `scan_writing.py` | Marks the text: known tics from the tables, plus repeated shapes the tables do not list |
| `render_review.py` | JSON report → per-group worksheet with a decision column |
| `compare_claims.py` | Diff a revision against its original and flag claim-level changes |

Standard library only, Python 3.10 or newer, no network and no model. Both entry points read the input
and write to stdout: there is no in-place edit, replacement, or overwrite option.

## Commands

```bash
SKILL_DIR=/path/to/de-ai-writing
python3 "$SKILL_DIR/scripts/scan_writing.py" article.md --format json > article.scan.json
python3 "$SKILL_DIR/scripts/render_review.py" article.scan.json > article.review.md
```

Run the two commands separately, not with `&&`: the scanner exits 1 when a banned structure is found and
the report is still complete. The worksheet needs the unfiltered JSON.

## Claim diff

`compare_claims.py` compares a revision with its original, so a tightening pass cannot quietly rewrite
the author's propositions (SKILL.md 1.6).

```bash
python3 "$SKILL_DIR/scripts/compare_claims.py" article.md article.de-ai.md
```

Flags, per changed sentence: `number`, `identifier`, `modality` (must / must not / should / may / can /
usually / as much as possible and their Chinese equivalents), `negation` (the count changed), `polarity`
(negations kept but the sentence was rewritten around them), `quantifier`, `punctuation`, and
`unlicensed`. A row matching a sentence does not license editing it; only a row that stopped matching
does, which is why a rewrite that removes no flagged pattern is reported as `unlicensed` and has to be
justified as meta text or reverted. Deleted and added sentences are listed separately, and additions
always need a reason because the skill never invents text.

Exit `1` when anything needs a reason, `0` when nothing does, `2` on a usage or input error. Sentences
come from the scanner's segmentation, but the text is sliced from the raw source, so inline code and
quotes stay visible; blockquotes are compared too, since status and scope lines often sit there.

## Exit codes

`0` no banned structure (review items may remain) · `1` a banned structure was found · `2` input or
argument error, including a rule table that failed to load. Exit status is not a quality score.

## Options

| Flag | Meaning |
| --- | --- |
| `--format text\|json` | Default `text`; `json` for the full report |
| `--max-uses N` | Review priority for repeated families (default 2) |
| `--pattern-uses N` | Occurrences before an unlisted phrase becomes a candidate (default 3, minimum 2) |
| `--opener-density F` | Connective density threshold (default 0.25; a group also needs 5 uses across 3 paragraphs) |
| `--only block\|review` | Display filter; statistics and the exit code do not change |
| `--include-quotes` | Also scan blockquotes and quoted spans |
| `-` | Read from stdin |

## Report fields

- `summary` — sentence, paragraph, and prose-character counts, per-language sentence counts, and blocked
  and review group totals.
- `findings` — one entry per rule that hit: rule key, label, language, severity, reason, advice, and every
  occurrence with line, paragraph, sentence, offsets, matched text, sentence context, and its share of
  sentences.
- `families` — per rule: use count, matching sentences, paragraphs touched, per-paragraph counts, sentence
  share, uses per 1000 prose characters, every occurrence, and the gaps between adjacent uses
  (`prose_chars_between`, `sentences_between`, `paragraph_distance`, `same_sentence`, `same_paragraph`).
- `patterns` and `repetition` — shapes the tables do not list: verbatim repeated sentences and repeated
  phrases (Han n-grams of 4–6 characters, English word n-grams of 3–5 words holding a content word), each
  with count, density, paragraph spread, `same_paragraph_pairs` against `cross_paragraph_pairs`, and gaps
  measured in words for English and characters for Chinese. `repetition` summarises the document. This
  finds repeated *phrases*, not repeated *syntactic habits*: a document that defines everything by
  negation, or that opens every paragraph the same way with different words, shows up in no n-gram and
  needs the read-through.
- `metrics` — formatting counts and densities: `em_dash`, `em_dash_spaced`, `bold_span`, `emoji`,
  `curly_quote`, `inline_header_bullet`, `title_case_heading`, `wh_heading`, `ordinal_heading`,
  `thematic_break`, `list_item`, `triple_list`, `quotation_mark`.
- `rhythm` — per language: sentence-length mean, standard deviation, variation (stdev ÷ mean), the share
  within 10% of the mean, and the shortest and longest sentence.
- `sentences` and `paragraphs` — the structural map the offsets refer to.

## Language routing

Each sentence is classified by weighed script evidence: Han characters, full-width punctuation, and Han
function characters against Latin words. A Chinese sentence keeps Chinese rules even when it lists English
product names, and an English sentence quoting a Chinese phrase keeps the English rules. Sentences
dominated by another script are counted as `other` in `summary.languages` and left unscanned.

## Maintenance

Add a row to the language's rule table: rule key (prefixed `zh-` or `en-`), kind, label, pattern, a probe
sentence, the model family, an evidence key, and the advice. Escape `|` as `\|` inside a cell.

The loader fails, naming file, line, and key, when a pattern does not compile, when a probe does not match
its own pattern, when a row has the wrong number of columns, when a key is missing its language prefix or
its probe, or when no rule loads at all. Every rule must have a probe; the regression suite replays them.

```bash
python3 -S -m unittest discover -s "$SKILL_DIR/tests" -v
```
