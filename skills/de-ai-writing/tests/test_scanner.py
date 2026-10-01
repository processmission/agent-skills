# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Regression checks for language routing, distance evidence, and non-destructive CLI behavior."""
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scan_writing.py"
RENDERER = SCRIPT.with_name("render_review.py")
sys.path.insert(0, str(SCRIPT.parent))
import scan_writing  # noqa: E402
import writing_rules  # noqa: E402


def scan(text, *options):
    process = subprocess.run([sys.executable, "-S", str(SCRIPT), "-", "--format", "json", *options],
                             input=text, text=True, capture_output=True)
    if process.returncode not in (0, 1):
        raise AssertionError(process.stderr)
    return process.returncode, json.loads(process.stdout)


def worksheet(report):
    return subprocess.run([sys.executable, "-S", str(RENDERER), "-"],
                          input=json.dumps(report), text=True, capture_output=True)


def family(report, name):
    return next(item for item in report["families"] if item["rule"] == name)


class ChineseRulesTests(unittest.TestCase):
    def test_local_parallelism_has_two_occurrences_in_one_sentence(self):
        _, report = scan("只有读完，才覆盖，只有写完，才读取。")
        item = family(report, "zh-exclusive-condition")
        self.assertEqual(item["count"], 2)
        self.assertEqual(item["sentence_count"], 1)
        self.assertTrue(item["adjacent_gaps"][0]["same_sentence"])
        self.assertEqual(report["summary"]["blocked_groups"], 0)

    def test_distances_are_anchored_in_source_not_line_counts(self):
        text = "虽然很慢，但正确。\n\n中间事实。\n\n尽管很快，却出错。"
        _, report = scan(text)
        item = family(report, "zh-concession")
        gap = item["adjacent_gaps"][0]
        first, second = item["occurrences"]
        self.assertEqual(text[first["start_offset"]:first["end_offset"]], first["match"])
        self.assertEqual(text[second["start_offset"]:second["end_offset"]], second["match"])
        self.assertEqual(gap["source_chars_between"], len("正确。\n\n中间事实。\n\n"))
        self.assertEqual(gap["prose_chars_between"], len("正确。中间事实。"))
        self.assertEqual(gap["sentences_between"], 1)
        self.assertEqual(gap["paragraph_distance"], 2)
        self.assertEqual(second["line"], 5)

    def test_fences_quotes_comments_and_metadata_do_not_pollute_counts(self):
        text = ('---\ntitle: 不是甲，而是乙\n---\n```text\n不是甲，而是乙。\n```\n'
                '> 不是甲，而是乙。\n\n“不是甲，而是乙。”\n\n'
                '<!-- 不是甲，而是乙。 -->\n\n实际结果正常。\n\n不是慢，而是错。')
        _, report = scan(text)
        item = family(report, "zh-false-reversal")
        self.assertEqual(item["count"], 1)
        self.assertEqual(item["occurrences"][0]["line"], 15)
        _, report = scan(text, "--include-quotes")
        self.assertEqual(family(report, "zh-false-reversal")["count"], 3)

    def test_distant_repetition_remains_agent_review(self):
        _, report = scan("虽然很慢，但正确。\n\n" + "正常事实。" * 100 + "\n\n尽管很快，却出错。\n\n即使重试，仍然失败。")
        self.assertEqual(report["summary"]["blocked_groups"], 0)
        self.assertGreater(family(report, "zh-concession")["gap_summary"]["max_prose_chars"], 400)
        self.assertTrue(any(item["rule"] == "zh-concession" for item in report["findings"]))

    def test_wrapped_paragraphs_and_markdown_links_preserve_positions(self):
        text = "# 概览\n\n虽然很慢，\n但正确。\n\n[虽然很快，却出错](https://example.com)。"
        _, report = scan(text)
        item = family(report, "zh-concession")
        self.assertEqual(item["count"], 2)
        self.assertEqual(item["occurrences"][0]["end_line"], 4)
        last = item["occurrences"][1]
        self.assertEqual(text[last["start_offset"]:last["end_offset"]], last["match"])

    def test_normal_connectives_are_not_individually_banned(self):
        code, report = scan("如果运行失败，就重试。\n\n因此记录日志。\n\n但是测试仍需完成。")
        self.assertEqual(code, 0)
        self.assertEqual(report["summary"]["blocked_groups"], 0)

    def test_output_filter_does_not_change_exit_status_or_full_statistics(self):
        code, report = scan("不能写成替换模型。", "--only", "review")
        self.assertEqual(code, 1)
        self.assertFalse(report["findings"])
        self.assertEqual(family(report, "zh-editor-leak")["count"], 1)

    def test_empty_and_unclosed_fence_are_safe(self):
        for text in ("", "```\n不是甲，而是乙。"):
            code, report = scan(text)
            self.assertEqual(code, 0)
            self.assertEqual(report["summary"]["sentences"], 0)


