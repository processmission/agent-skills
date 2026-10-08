# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Load the scan rules from the reference tables.

The rules are `references/rules-zh.md` and `references/rules-en.md`: Markdown tables a person reads
and edits, which the agent consults when judging a mark and the scanner applies to produce it. This
module parses, compiles, and validates them, so adding or changing a tic is a table edit rather than
a code change.

Table columns: Rule key | Kind | Label | Pattern | Probe | Model | Source | Advice.

- Kind: `ban`, `review`, `family`, or `opener:<group>` for sentence-initial connectives.
- Pattern: a Python regex, matched case-insensitively inside one sentence; `\\|` is a literal pipe.
- Probe: a sentence the pattern must match. Every rule needs one; the suite replays them.
- Several rows may share a rule key: they are alternatives of the same family.
"""
from dataclasses import dataclass
import pathlib
import re
from typing import Literal

Lang = Literal["zh", "en"]
Kind = Literal["ban", "review", "family"]

RULE_DIR = pathlib.Path(__file__).resolve().parents[1] / "references"
RULE_FILES: tuple[tuple[str, str], ...] = (("zh", "rules-zh.md"), ("en", "rules-en.md"))
VALID_KINDS = {"ban", "review", "family"}
COLUMNS = ("Rule key", "Kind", "Label", "Pattern", "Probe", "Model", "Source", "Advice")


class RulesError(Exception):
    """A rule table row that the scanner cannot use."""


@dataclass(frozen=True)
class Rule:
    key: str
    label: str
    kind: Kind
    lang: Lang
    patterns: tuple[str, ...]
    advice: str
    model: str | None = None
    source: str | None = None

    def matches(self, text: str) -> bool:
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in self.patterns)

    def spans(self, text: str) -> list[tuple[int, int]]:
        """Merge overlapping variants, keeping distinct uses within a sentence."""
        spans = sorted({match.span() for pattern in self.patterns
                        for match in re.finditer(pattern, text, re.IGNORECASE)})
        merged: list[tuple[int, int]] = []
        for start, end in spans:
            if merged and start < merged[-1][1]:
                merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
            else:
                merged.append((start, end))
        return merged


def _split_row(line: str) -> list[str]:
    """Split a table row on unescaped pipes; keep every other backslash sequence intact."""
    cells: list[str] = []
    current: list[str] = []
    index = 0
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") else body
    while index < len(body):
        char = body[index]
        if char == "\\" and index + 1 < len(body):
            nxt = body[index + 1]
            if nxt == "|":
                current.append("|")
            else:
                current.extend((char, nxt))
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def _plain(cell: str) -> str:
    """Strip the code span a pattern or probe is written in."""
    text = cell.strip()
    if text.startswith("`") and text.endswith("`") and len(text) > 1:
        text = text[1:-1]
    return text.strip()


def _rows(path: pathlib.Path, lang: str) -> list[tuple[int, list[str]]]:
    parsed: list[tuple[int, list[str]]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = _split_row(line)
        if cells[0] in (COLUMNS[0], "") or set(cells[0]) <= set("-: "):
            continue
        if len(cells) != len(COLUMNS):
            raise RulesError(
                f"{path.name}:{number}: expected {len(COLUMNS)} columns "
                f"({' | '.join(COLUMNS)}), found {len(cells)}")
        if not cells[0].startswith(lang + "-"):
            raise RulesError(f"{path.name}:{number}: rule key {cells[0]!r} does not start with {lang!r}-")
        parsed.append((number, cells))
    return parsed


def load_rules(files: tuple[tuple[str, str], ...] = RULE_FILES
               ) -> tuple[list[Rule], dict, dict, list[tuple[str, str, str]]]:
    """Parse the reference tables into rules, opener groups, one probe per key, and every row probe."""
    entries: dict[tuple[str, str], dict] = {}
    openers: dict[str, dict[str, tuple[str, str]]] = {"zh": {}, "en": {}}
    probes: dict[str, str] = {}
    row_probes: list[tuple[str, str, str]] = []
    for lang, name in files:
        path = RULE_DIR / name
        if not path.exists():
            raise RulesError(f"missing rule table: {path}")
        for number, cells in _rows(path, lang):
            key, kind, label, pattern, probe, model, source, advice = cells
            where = f"{name}:{number}"
            pattern = _plain(pattern)
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as error:
                raise RulesError(f"{where}: {key}: bad regex: {error}") from None
            if kind.startswith("opener:"):
                group = kind.split(":", 1)[1]
                existing = openers[lang].get(group)
                combined = pattern if existing is None else f"(?:{existing[1]})|(?:{pattern})"
                openers[lang][group] = (label or (existing or ("", ""))[0], combined)
                continue
            if kind not in VALID_KINDS:
                raise RulesError(f"{where}: {key}: unknown kind {kind!r}")
            entry = entries.setdefault((lang, key), {
                "label": label, "kind": kind, "advice": advice, "model": model, "source": source,
                "patterns": [],
            })
            if entry["kind"] != kind or entry["label"] != label:
                raise RulesError(f"{where}: {key}: rows disagree on kind or label")
            entry["patterns"].append(pattern)
            probe = _plain(probe)
            if probe and probe != "-":
                row_probes.append((key, pattern, probe))
                if not re.search(pattern, probe, re.IGNORECASE):
                    raise RulesError(f"{where}: {key}: the probe does not match its own pattern")
                probes.setdefault(key, probe)
    if not entries:
        raise RulesError("no rules found in " + ", ".join(name for _, name in files))
    missing = [key for (_, key) in entries if key not in probes]
    if missing:
        raise RulesError("rules without a probe: " + ", ".join(sorted(missing)))
    rules = [Rule(key=key, label=entry["label"], kind=entry["kind"], lang=lang,
                  patterns=tuple(entry["patterns"]), advice=entry["advice"],
                  model=None if entry["model"] in ("", "-") else entry["model"],
                  source=None if entry["source"] in ("", "-") else entry["source"])
             for (lang, key), entry in entries.items()]
    return rules, openers, probes, row_probes


try:
    RULES, OPENERS, PROBES, ROW_PROBES = load_rules()
    LOAD_ERROR: str | None = None
except RulesError as error:  # surfaced by the CLI as an argument error
    RULES, OPENERS, PROBES, ROW_PROBES, LOAD_ERROR = [], {"zh": {}, "en": {}}, {}, [], str(error)
