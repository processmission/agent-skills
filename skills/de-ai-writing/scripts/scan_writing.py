#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Scan Chinese and English prose for AI writing tics; never modify the input."""
import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import statistics
import sys

from writing_rules import LOAD_ERROR, OPENERS, RULES, Rule

SCHEMA_VERSION = 4
# A period ends a sentence unless it closes a decimal or a mid-sentence abbreviation.
# After e.g./i.e./etc. it still ends one when a new sentence clearly starts, otherwise the
# next sentence would merge and every ^-anchored rule would miss it.
SENTENCE_PATTERN = re.compile(
    r".+?(?:[。！？；]+"
    r"|[!?]+"
    r"|(?<!\d)(?<!\be\.g)(?<!\bi\.e)(?<!\betc)\.(?=\s|$)"
    r"|(?<!\d)\.(?=\s+[\"“'‘「]?[A-Z])"
    r"|$)", re.S)
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]")
KANA = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff]")
CJK_PUNCTUATION = "，。、；：！？（）「」『』《》"
ZH_FUNCTION_CHARS = "的了在是与和及对从把被而并且等也就都很更还则其所为以于"


@dataclass(frozen=True)
class Sentence:
    line: int
    end_line: int
    paragraph: int
    text: str
    index: int
    start_offset: int
    end_offset: int
    lang: str


@dataclass(frozen=True)
class Finding:
    rule: str
    label: str
    lang: str
    severity: str
    reason: str
    advice: str
    count: int
    paragraph_count: int
    sentence_density: float
    occurrences: tuple[Sentence, ...]


def _blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group())


def mask_markup(source: str, include_quotes: bool = False) -> str:
    """Blank frontmatter, comments, code, links and optional quotes, keeping line positions."""
    text = source.lstrip("\ufeff")
    text = re.sub(r"\A---[^\S\n]*\n.*?\n---[^\S\n]*(?=\n|$)", _blank, text, flags=re.S)
    text = re.sub(r"<!--.*?-->", _blank, text, flags=re.S)
    lines = text.splitlines(keepends=True)
    fence_char, fence_size = "", 0
    for i, line in enumerate(lines):
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence_char:
            if re.match(r"^ {0,3}" + re.escape(fence_char) + "{" + str(fence_size) + r",}\s*$", line):
                fence_char = ""
            lines[i] = re.sub(r"[^\n]", " ", line)
        elif fence:
            fence_char, fence_size = fence.group(1)[0], len(fence.group(1))
            lines[i] = re.sub(r"[^\n]", " ", line)
        elif (not include_quotes and re.match(r"^\s*>", line)) or re.match(r"^\s*\[[^\]]+\]:\s*\S", line):
            lines[i] = re.sub(r"[^\n]", " ", line)
    text = "".join(lines)
    text = re.sub(r"(`+)([^`]*?)\1", _blank, text)
    text = re.sub(r"!?\[([^\]\n]*)\]\([^\n)]*\)",
                  lambda m: " " * (m.start(1) - m.start()) + m.group(1)
                  + " " * (m.end() - m.end(1)), text)
    text = re.sub(r"https?://[^\s<>]+", _blank, text)
    if not include_quotes:
        for pattern in (r"“[^”]*”", r"「[^」]*」", r"『[^』]*』", r'"[^"\n]*"'):
            text = re.sub(pattern, _blank, text)
    return text


def sentence_lang(text: str) -> str | None:
    """Classify by script evidence, not by raw word counts.

    A Han character scores 1, a full-width punctuation mark inside the sentence 2, a Han function
    character 1 extra, and a Latin word 1; a sentence is Chinese only when that score is strictly
    higher. Weighing internal punctuation and function characters keeps a Chinese sentence Chinese
    even when it lists many Latin product names, while one quoted Chinese term inside an English
    sentence does not flip it. Kana-heavy text is reported as "other" and left unscanned, because
    the library only holds Chinese and English rules.
    """
    han = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))
    kana = len(KANA.findall(text))
    if kana and kana >= han:
        return "other"
    if not han and not latin:
        return None
    if not latin:
        return "zh"
    body = text.rstrip("。！？；，、：")
    zh_evidence = (han
                   + 2 * sum(char in CJK_PUNCTUATION for char in body)
                   + sum(char in ZH_FUNCTION_CHARS for char in text))
    return "zh" if zh_evidence > latin else "en"


