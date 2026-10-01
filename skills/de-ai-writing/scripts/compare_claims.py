# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Compare a revision against its original and flag every change that needs a reason.

The skill may delete meta text, reorder, and remove patterns a rule row names. It may not paraphrase
the author's propositions: modality, scope, quantifiers, subject, conditions, and negation polarity
stay as written. This tool is the guard for that rule. For each sentence that changed it reports:

- `number`      — the numeric content differs
- `identifier`  — a backticked or Latin identifier was added, removed, or swapped
- `modality`    — must / must not / should / may / can / usually / as much as possible and their Chinese
                  equivalents differ
- `negation`    — the number of negations differs
- `polarity`    — negations are present but their count is unchanged, so the sentence was rewritten
                  around them; check that the same thing is still negated
- `quantifier`  — all / some / any / exactly one / only and their Chinese equivalents differ
- `punctuation` — only punctuation or spacing changed
- `unlicensed`  — the rewrite removed no pattern the tables flag, so nothing licensed it: justify it as
                  meta text, or revert it

Deleted and added sentences are listed separately. Additions always need justification, because the
skill never invents text; deletions need a reason: meta text, or the key of the rule that fired.

Sentences come from the scanner's own segmentation, but the text is sliced out of the raw source, so
quoting and inline code stay visible in the report. Blockquotes and quoted spans are compared too,
since status and scope lines often sit there.