class EnglishRulesTests(unittest.TestCase):
    def test_banned_english_structures_block_the_run(self):
        code, report = scan("This is not just a refactor, but a redesign. In today's fast-paced world, "
                            "the cache stands as a testament to the craft. In conclusion, the future looks bright.")
        self.assertEqual(code, 1)
        reported = {item["rule"] for item in report["findings"]}
        self.assertLessEqual({"en-false-reversal", "en-stock-phrases", "en-generic-conclusion"}, reported)

    def test_english_review_families_stay_review(self):
        _, report = scan("The patch is not only faster but also simpler. It is worth noting that the queue "
                         "drains first.")
        self.assertEqual(report["summary"]["blocked_groups"], 0)
        reported = {item["rule"] for item in report["findings"]}
        self.assertLessEqual({"en-negative-parallelism", "en-throat-clearing"}, reported)

    def test_sentence_boundaries_keep_abbreviations_and_decimals_intact(self):
        _, report = scan("The p99 was 3.5 ms, e.g. inside one frame. It held.")
        self.assertEqual(report["summary"]["sentences"], 2)

    def test_abbreviation_before_a_new_sentence_does_not_hide_anchored_rules(self):
        code, report = scan("We ran the tests, etc. Certainly, the cache is faster.")
        self.assertEqual(code, 1)
        self.assertEqual(report["summary"]["sentences"], 2)
        self.assertTrue(any(item["rule"] == "en-chatbot-voice" for item in report["findings"]))

    def test_single_hype_word_is_a_review_item(self):
        code, report = scan("这个方案能够重塑整个体系。")
        self.assertEqual(code, 0)
        item = next(item for item in report["findings"] if item["rule"] == "zh-hype-vocabulary")
        self.assertEqual(item["severity"], "review")

    def test_corporate_jargon_is_review_only_and_carries_its_own_advice(self):
        code, report = scan("这个项目要先打通数据链路，形成闭环。")
        self.assertEqual(code, 0)
        item = next(item for item in report["findings"] if item["rule"] == "zh-corporate-jargon")
        self.assertEqual(item["severity"], "review")
        self.assertEqual(item["count"], 1, "one sentence counts once, however many jargon words it holds")
        self.assertIn("打通", item["advice"])

    def test_english_opener_density_is_review_only(self):
        text = ("However, the cache drains.\n\nHowever, the queue fills.\n\nHowever, the batch shrinks.\n\n"
                "However, the tail grows.\n\nHowever, the kernel waits.\n\nDone.")
        code, report = scan(text)
        self.assertEqual(code, 0)
        self.assertEqual(report["summary"]["blocked_groups"], 0)
        self.assertTrue(any(item["rule"] == "en-opener-turn" for item in report["findings"]))

    def test_repeated_opening_is_surfaced_as_a_candidate_pattern(self):
        text = ("The results show a win.\n\nThe results show a loss.\n\nThe results show a tie.\n\n"
                "The results show a shift.\n\nDone.")
        _, report = scan(text)
        item = next(item for item in report["patterns"] if item["pattern"] == "the results show a")
        self.assertEqual(item["count"], 4)
        self.assertEqual(item["units"], "words")
        self.assertGreater(item["paragraph_count"], 1)

    def test_scattered_and_clustered_repetition_are_distinguished(self):
        def candidate(report):
            return next(item for item in report["patterns"]
                        if "cache holds" in item["pattern"].lower())

        scattered = ("The cache holds the writes.\n\n" + "Filler about the queue. " * 20
                     + "\n\nThe cache holds the writes.\n\n" + "Filler about the scheduler. " * 20
                     + "\n\nThe cache holds the writes.")
        item = candidate(scan(scattered)[1])
        self.assertGreaterEqual(item["cross_paragraph_pairs"], 1)
        self.assertGreater(item["gap_summary"]["median_units"], 10)

        clustered = " ".join(["The cache holds the writes."] * 4)
        item = candidate(scan(clustered)[1])
        self.assertGreaterEqual(item["same_paragraph_pairs"], 1)

    def test_repeated_phrase_inside_different_sentences_is_reported(self):
        text = ("The cache holds the writes first. The queue holds the writes later. "
                "The disk holds the writes eventually. Nothing else changes here.")
        _, report = scan(text)
        item = next(item for item in report["patterns"] if item["pattern"] == "holds the writes")
        self.assertEqual(item["kind"], "phrase")
        self.assertEqual(item["count"], 3)
        self.assertEqual(item["units"], "words")
        self.assertGreater(item["gap_summary"]["median_units"], 0)

    def test_verbatim_sentence_repeat_is_reported_once(self):
        text = "缓存命中率提升明显。\n\n缓存命中率提升明显。\n\n缓存命中率提升明显。\n\n另一段无关内容。"
        _, report = scan(text)
        sentences = [item for item in report["patterns"] if item["kind"] == "sentence"]
        self.assertEqual(len(sentences), 1)
        self.assertEqual(sentences[0]["count"], 3)
        self.assertEqual(sentences[0]["units"], "chars")

    def test_text_without_repetition_reports_no_candidates(self):
        _, report = scan("缓存命中率提升，延迟下降。队列排空后写入完成，磁盘压力回落。")
        self.assertEqual(report["patterns"], [])
        self.assertEqual(report["repetition"]["patterns"], 0)

    def test_formatting_metrics_count_markup_tells(self):
        text = "Caching helps — a lot — here.\n\n## Strategic Negotiation And Partnership\n\nA **bold** label.\n"
        _, report = scan(text)
        metrics = report["metrics"]
        self.assertEqual(metrics["em_dash"]["count"], 2)
        self.assertEqual(metrics["bold_span"]["count"], 1)
        self.assertEqual(metrics["title_case_heading"]["count"], 1)

    def test_formatting_metrics_cover_spacing_quotes_breaks_and_wh_headings(self):
        text = ("## Why It Matters\n\nThe tool is fast — really — today.\n\n---\n\n"
                "She said \"the queue drains first\".\n")
        _, report = scan(text)
        metrics = report["metrics"]
        self.assertEqual(metrics["em_dash_spaced"]["count"], 2)
        self.assertEqual(metrics["wh_heading"]["count"], 1)
        self.assertEqual(metrics["thematic_break"]["count"], 1)
        self.assertEqual(metrics["quotation_mark"]["count"], 2)


