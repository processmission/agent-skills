#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Turn a scanner JSON report into an agent review worksheet; stdout only."""
import argparse
import json
from pathlib import Path
import sys

from scan_writing import SCHEMA_VERSION


def cell(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ").replace("\r", " ")


def render(report: dict) -> str:
    alerts = {item["rule"]: item for item in report["findings"]}
    families = [item for item in report["families"] if item["count"] >= 2 or item["rule"] in alerts]
    rows = ["# Structure review worksheet", "", f"Source: {cell(report.get('file', 'stdin'))}", "",
            "Editing worksheet; never merge it into the article. The scanner made no decisions.", "",
            "For each group, check the logical relation, the information gain, and any deliberate local "
            "emphasis. Record keep / rewrite / merge / delete with a concrete reason for every occurrence.", ""]
    for family in families:
        rule = family["rule"]
        rows.extend([f"## {family['label']} ({rule}, {family['lang']})", "",
                     f"{family['count']} uses across {family['paragraph_count']} paragraph(s); "
                     f"{family['sentence_density']:.1%} of sentences, "
                     f"{family['uses_per_1000_prose_chars']} per 1000 prose chars.", ""])
        if rule in alerts:
            rows.extend([f"Scanner note: {alerts[rule]['reason']}. {alerts[rule]['advice']}", ""])
        rows.extend(["| Location / offset | Sentence context | Gap to previous: prose chars / sentences / paragraphs | Decision and reason |",
                     "| --- | --- | --- | --- |"])
        for index, occurrence in enumerate(family["occurrences"]):
            gap = family["adjacent_gaps"][index - 1] if index else None
            distance = (f"{gap['prose_chars_between']} / {gap['sentences_between']} / {gap['paragraph_distance']}"
                        + (" (same sentence)" if gap["same_sentence"]
                           else " (same paragraph)" if gap["same_paragraph"] else "")) if gap else "first"
            location = (f"L{occurrence['line']} P{occurrence['paragraph']} "
                        f"S{occurrence['sentence']} @{occurrence['start_offset']}")
            rows.append(f"| {location} | {cell(occurrence['context'])} | {distance} | Agent decision pending |")
        rows.extend(["", "Group verdict: pending. State whether this is deliberate parallelism, a necessary "
                         "logical relation, or mechanical repetition.", ""])
    if not families:
        rows.append("No rule hits to review; still read the full text for synonymous patterns the rules cannot see.")

    patterns = report.get("patterns") or []
    if patterns:
        repetition = report.get("repetition", {})
        rows.extend(["## Candidate fixed phrases (not in the rule tables)", "",
                     f"{repetition.get('patterns', len(patterns))} candidate(s) at "
                     f"{repetition.get('min_uses', 3)}+ uses. Discovery only: a repeated term, a quoted "
                     "line, or a deliberate refrain is legitimate. Judge every one.", ""])
        for item in patterns:
            gap = item["gap_summary"]
            pairs = item["same_paragraph_pairs"] + item["cross_paragraph_pairs"]
            rows.extend([f"### {cell(item['pattern'])} ({item['kind']}, {item['lang']})", "",
                         f"{item['count']} uses across {item['paragraph_count']} paragraph(s); "
                         f"{item['sentence_share']:.1%} of sentences, "
                         f"{item['uses_per_1000_prose_chars']} per 1000 prose chars; "
                         f"same-paragraph pairs {item['same_paragraph_pairs']}/{pairs}; gap "
                         f"{gap['min_units']}–{gap['max_units']} {item['units']} "
                         f"(median {gap['median_units']}).", "",
                         f"| Location / offset | Sentence context | Gap to previous: {item['units']} / "
                         "sentences / paragraphs | Decision and reason |",
                         "| --- | --- | --- | --- |"])
            for index, occurrence in enumerate(item["occurrences"]):
                previous = item["adjacent_gaps"][index - 1] if index else None
                distance = (f"{previous['units_between']} / {previous['sentences_between']} / "
                            f"{previous['paragraph_distance']}"
                            + (" (same sentence)" if previous["same_sentence"]
                               else " (same paragraph)" if previous["same_paragraph"] else "")) if previous else "first"
                location = (f"L{occurrence['line']} P{occurrence['paragraph']} "
                            f"S{occurrence['sentence']} @{occurrence['start_offset']}")
                rows.append(f"| {location} | {cell(occurrence['context'])} | {distance} | "
                            "Agent decision pending |")
            rows.extend(["", "Group verdict: pending. Say whether this is a term, a quotation, a deliberate "
                             "refrain, or mechanical repetition to remove.", ""])

    metrics = {key: value for key, value in report.get("metrics", {}).items() if isinstance(value, dict)}
    if metrics:
        rows.extend(["## Formatting metrics", "", "| Metric | Count | Per 1000 prose chars |", "| --- | --- | --- |"])
        for key, value in metrics.items():
            rows.append(f"| {key} | {value['count']} | {value['per_1000_prose_chars']} |")
        rows.extend(["", "Metrics are context, not verdicts: judge them against the genre and length.", ""])
    return "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="Unfiltered schema-v4 JSON report; - reads stdin")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.report == "-" else Path(args.report).read_text(encoding="utf-8")
        report = json.loads(raw)
        if report.get("schema_version") != SCHEMA_VERSION or report.get("display_filter", "all") != "all":
            parser.error("Use an unfiltered schema-v4 scan report (--format json without --only).")
        output = render(report)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError) as error:
        parser.error(f"Invalid scan report: {error}")
    print(output, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