def prose_sentences(source: str, include_quotes: bool = False) -> list[Sentence]:
    """Segment prose while keeping source line positions.

    Blank lines, headings, and list items are paragraph boundaries. Wrapped prose
    lines remain one paragraph. This is a bounded Markdown reader, not CommonMark.
    """
    text = mask_markup(source, include_quotes)
    # Drop formatting markers without shifting line numbers.
    text = re.sub(r"^(\s*)\*(?=\s)", r"\1-", text, flags=re.M)
    text = re.sub(r"[*_~]", " ", text)
    line_offsets = [0]
    for match in re.finditer("\n", text):
        line_offsets.append(match.end())
    result: list[Sentence] = []
    buffer: list[tuple[int, str]] = []
    paragraph = 0

    def flush() -> None:
        nonlocal paragraph
        if not buffer:
            return
        block = "".join(part for _, part in buffer)
        if not block.strip():
            buffer.clear()
            return
        paragraph += 1
        for match in re.finditer(SENTENCE_PATTERN, block):
            raw = match.group()
            if not re.search(r"[\w\u4e00-\u9fff]", raw):
                continue
            start = match.start() + len(raw) - len(raw.lstrip())
            end = match.end() - len(raw) + len(raw.rstrip())
            stripped = raw.strip().replace("\n", " ").replace("\r", " ")
            lang = sentence_lang(stripped)
            if lang is None:
                continue
            result.append(Sentence(
                buffer[0][0] + block[:start].count("\n"),
                buffer[0][0] + block[:end].count("\n"), paragraph,
                stripped, len(result) + 1,
                line_offsets[buffer[0][0] - 1] + start,
                line_offsets[buffer[0][0] - 1] + end, lang,
            ))
        buffer.clear()

    for number, line in enumerate(text.splitlines(keepends=True), 1):
        if not line.strip() or re.match(r"^\s*(?:[-:| ]{3,}|={3,})\s*$", line):
            flush()
            continue
        structured = re.match(r"^\s*(?:#{1,6}\s+|[-+]\s+|\d+[.)]\s+|>\s*|\|)", line)
        if structured:
            flush()
            prefix = re.match(r"^\s*(?:#{1,6}\s+|[-+]\s+|\d+[.)]\s+|>\s*)", line)
            if prefix:
                line = " " * prefix.end() + line[prefix.end():]
            buffer.append((number, line))
            flush()
        else:
            buffer.append((number, line))
    flush()
    return result


def _question_heading(heading: str) -> bool:
    """A heading that asks instead of stating: English wh-openers, a trailing question mark, or a
    Chinese question word anywhere in the heading.

    Headings are the one place a document-wide structural tell can be measured without flooding the
    report, which is why this is a metric rather than a rule: as a sentence rule it fired on 21
    ordinary Chinese sentences in a single article.
    """
    if re.match(r"(?i)^(?:where|what|why|how|when)\s+(?:the|we|it|they|you|this|that)\b", heading):
        return True
    if heading.rstrip().endswith(("？", "?")):
        return True
    return bool(re.search(r"(?:为什么|为何|如何|怎么|怎样|哪里|何处|什么是|是什么|哪些|是否|多少)", heading))


def _title_case(heading: str) -> bool:
    words = [word for word in re.findall(r"[A-Za-z][A-Za-z'-]*", heading) if len(word) > 3]
    if len(words) < 3:
        return False
    return sum(word[0].isupper() for word in words) / len(words) >= 0.6