class LanguageRoutingTests(unittest.TestCase):
    def test_each_rule_set_runs_only_on_its_own_sentences(self):
        text = ("这不是甲，而是乙。\n\nThis is not just a refactor, but a redesign.\n\n"
                "在中文句子里嵌入 API 与 kernel 的术语说明正常。")
        _, report = scan(text)
        self.assertEqual(report["summary"]["languages"], {"zh": 2, "en": 1})
        self.assertEqual(family(report, "zh-false-reversal")["count"], 1)
        self.assertEqual(family(report, "en-false-reversal")["count"], 1)

    def test_report_carries_schema_languages_and_metrics(self):
        _, report = scan("Done.")
        self.assertEqual(report["schema_version"], 4)
        self.assertEqual(report["summary"]["languages"], {"en": 1})
        self.assertEqual(report["metrics"]["prose_chars"], len("Done."))

    def test_term_dense_chinese_sentences_stay_chinese(self):
        _, report = scan("用 Redis、Kafka、MySQL、Nginx、Docker、Terraform 部署服务。")
        self.assertEqual(report["summary"]["languages"], {"zh": 1})
        _, report = scan("The term 缓存穿透 appears here.")
        self.assertEqual(report["summary"]["languages"], {"en": 1})

    def test_unsupported_script_is_reported_but_not_scanned(self):
        _, report = scan("これはテストです。")
        self.assertEqual(report["summary"]["languages"], {"other": 1})
        self.assertEqual(report["families"], [])
        self.assertEqual(report["summary"]["blocked_groups"], 0)

    def test_metrics_use_the_documented_prose_character_denominator(self):
        text = "Real prose here.\n\n> quoted line with more words inside\n\n“more quoted text”\n"
        _, report = scan(text)
        self.assertEqual(report["metrics"]["prose_chars"], report["summary"]["prose_chars"])


