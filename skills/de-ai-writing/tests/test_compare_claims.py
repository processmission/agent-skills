# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Checks for the claim diff: it must surface paraphrases, and stay quiet on real edits."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_claims.py"
sys.path.insert(0, str(SCRIPT.parent))
import compare_claims  # noqa: E402


def diff(before, after):
    return compare_claims.compare(before, after)


def flags(before, after):
    report = diff(before, after)
    return [flag for item in report["changed"] for flag in item["flags"]]


class ClaimDiffTests(unittest.TestCase):
    def test_identical_text_needs_no_justification(self):
        text = "Host reservation 必须从 Host 管理 RAM 中扣除。\n\n每个 VM 要求恰好一个 boot memory。\n"
        report = diff(text, text)
        self.assertEqual(report["summary"]["needs_reason"], 0)
        self.assertEqual(report["summary"]["exit_code"], 0)
        self.assertEqual(report["changed"], [])

    def test_dropping_an_intensifier_is_flagged_as_unlicensed(self):
        before = "只有构建明确提供 `EMBEDDED_IMAGES` 时，生成器才输出引用。\n"
        after = "只有构建提供 `EMBEDDED_IMAGES` 时，生成器才输出引用。\n"
        self.assertIn("unlicensed", flags(before, after))

    def test_a_changed_number_is_flagged(self):
        self.assertIn("number", flags("峰值达到 2122 tokens/s。\n", "峰值达到 2200 tokens/s。\n"))

    def test_a_digit_inside_an_identifier_is_not_a_number_change(self):
        self.assertNotIn("number", flags("模型为 ARM64 Host 配置。\n", "模型为 ARM64 与 RISC-V Host 配置。\n"))

    def test_a_swapped_identifier_is_flagged(self):
        self.assertIn("identifier", flags("`zvisor.json` 供导出器读取。\n", "`zvisor_input.json` 供导出器读取。\n"))

    def test_a_weakened_requirement_is_flagged_as_modality(self):
        self.assertIn("modality", flags("每个 VM 必须有一个 boot memory。\n", "每个 VM 应当有一个 boot memory。\n"))

    def test_a_dropped_quantifier_is_flagged(self):
        self.assertIn("quantifier", flags("镜像中仅嵌入一个 Guest payload。\n", "镜像中嵌入一个 Guest payload。\n"))

    def test_equal_negation_counts_are_flagged_as_polarity(self):
        before = "本设计不将 x86、整设备直通列为已验证能力。\n"
        after = "x86、整设备直通尚无验证证据。\n"
        self.assertIn("polarity", flags(before, after))

    def test_a_removed_negation_is_flagged(self):
        before = "整设备直通不属于当前 DTS 资源生成能力。\n"
        after = "整设备直通属于当前 DTS 资源生成能力。\n"
        self.assertIn("negation", flags(before, after))

    def test_a_rule_driven_removal_is_not_unlicensed(self):
        before = "这不是调度问题，而是内存布局问题。\n"
        after = "这是内存布局问题。\n"
        report = diff(before, after)
        self.assertEqual(report["changed"][0]["rules_removed"], ["zh-false-reversal"])
        self.assertNotIn("unlicensed", report["changed"][0]["flags"])
        self.assertIn("negation", report["changed"][0]["flags"])

    def test_a_punctuation_only_change_is_not_a_claim_change(self):
        report = diff("两级结构——Host 与 Guest——共享同一份事实。\n", "两级结构：Host 与 Guest 共享同一份事实。\n")
        self.assertEqual(report["changed"][0]["flags"], ["punctuation"])
        self.assertEqual(report["summary"]["needs_reason"], 0)
        self.assertEqual(report["summary"]["exit_code"], 0)

    def test_an_added_sentence_needs_a_reason(self):
        report = diff("配置链路采用失败关闭。\n", "配置链路采用失败关闭。\n评测覆盖运行期路径。\n")
        self.assertEqual(len(report["added"]), 1)
        self.assertEqual(report["summary"]["exit_code"], 1)

    def test_a_deleted_sentence_needs_a_reason(self):
        report = diff("配置链路采用失败关闭。\n多余的说明可以删除。\n", "配置链路采用失败关闭。\n")
        self.assertEqual(len(report["deleted"]), 1)
        self.assertEqual(report["summary"]["exit_code"], 1)

    def test_a_quoted_scope_line_is_compared(self):
        before = "> 状态：本文描述构建期路径。\n"
        after = "> 状态：本文描述运行期路径。\n"
        report = diff(before, after)
        self.assertEqual(len(report["changed"]), 1)
        self.assertIn("构建期", report["changed"][0]["before"]["text"])


class ClaimDiffCliTests(unittest.TestCase):
    def run_cli(self, before, after):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.md"
            revised = Path(directory) / "revised.md"
            original.write_text(before, encoding="utf-8")
            revised.write_text(after, encoding="utf-8")
            process = subprocess.run([sys.executable, "-S", str(SCRIPT), str(original), str(revised)],
                                     text=True, capture_output=True)
            return process, original.read_text(encoding="utf-8"), revised.read_text(encoding="utf-8")

    def test_exit_codes_and_read_only_inputs(self):
        process, original, revised = self.run_cli("文本保持不变。\n", "文本保持不变。\n")
        self.assertEqual(process.returncode, 0)
        self.assertEqual(original, "文本保持不变。\n")
        self.assertEqual(revised, "文本保持不变。\n")

        process, _, _ = self.run_cli("峰值达到 2122 tokens/s。\n", "峰值达到 2200 tokens/s。\n")
        self.assertEqual(process.returncode, 1)
        self.assertIn("number", process.stdout)

        process = subprocess.run([sys.executable, "-S", str(SCRIPT), "/nonexistent.md", "/also/missing.md"],
                                 text=True, capture_output=True)
        self.assertEqual(process.returncode, 2)

    def test_json_format_reports_the_same_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.md"
            revised = Path(directory) / "revised.md"
            original.write_text("每个 VM 必须有一个 boot memory。\n", encoding="utf-8")
            revised.write_text("每个 VM 应当有一个 boot memory。\n", encoding="utf-8")
            process = subprocess.run([sys.executable, "-S", str(SCRIPT), str(original), str(revised),
                                      "--format", "json"], text=True, capture_output=True)
            report = json.loads(process.stdout)
            self.assertEqual(report["schema"], 1)
            self.assertEqual(report["summary"]["changed"], 1)
            self.assertIn("modality", report["changed"][0]["flags"])


if __name__ == "__main__":
    unittest.main()