def style_metrics(source: str, prose_chars: int) -> dict:
    """Formatting evidence on the masked source; counts inform review, they do not decide.

    Quotations stay in scope so curly quotes can be counted at all; the denominator is the
    report's prose_chars, which does exclude them, so every per-1000 figure shares one unit.
    """
    text = mask_markup(source, include_quotes=True)
    headings = re.findall(r"^#{1,6}[ \t]+(.+?)[ \t]*$", text, re.M)
    counters = {
        "em_dash": len(re.findall(r"[—–]", text)),
        "bold_span": len(re.findall(r"\*\*[^*\n]+\*\*", text)),
        "emoji": len(EMOJI.findall(text)),
        "curly_quote": len(re.findall(r"[“”‘’«»]", text)),
        "inline_header_bullet": len(re.findall(r"^[ \t]*[-*+][ \t]+\*\*[^*\n]+\*\*[ \t]*:", text, re.M)),
        "title_case_heading": sum(1 for heading in headings if _title_case(heading)),
        "list_item": len(re.findall(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\S", text, re.M)),
        "triple_list": len(re.findall(
            r"\b[A-Za-z][\w'-]*(?:[ \t]+[\w'-]+){0,2},[ \t]+[A-Za-z][\w'-]*(?:[ \t]+[\w'-]+){0,2}"
            r",?[ \t]+and[ \t]+", text)),
        "em_dash_spaced": len(re.findall(r"(?<=\S)[ \u00a0][—–][ \u00a0](?=\S)", text)),
        "quotation_mark": len(re.findall(r'["“”]', text)),
        "thematic_break": len(re.findall(r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$", text, re.M)),
        "wh_heading": sum(1 for heading in headings if _question_heading(heading)),
        "ordinal_heading": sum(1 for heading in headings
                               if re.match(r"^(?:[一二三四五六七八九十]+[、.．]|\d+[、.．)]"
                                           r"|第[一二三四五六七八九十\d]+[步部分点])", heading)),
    }
    metrics = {"prose_chars": prose_chars}
    for key, count in counters.items():
        metrics[key] = {"count": count,
                        "per_1000_prose_chars": round(count * 1000 / max(prose_chars, 1), 3)}
    return metrics


def rhythm_metrics(sentences: list[Sentence]) -> dict:
    """Sentence-length spread per language; uniform rhythm is evidence, never a verdict."""
    result = {}
    for lang in ("en", "zh"):
        lengths = [len(sentence.text) for sentence in sentences if sentence.lang == lang]
        if len(lengths) < 3:
            continue
        mean = statistics.fmean(lengths)
        stdev = statistics.stdev(lengths)
        result[lang] = {
            "sentences": len(lengths),
            "mean_chars": round(mean, 1),
            "stdev_chars": round(stdev, 1),
            "variation": round(stdev / mean, 3) if mean else None,
            "share_within_10_percent": round(
                sum(1 for length in lengths if abs(length - mean) <= 0.1 * mean) / len(lengths), 3),
            "shortest_chars": min(lengths),
            "longest_chars": max(lengths),
        }
    return result


EN_STOPWORDS = frozenset(
    "a an the and or but if then than that this these those it its is are was were be been being of "
    "to in on at by for with from as not no do does did have has had will would can could may might "
    "should must we you they he she i there here".split())
GRAM_SIZES = {"zh": (4, 5, 6), "en": (3, 4, 5)}
GRAM_UNITS = {"zh": "chars", "en": "words"}


def _grams(sentence: Sentence) -> list[tuple[str, int, int]]:
    """Candidate fixed phrases: Han-character n-grams, or word n-grams holding a content word."""
    found: list[tuple[str, int, int]] = []
    if sentence.lang == "zh":
        for run in re.finditer(r"[\u4e00-\u9fff]{4,}", sentence.text):
            text = run.group()
            for size in GRAM_SIZES["zh"]:
                for offset in range(len(text) - size + 1):
                    found.append((text[offset:offset + size],
                                  run.start() + offset, run.start() + offset + size))
        return found
    words = [(match.group().lower(), match.start(), match.end())
             for match in re.finditer(r"[A-Za-z][A-Za-z'-]*", sentence.text)]
    for size in GRAM_SIZES["en"]:
        for offset in range(len(words) - size + 1):
            window = words[offset:offset + size]
            if all(word[0] in EN_STOPWORDS for word in window):
                continue
            found.append((" ".join(word[0] for word in window), window[0][1], window[-1][2]))
    return found


def _contains(gram: str, longer: str, lang: str) -> bool:
    return f" {gram} " in f" {longer} " if lang == "en" else gram in longer


def _maximal(grams: dict[str, list[tuple[int, int, int]]], lang: str,
             taken: dict[int, list[tuple[int, int]]] | None = None) -> dict[str, list[tuple[int, int, int]]]:
    """Describe each repeated phrase once: drop shifted windows and sub-phrases of a kept phrase.

    Candidates are ranked by frequency times length, so the full common form wins. A candidate is
    dropped when most of its occurrences are already covered by a kept one, or when it sits inside a
    kept phrase that repeats at least as often. Spans already claimed by a repeated sentence arrive
    pre-seeded in `taken`, so a verbatim repeat is not reported again as dozens of windows.
    """
    taken = defaultdict(list) if taken is None else taken
    kept: dict[str, list[tuple[int, int, int]]] = {}
    ranked = sorted(grams, key=lambda gram: (-(len(grams[gram]) * len(gram)), -len(gram), gram))
    for gram in ranked:
        hits = grams[gram]
        covered = 0
        for index, start, end in hits:
            length = end - start
            if any(min(end, stop) - max(start, begin) >= 0.6 * length
                   for begin, stop in taken.get(index, ())):
                covered += 1
        if covered * 2 > len(hits):
            continue
        if any(len(other) >= len(hits) and _contains(gram, longer, lang)
               for longer, other in kept.items()):
            continue
        kept[gram] = hits
        for index, start, end in hits:
            taken[index].append((start, end))
    return kept


def source_words_between(sentences: list[Sentence], start: int, end: int) -> int:
    """English words between two occurrences, so gaps are reported in words rather than characters."""
    if end <= start:
        return 0
    text = " ".join(sentence.text for sentence in sentences
                    if sentence.end_offset > start and sentence.start_offset < end)
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))


def _normalise(text: str) -> str:
    return re.sub(r"[\s。！？!?；;，,、]+$", "", re.sub(r"\s+", " ", text)).strip()


def _pattern_record(pattern: str, kind: str, lang: str, hits: list[tuple[int, int, int]],
                    by_index: dict[int, Sentence], sentences: list[Sentence],
                    prose_prefix: list[int]) -> dict:
    """One candidate pattern: where it occurs, how tightly it repeats, and how far apart."""
    occurrences = []
    for index, start, end in hits:
        sentence = by_index[index]
        absolute_start = sentence.start_offset + start
        absolute_end = sentence.start_offset + end
        occurrences.append({
            "line": sentence.line, "paragraph": sentence.paragraph, "sentence": index,
            "start_offset": absolute_start, "end_offset": absolute_end,
            "prose_start": prose_prefix[absolute_start], "prose_end": prose_prefix[absolute_end],
            "match": pattern, "context": sentence.text,
        })
    gaps = []
    for previous, current in zip(occurrences, occurrences[1:]):
        between = (source_words_between(sentences, previous["end_offset"], current["start_offset"])
                   if lang == "en" else current["prose_start"] - previous["prose_end"])
        gaps.append({
            "units_between": between,
            "prose_chars_between": current["prose_start"] - previous["prose_end"],
            "sentences_between": max(0, current["sentence"] - previous["sentence"] - 1),
            "paragraph_distance": current["paragraph"] - previous["paragraph"],
            "same_sentence": current["sentence"] == previous["sentence"],
            "same_paragraph": current["paragraph"] == previous["paragraph"],
        })
    local = [gap["units_between"] for gap in gaps]
    return {
        "pattern": pattern, "kind": kind, "lang": lang, "units": GRAM_UNITS[lang],
        "count": len(occurrences), "sentence_count": len({index for index, _, _ in hits}),
        "paragraph_count": len({item["paragraph"] for item in occurrences}),
        "sentence_share": round(len({index for index, _, _ in hits}) / max(len(sentences), 1), 4),
        "uses_per_1000_prose_chars": round(
            len(occurrences) * 1000 / max(prose_prefix[-1], 1), 3),
        "paragraph_counts": {str(p): sum(1 for item in occurrences if item["paragraph"] == p)
                             for p in sorted({item["paragraph"] for item in occurrences})},
        "same_paragraph_pairs": sum(1 for gap in gaps if gap["same_paragraph"]),
        "cross_paragraph_pairs": sum(1 for gap in gaps if not gap["same_paragraph"]),
        "gap_summary": {"min_units": min(local, default=None),
                        "median_units": statistics.median(local) if local else None,
                        "max_units": max(local, default=None)},
        "occurrences": occurrences, "adjacent_gaps": gaps,
    }


def discover_patterns(sentences: list[Sentence], prose_prefix: list[int], *,
                      min_uses: int = 3) -> tuple[list[dict], dict]:
    """Find fixed phrases the rule tables do not list, and measure how mechanically they repeat.

    Human prose scatters a repeated shape; machine prose runs it at a steady rate. Two kinds of
    candidate are reported: whole sentences repeated verbatim, and repeated phrases anywhere in a
    sentence (Han-character n-grams, or English word n-grams holding a content word). Each carries
    its count, density, paragraph spread, and the gap to its previous use, measured in words for
    English and characters for Chinese. Phrases the rule tables already cover are not repeated here.
    """
    patterns: list[dict] = []
    by_language: dict[str, dict] = {}
    by_index = {sentence.index: sentence for sentence in sentences}
    for lang in ("zh", "en"):
        own = [sentence for sentence in sentences if sentence.lang == lang]
        if not own:
            continue
        touched: set[int] = set()
        gap_units: list[int] = []
        taken: dict[int, list[tuple[int, int]]] = defaultdict(list)

        # 1. Sentences repeated verbatim: the strongest mechanical-repetition signal.
        buckets: dict[str, list[Sentence]] = {}
        for sentence in own:
            key = _normalise(sentence.text)
            if len(key) >= 8:
                buckets.setdefault(key, []).append(sentence)
        for key, group in buckets.items():
            if len(group) < min_uses:
                continue
            hits = [(sentence.index, 0, len(sentence.text)) for sentence in group]
            record = _pattern_record(key, "sentence", lang, hits, by_index, sentences, prose_prefix)
            patterns.append(record)
            touched.update(index for index, _, _ in hits)
            gap_units.extend(gap["units_between"] for gap in record["adjacent_gaps"])
            for index, start, end in hits:
                taken[index].append((start, end))

        # 2. Repeated phrases, minus anything the tables already know and anything inside a repeat.
        grams: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
        for sentence in own:
            for gram, start, end in _grams(sentence):
                grams[gram].append((sentence.index, start, end))
        known = [rule for rule in RULES if rule.lang == lang]
        frequent = {gram: hits for gram, hits in grams.items()
                    if len(hits) >= min_uses and not any(rule.matches(gram) for rule in known)}
        for gram, hits in _maximal(frequent, lang, taken).items():
            record = _pattern_record(gram, "phrase", lang, hits, by_index, sentences, prose_prefix)
            patterns.append(record)
            touched.update(index for index, _, _ in hits)
            gap_units.extend(gap["units_between"] for gap in record["adjacent_gaps"])

        summary = {"patterns": sum(1 for item in patterns if item["lang"] == lang),
                   "sentences_touched": len(touched), "units": GRAM_UNITS[lang]}
        summary["median_gap_units"] = statistics.median(gap_units) if gap_units else None
        by_language[lang] = summary

    patterns.sort(key=lambda item: (item["kind"] != "sentence", -item["count"], item["pattern"]))
    touched_all = {occurrence["sentence"] for item in patterns for occurrence in item["occurrences"]}
    pairs = sum(item["same_paragraph_pairs"] + item["cross_paragraph_pairs"] for item in patterns)
    same = sum(item["same_paragraph_pairs"] for item in patterns)
    repetition = {
        "min_uses": min_uses,
        "patterns": len(patterns),
        "sentence_repeats": sum(1 for item in patterns if item["kind"] == "sentence"),
        "phrase_repeats": sum(1 for item in patterns if item["kind"] == "phrase"),
        "sentences_touched": len(touched_all),
        "sentence_share": round(len(touched_all) / max(len(sentences), 1), 4),
        "same_paragraph_pair_share": round(same / max(pairs, 1), 4),
        "by_language": by_language,
        "units": GRAM_UNITS,
    }
    return patterns, repetition


def analyze(source: str, *, max_uses: int = 2, opener_density: float = 0.25,
            include_quotes: bool = False, pattern_uses: int = 3) -> dict:
    source = source.lstrip("\ufeff")
    sentences = prose_sentences(source, include_quotes)
    findings: list[Finding] = []
    stats = []
    # The documented denominator for every per-1000 figure: non-whitespace characters of the
    # markup-masked source, quotations excluded.
    prose_chars = sum(1 for char in mask_markup(source) if not char.isspace())
    # Positions and gap distances are tracked on the scanned sentences themselves.
    visible_prefix = [0] * (len(source) + 1)
    for sentence in sentences:
        for offset, char in enumerate(sentence.text, sentence.start_offset):
            visible_prefix[offset + 1] = int(not char.isspace())
    for i in range(1, len(visible_prefix)):
        visible_prefix[i] += visible_prefix[i - 1]

    def locations(rule: Rule) -> list[dict]:
        result = []
        for sentence in sentences:
            for start, end in rule.spans(sentence.text):
                absolute_start = sentence.start_offset + start
                absolute_end = sentence.start_offset + end
                result.append({
                    "line": source[:absolute_start].count("\n") + 1,
                    "end_line": source[:absolute_end].count("\n") + 1,
                    "paragraph": sentence.paragraph, "sentence": sentence.index,
                    "start_offset": absolute_start, "end_offset": absolute_end,
                    "prose_start": visible_prefix[absolute_start],
                    "prose_end": visible_prefix[absolute_end],
                    "match": sentence.text[start:end], "context": sentence.text,
                })
        return result

    def record(key: str, label: str, lang: str, severity: str, hits: list[Sentence],
               reason: str, advice: str) -> None:
        findings.append(Finding(key, label, lang, severity, reason, advice, len(hits),
                                len({s.paragraph for s in hits}),
                                round(len(hits) / max(len(sentences), 1), 4), tuple(hits)))

    def summarize(rule: Rule, hits: list[Sentence]) -> int:
        occurrences = locations(rule)
        gaps = []
        for previous, current in zip(occurrences, occurrences[1:]):
            gaps.append({
                "from_offset": previous["start_offset"], "to_offset": current["start_offset"],
                "source_chars_between": current["start_offset"] - previous["end_offset"],
                "prose_chars_between": current["prose_start"] - previous["prose_end"],
                "prose_start_distance": current["prose_start"] - previous["prose_start"],
                "sentences_between": max(0, current["sentence"] - previous["sentence"] - 1),
                "paragraph_distance": current["paragraph"] - previous["paragraph"],
                "same_sentence": current["sentence"] == previous["sentence"],
                "same_paragraph": current["paragraph"] == previous["paragraph"],
            })
        paragraphs = len({s.paragraph for s in hits})
        paragraph_counts = {}
        for item in occurrences:
            key = str(item["paragraph"])
            paragraph_counts[key] = paragraph_counts.get(key, 0) + 1
        stats.append({"rule": rule.key, "label": rule.label, "kind": rule.kind, "lang": rule.lang,
                      "count": len(occurrences), "sentence_count": len(hits),
                      "paragraph_count": paragraphs,
                      "sentence_density": round(len(hits) / len(sentences), 4),
                      "uses_per_1000_prose_chars": round(len(occurrences) * 1000 / max(prose_chars, 1), 3),
                      "paragraph_counts": paragraph_counts,
                      "gap_summary": {"min_prose_chars": min((g["prose_chars_between"] for g in gaps), default=None),
                                      "max_prose_chars": max((g["prose_chars_between"] for g in gaps), default=None),
                                      "median_prose_chars": statistics.median(g["prose_chars_between"] for g in gaps) if gaps else None},
                      "occurrences": occurrences, "adjacent_gaps": gaps})
        return len(occurrences)

    for rule in RULES:
        hits = [s for s in sentences if s.lang == rule.lang and rule.matches(s.text)]
        if not hits:
            continue
        count = summarize(rule, hits)
        paragraphs = len({s.paragraph for s in hits})
        if rule.kind in ("ban", "review"):
            record(rule.key, rule.label, rule.lang, "block" if rule.kind == "ban" else "review",
                   hits, "banned structure found" if rule.kind == "ban" else "review against article purpose",
                   rule.advice)
        elif count >= 2:
            record(rule.key, rule.label, rule.lang, "review", hits,
                   f"{count} uses across {paragraphs} paragraph(s); "
                   + (f"above the reference count of {max_uses}, review first" if count > max_uses
                      else "within the reference count, judge from distance and context"),
                   rule.advice)

    for lang, openers in OPENERS.items():
        for key, (label, pattern) in openers.items():
            hits = [s for s in sentences if s.lang == lang and re.search(pattern, s.text, re.IGNORECASE)]
            if hits:
                summarize(Rule(f"{lang}-opener-{key}", label, "family", lang, (pattern,), ""), hits)
            if (len(hits) >= 5 and len({s.paragraph for s in hits}) >= 3
                    and len(hits) / len(sentences) >= opener_density):
                record(f"{lang}-opener-{key}", label, lang, "review", hits,
                       "same-function connective opens sentences at or above the density threshold",
                       "Check whether sentence linkage is too uniform; do not delete connectives mechanically.")

    # Everything the rule tables do not list: discover fixed phrases and measure how they repeat.
    # A discovered pattern is a candidate for the agent, never a verdict.
    patterns, repetition = discover_patterns(sentences, visible_prefix, min_uses=pattern_uses)
    repetition["rule_hit_sentence_share"] = round(
        len({s for finding in findings for s in finding.occurrences}) / max(len(sentences), 1), 4)

    findings.sort(key=lambda f: (f.occurrences[0].line, f.rule))
    languages: dict[str, int] = {}
    for sentence in sentences:
        languages[sentence.lang] = languages.get(sentence.lang, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "method": "Rule-based rhetorical grouping and distribution statistics; not language-model semantics, not AI-authorship detection",
        "settings": {"max_uses": max_uses, "opener_density": opener_density,
                     "pattern_uses": pattern_uses, "include_quotes": include_quotes},
        "summary": {"sentences": len(sentences), "paragraphs": len({s.paragraph for s in sentences}),
                    "prose_chars": prose_chars, "languages": languages,
                    "blocked_groups": sum(f.severity == "block" for f in findings),
                    "review_groups": sum(f.severity == "review" for f in findings)},
        "metrics": style_metrics(source, prose_chars),
        "rhythm": rhythm_metrics(sentences),
        "patterns": patterns,
        "repetition": repetition,
        "families": stats,
        "paragraphs": [{"paragraph": p,
                        "prose_chars": sum(sum(not c.isspace() for c in s.text) for s in sentences if s.paragraph == p),
                        "sentences": [s.index for s in sentences if s.paragraph == p]}
                       for p in sorted({s.paragraph for s in sentences})],
        "sentences": [asdict(s) for s in sentences],
        "findings": [asdict(f) for f in findings],
    }


def format_text(report: dict) -> str:
    summary = report["summary"]
    languages = ", ".join(f"{lang} {count}" for lang, count in sorted(summary["languages"].items()))
    rows = [f"{report['file']}: {summary['sentences']} sentences / {summary['paragraphs']} paragraphs "
            f"({languages or 'no prose'}); {summary['blocked_groups']} banned group(s), "
            f"{summary['review_groups']} review group(s)"]
    for finding in report["findings"]:
        rows.append(f"\n[{finding['severity']}] {finding['rule']} / {finding['label']}: {finding['reason']}")
        rows.append(f"  {finding['sentence_density']:.1%} of sentences; {finding['advice']}")
        for occurrence in finding["occurrences"]:
            rows.append(f"  L{occurrence['line']}-L{occurrence['end_line']} P{occurrence['paragraph']}: "
                        f"{occurrence['text']}")
    if report["families"]:
        rows.append("\nStructure distribution and adjacent distances (including single uses):")
        for family in report["families"]:
            rows.append(f"  {family['rule']}: {family['count']} uses / {family['paragraph_count']} paragraph(s) / "
                        f"{family['uses_per_1000_prose_chars']} per 1000 prose chars")
            for gap in family["adjacent_gaps"]:
                rows.append(f"    gap {gap['prose_chars_between']} prose chars, "
                            f"{gap['sentences_between']} whole sentence(s); paragraph distance "
                            f"{gap['paragraph_distance']}; same paragraph={gap['same_paragraph']}")
    shown = {key: value for key, value in report["metrics"].items()
             if isinstance(value, dict) and value["count"]}
    if shown:
        rows.append("\nFormatting metrics (count / per 1000 prose chars):")
        for key, value in shown.items():
            rows.append(f"  {key}: {value['count']} / {value['per_1000_prose_chars']}")
    if report.get("rhythm"):
        rows.append("\nSentence rhythm (chars per sentence; variation = stdev / mean):")
        for lang, values in report["rhythm"].items():
            rows.append(f"  {lang}: {values['sentences']} sentences, mean {values['mean_chars']}, "
                        f"variation {values['variation']}, "
                        f"{values['share_within_10_percent']:.0%} within 10% of the mean, "
                        f"range {values['shortest_chars']}–{values['longest_chars']}")
    if report.get("patterns"):
        repetition = report.get("repetition", {})
        rows.append(f"\nFixed phrases the rule tables do not list "
                    f"({repetition.get('patterns', 0)} pattern(s); candidate tics, agent decides):")
        for item in report["patterns"]:
            gap = item["gap_summary"]
            rows.append(f"  [{item['lang']}] {item['pattern']}: {item['count']} uses / "
                        f"{item['paragraph_count']} paragraph(s) / "
                        f"{item['uses_per_1000_prose_chars']} per 1000 prose chars; "
                        f"same-paragraph pairs {item['same_paragraph_pairs']}/"
                        f"{item['same_paragraph_pairs'] + item['cross_paragraph_pairs']}; gap "
                        f"{gap['min_units']}–{gap['max_units']} {item['units']} "
                        f"(median {gap['median_units']})")
            for occurrence in item["occurrences"][:3]:
                rows.append(f"    L{occurrence['line']} P{occurrence['paragraph']}: "
                            f"{occurrence['context'][:110]}")
    if report.get("repetition"):
        repetition = report["repetition"]
        rows.append(f"\nRepetition profile: {repetition['sentence_share']:.0%} of sentences carry a "
                    f"discovered pattern; {repetition['same_paragraph_pair_share']:.0%} of adjacent "
                    f"repeats sit in one paragraph; rule findings touch "
                    f"{repetition.get('rule_hit_sentence_share', 0):.0%} of sentences.")
    rows.append("\nRule scanning and phrase discovery cannot find every synonymous pattern; read the "
                "full text. Input unchanged.")
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="UTF-8 Markdown/text file; - reads stdin")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--only", choices=("all", "block", "review"), default="all",
                        help="Filter displayed findings; does not change exit status")
    parser.add_argument("--max-uses", type=int, default=2,
                        help="Reference frequency for review priority, not automatic rejection (default: 2)")
    parser.add_argument("--opener-density", type=float, default=0.25)
    parser.add_argument("--pattern-uses", type=int, default=3,
                        help="Occurrences before a phrase the rule tables do not list is reported as a "
                             "candidate pattern (default: 3)")
    parser.add_argument("--include-quotes", action="store_true",
                        help="Also scan quoted spans and blockquotes")
    args = parser.parse_args()
    if LOAD_ERROR:
        parser.error(f"rule tables: {LOAD_ERROR}")
    if args.max_uses < 1 or args.pattern_uses < 2 or not 0 < args.opener_density <= 1:
        parser.error("--max-uses must be >= 1; --pattern-uses must be >= 2; "
                     "--opener-density must be in (0, 1]")
    try:
        source = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    report = analyze(source, max_uses=args.max_uses, opener_density=args.opener_density,
                     include_quotes=args.include_quotes, pattern_uses=args.pattern_uses)
    report["file"] = args.file
    report["display_filter"] = args.only
    if args.only != "all":
        report["findings"] = [f for f in report["findings"] if f["severity"] == args.only]
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text(report), end="")
    return 1 if report["summary"]["blocked_groups"] else 0


if __name__ == "__main__":
    sys.exit(main())