class WorksheetTests(unittest.TestCase):
    def test_review_worksheet_preserves_evidence_without_making_decisions(self):
        _, report = scan("只有搬完，才读取；只有算完，才覆盖。")
        process = worksheet(report)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("same paragraph", process.stdout)
        self.assertIn("Agent decision pending", process.stdout)
        self.assertIn("只有搬完，才读取", process.stdout)

    def test_filtered_or_stale_reports_are_rejected(self):
        _, report = scan("只有搬完，才读取；只有算完，才覆盖。")
        report["display_filter"] = "block"
        self.assertEqual(worksheet(report).returncode, 2)
        report["display_filter"] = "all"
        report["schema_version"] = 2
        self.assertEqual(worksheet(report).returncode, 2)


class RuleProbeTests(unittest.TestCase):
    """Every rule must fire on a realistic sentence, so no rule can be silently dead."""

    def test_every_rule_has_a_probe_from_the_tables(self):
        library = {rule.key for rule in writing_rules.RULES}
        self.assertEqual(sorted(library - set(writing_rules.PROBES)), [])

    def test_every_rule_fires_on_its_table_probe(self):
        report = scan_writing.analyze("\n\n".join(writing_rules.PROBES.values()))
        reported = {family["rule"] for family in report["families"]}
        missing = sorted(set(writing_rules.PROBES) - reported)
        self.assertEqual(missing, [])
        for key, probe in writing_rules.PROBES.items():
            rule = next(rule for rule in writing_rules.RULES if rule.key == key)
            self.assertTrue(rule.matches(probe), f"{key} does not match its own probe")


    def test_rhythm_block_separates_uniform_from_varied_prose(self):
        uniform = " ".join(["The system handles every request in a consistent manner."] * 6)
        varied = ("Cache. The write path took 21-23 us less after we removed one global lock, which I "
                  "would not have believed before running the benchmark twelve times. Then it broke.")
        _, report = scan(uniform)
        self.assertGreater(report["rhythm"]["en"]["share_within_10_percent"], 0.5)
        self.assertLess(report["rhythm"]["en"]["variation"], 0.2)
        _, report = scan(varied)
        self.assertGreater(report["rhythm"]["en"]["variation"], 0.5)


class RuleTableTests(unittest.TestCase):
    def test_escaped_pipe_survives_the_table_round_trip(self):
        cells = writing_rules._split_row(r"| k | ban | L | `a\|b` | probe | - | advice |")
        self.assertEqual(cells[3], "`a|b`")
        self.assertEqual(writing_rules._plain(cells[3]), "a|b")

    def test_tables_supply_both_languages_and_model_rows(self):
        keys = {rule.key for rule in writing_rules.RULES}
        self.assertTrue(any(key.startswith("zh-") for key in keys))
        self.assertTrue(any(key.startswith("en-") for key in keys))
        self.assertTrue(any(rule.model for rule in writing_rules.RULES))
        self.assertIsNone(writing_rules.LOAD_ERROR)

    def test_a_broken_row_names_the_file_line_and_key(self):
        bad = Path("/tmp/bad-rules-zh.md")
        bad.write_text("| Rule key | Kind | Label | Pattern | Probe | Model | Source | Advice |\n"
                       "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                       "| zh-broken | ban | Broken | `a(b` | 探针句。 | - | - | fix it |\n",
                       encoding="utf-8")
        with self.assertRaises(writing_rules.RulesError) as caught:
            writing_rules.load_rules((("zh", str(bad)),))
        self.assertIn("bad-rules-zh.md:3", str(caught.exception))
        self.assertIn("zh-broken", str(caught.exception))

    def test_a_row_with_the_wrong_column_count_is_rejected(self):
        bad = Path("/tmp/short-rules-zh.md")
        bad.write_text("| Rule key | Kind | Label | Pattern | Probe | Model | Advice |\n"
                       "| --- | --- | --- | --- | --- | --- | --- |\n"
                       "| zh-short | ban | Short | `x` | 探针。 | - | fix it |\n", encoding="utf-8")
        with self.assertRaises(writing_rules.RulesError) as caught:
            writing_rules.load_rules((("zh", str(bad)),))
        self.assertIn("expected 8 columns", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