Exit codes: `0` nothing to justify, `1` at least one change needs a reason, `2` usage or input error.
The inputs are never modified.
"""
import argparse
from difflib import SequenceMatcher
import json
import pathlib
import re
import sys

import scan_writing
import writing_rules

SCHEMA_VERSION = 1
SIMILARITY_DEFAULT = 0.55

NEGATION = {
    "zh": re.compile(r"(?:不|未|非|无|没)[\u4e00-\u9fff]"),
    "en": re.compile(r"\b(?:not|no|never|without|cannot|n't)\b", re.IGNORECASE),
}
MODALITY = {
    "zh": re.compile(r"必须|不得|不应|应当|应该|可以|可能|尽量|通常|一般|至少|最多|恰好|要求|允许|禁止"),
    "en": re.compile(r"\b(?:must|must\s+not|should|may|can|cannot|may\s+not|usually|as\s+much\s+as\s+possible"
                     r"|at\s+least|at\s+most|exactly|only|required?|allowed?)\b", re.IGNORECASE),
}
QUANTIFIER = {
    "zh": re.compile(r"所有|全部|任何|每个|每一个|部分|某些|唯一|若干|只|仅"),
    "en": re.compile(r"\b(?:all|every|each|any|some|only|exactly|none)\b", re.IGNORECASE),
}
# A digit run that starts an identifier (ARM64, GPT6) is not a number; a run followed by a unit
# (128 tokens, 3.25T, 1M) is.
NUMBER = re.compile(r"(?<![A-Za-z0-9])\d+(?:\.\d+)?")
IDENTIFIER = re.compile(r"`([^`\n]+)`|\b([A-Za-z_][A-Za-z0-9_]*[._][A-Za-z0-9_.]*|[A-Z][A-Z0-9_]{2,})\b")
PUNCTUATION = re.compile(r"[\s\W_]+", re.UNICODE)


def _sentences(source: str) -> list[dict]:
    """Segment with the scanner, then slice the raw text so code spans and quotes survive.

    The scanner works on a masked copy where code spans, links, and quoted text become blanks, so a
    sentence can start after its own inline code. Each span is widened to the line boundaries to pull
    that material back in.
    """
    plain = source.lstrip("\ufeff")
    masked = scan_writing.mask_markup(plain, include_quotes=True)
    rows = []
    for sentence in scan_writing.prose_sentences(plain, include_quotes=True):
        start, end = sentence.start_offset, sentence.end_offset
        line_start = masked.rfind("\n", 0, start) + 1
        while start > line_start and masked[start - 1] == " ":
            start -= 1
        line_end = masked.find("\n", end)
        line_end = len(masked) if line_end == -1 else line_end
        while end < line_end and masked[end] == " ":
            end += 1
        rows.append({"line": sentence.line, "paragraph": sentence.paragraph, "lang": sentence.lang,
                     "text": plain[start:end].strip()})
    return rows


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _words(text: str) -> str:
    return PUNCTUATION.sub("", text)


def _count(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall(text))


def _identifiers(text: str) -> set[str]:
    return {(backticked or bare).strip() for backticked, bare in IDENTIFIER.findall(text) if backticked or bare}


def _rule_keys(text: str, lang: str) -> set[str]:
    """Every table row that matches this sentence."""
    return {rule.key for rule in writing_rules.RULES if rule.lang == lang and rule.matches(text)}


def _flags(before: str, after: str, lang: str) -> list[str]:
    if _norm(before) == _norm(after):
        return []
    if _words(before) == _words(after):
        return ["punctuation"]
    flags = []
    if sorted(NUMBER.findall(before)) != sorted(NUMBER.findall(after)):
        flags.append("number")
    if _identifiers(before) != _identifiers(after):
        flags.append("identifier")
    for name, table in (("modality", MODALITY), ("quantifier", QUANTIFIER)):
        pattern = table.get(lang) or table["en"]
        if sorted(pattern.findall(before)) != sorted(pattern.findall(after)):
            flags.append(name)
    negation = NEGATION.get(lang) or NEGATION["en"]
    before_negation, after_negation = _count(negation, before), _count(negation, after)
    if before_negation != after_negation:
        flags.append("negation")
    elif before_negation and after_negation:
        flags.append("polarity")
    # A row matching the sentence does not license editing it: only a row that stopped matching does.
    if not (_rule_keys(before, lang) - _rule_keys(after, lang)):
        flags.append("unlicensed")
    return flags


def _pair(original: list[dict], revised: list[dict], similarity: float) -> tuple[list, list, list]:
    """Match by exact text first, then by similarity; leftovers are deletions and additions."""
    pairs: list[tuple[dict, dict, list[str]]] = []
    taken_original: set[int] = set()
    taken_revised: set[int] = set()
    for index, old in enumerate(original):
        for other, new in enumerate(revised):
            if other in taken_revised:
                continue
            if _norm(old["text"]) == _norm(new["text"]):
                pairs.append((old, new, []))
                taken_original.add(index)
                taken_revised.add(other)
                break
    remaining_original = [i for i in range(len(original)) if i not in taken_original]
    remaining_revised = [i for i in range(len(revised)) if i not in taken_revised]
    scored = sorted(((SequenceMatcher(None, _norm(original[i]["text"]), _norm(revised[j]["text"])).ratio(), i, j)
                     for i in remaining_original for j in remaining_revised), key=lambda item: -item[0])
    for ratio, i, j in scored:
        if ratio < similarity or i in taken_original or j in taken_revised:
            continue
        taken_original.add(i)
        taken_revised.add(j)
        old, new = original[i], revised[j]
        pairs.append((old, new, _flags(old["text"], new["text"], old["lang"])))
    pairs.sort(key=lambda item: (item[0]["paragraph"], item[0]["line"]))
    deleted = [original[i] for i in range(len(original)) if i not in taken_original]
    added = [revised[j] for j in range(len(revised)) if j not in taken_revised]
    return pairs, deleted, added


def compare(original_source: str, revised_source: str, *, similarity: float = SIMILARITY_DEFAULT) -> dict:
    original = _sentences(original_source)
    revised = _sentences(revised_source)
    pairs, deleted, added = _pair(original, revised, similarity)
    changed = []
    for old, new, flags in pairs:
        if not flags:
            continue
        removed = sorted(_rule_keys(old["text"], old["lang"]) - _rule_keys(new["text"], new["lang"]))
        changed.append({"before": old, "after": new, "flags": flags, "rules_removed": removed})
    needs_reason = [c for c in changed if set(c["flags"]) - {"punctuation"}]
    return {
        "schema": SCHEMA_VERSION,
        "settings": {"similarity": similarity},
        "summary": {
            "sentences_original": len(original),
            "sentences_revised": len(revised),
            "unchanged": len(pairs) - len(changed),
            "changed": len(changed),
            "deleted": len(deleted),
            "added": len(added),
            "needs_reason": len(needs_reason) + len(deleted) + len(added),
            "exit_code": 1 if needs_reason or deleted or added else 0,
        },
        "changed": changed,
        "deleted": deleted,
        "added": added,
    }


def format_text(report: dict) -> str:
    summary = report["summary"]
    lines = [f"claim diff (schema-v{report['schema']}): {summary['unchanged']} unchanged, "
             f"{summary['changed']} changed, {summary['deleted']} deleted, {summary['added']} added"]
    if report["changed"]:
        lines += ["", "Changed sentences (each flag needs a reason: a rule key, or meta text):"]
        for item in report["changed"]:
            rule = f" removed={','.join(item['rules_removed'])}" if item["rules_removed"] else ""
            lines.append(f"  L{item['before']['line']} [{' '.join(item['flags'])}]{rule}")
            lines.append(f"    - {item['before']['text']}")
            lines.append(f"    + {item['after']['text']}")
    for name in ("deleted", "added"):
        if report[name]:
            lines += ["", f"{name.capitalize()} sentences (justify each: meta text, a rule key, or revert):"]
            lines += [f"  L{item['line']} {item['text']}" for item in report[name]]
    if not summary["needs_reason"]:
        lines += ["", "Nothing to justify: no claim-level change, no addition, no deletion."]
    return "\n".join(lines) + "\n"


def _read(path: str, cache: list[str]) -> str:
    if path == "-":
        if not cache:
            cache.append(sys.stdin.read())
        return cache[0]
    return pathlib.Path(path).read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff a revision against its original and flag "
                                                 "claim-level changes.")
    parser.add_argument("original", help="the untouched original, or - for stdin")
    parser.add_argument("revised", help="the revision, or - for stdin")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--similarity", type=float, default=SIMILARITY_DEFAULT,
                        help=f"sentence pairing threshold (default {SIMILARITY_DEFAULT})")
    arguments = parser.parse_args()
    if arguments.original == "-" and arguments.revised == "-":
        parser.error("only one input can come from stdin")
    if writing_rules.LOAD_ERROR:
        parser.error(f"rule tables failed to load: {writing_rules.LOAD_ERROR}")
    cache: list[str] = []
    try:
        original = _read(arguments.original, cache)
        revised = _read(arguments.revised, cache)
    except OSError as error:
        parser.error(str(error))
    report = compare(original, revised, similarity=arguments.similarity)
    if arguments.format == "json":
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_text(report))
    return report["summary"]["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
