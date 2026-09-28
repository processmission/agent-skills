#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
"""Read-only lexical terminology assistance; findings require contextual review."""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Iterator


@dataclass(frozen=True)
class Term:
    english: str
    chinese: str
    policy: str
    project: str


PROJECTS = ('qemu', 'linux', 'yocto', 'bitbake', 'zephyr')
GLOSSARIES = Path(__file__).resolve().parents[1] / 'references' / 'glossary'


def load_terms(projects: list[str], directory: Path) -> list[Term]:
    terms = []
    for project in projects:
        path = directory / f'{project}.md'
        seen = set()
        for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if not line.startswith('| ') or line.startswith(('| English |', '| ---')):
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) != 5:
                raise ValueError(f'{path}:{number}: expected five columns')
            english, chinese, policy, _, _ = cells
            if (not english or english in seen or policy not in ('bilingual', 'keep-English')
                    or bool(chinese) != (policy == 'bilingual')):
                raise ValueError(f'{path}:{number}: invalid or duplicate term')
            seen.add(english)
            terms.append(Term(english, chinese, policy, project))
        if not seen:
            raise ValueError(f'{path}: empty glossary')
    return terms


def input_files(paths: list[Path]) -> list[Path]:
    files = set()
    for path in paths:
        if not path.exists():
            raise ValueError(f'input does not exist: {path}')
        for candidate in path.rglob('*') if path.is_dir() else [path]:
            if (candidate.is_file() and not candidate.is_symlink()
                    and candidate.name.endswith(('.rst', '.rst.inc', '.md', '.txt'))
                    and not any(part in ('.git', '.venv', 'node_modules', '_build')
                                for part in candidate.parts)):
                files.add(candidate.resolve())
    if not files:
        raise ValueError('no RST, RST include, Markdown or text inputs')
    return sorted(files)


def pattern_body(english: str) -> str:
    return r'\s+'.join(re.escape(word) for word in english.split())


def findings(text: str, terms: list[Term], mode: str) -> Iterator[tuple[int, str, str, str]]:
    if mode == 'inventory':
        for term in terms:
            pattern = r'(?<![A-Za-z0-9_])' + pattern_body(term.english) + r'(?![A-Za-z0-9_])'
            for match in re.finditer(pattern, text, re.I):
                yield match.start(), 'occurrence', term.english, term.project
        return
    if mode == 'candidates':
        known = {term.english.casefold() for term in terms}
        for match in re.finditer(r':term:`([^`]+)`|\b[A-Z][A-Z0-9_+-]{1,}\b', text):
            value = match.group(1) or match.group()
            if value.casefold() not in known:
                yield match.start(), 'unlisted-candidate', value, ''
        return
    by_chinese: dict[str, list[Term]] = {}
    for term in terms:
        if term.chinese:
            by_chinese.setdefault(term.chinese, []).append(term)
    if not by_chinese:
        return
    pattern = '|'.join(re.escape(word) for word in sorted(by_chinese, key=len, reverse=True))
    for match in re.finditer(pattern, text):
        options = by_chinese[match.group()]
        tail = text[match.end():]
        valid = duplicate = False
        for term in options:
            body = pattern_body(term.english)
            bracket = r'\s*(?:（\s*' + body + r'\s*）|\(\s*' + body + r'\s*\))'
            suffix = re.match(bracket, tail, re.I)
            if suffix:
                valid = True
                duplicate = bool(re.match(bracket, tail[suffix.end():], re.I))
                break
        if not valid or duplicate:
            yield (match.start(), 'duplicate-english' if duplicate else 'missing-or-wrong-english',
                   ' / '.join(f'{term.chinese}（{term.english}）' for term in options),
                   ','.join(sorted({term.project for term in options})))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('inventory', 'check', 'candidates'))
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--project', choices=PROJECTS, action='append')
    parser.add_argument('--glossary-dir', type=Path, default=GLOSSARIES)
    parser.add_argument('--format', choices=('text', 'jsonl'), default='text')
    parser.add_argument('--fail-on-findings', action='store_true')
    args = parser.parse_args()
    try:
        terms = load_terms(list(dict.fromkeys(args.project or PROJECTS)), args.glossary_dir)
        files = input_files(args.paths)
        count = 0
        for path in files:
            text = path.read_text(encoding='utf-8')
            for offset, kind, term, project in findings(text, terms, args.mode):
                line = text.count('\n', 0, offset) + 1
                column = offset - text.rfind('\n', 0, offset)
                record = dict(path=str(path), line=line, column=column,
                              kind=kind, term=term, project=project)
                if args.format == 'jsonl':
                    print(json.dumps(record, ensure_ascii=False))
                else:
                    print(f'{path}:{line}:{column}: {kind}: {term} [{project}]')
                count += 1
        print(f'{len(files)} files; {len(terms)} entries; {count} lexical findings '
              '(manual review required)', file=sys.stderr)
        return 1 if count and args.fail_on_findings else 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f'term_scan: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
