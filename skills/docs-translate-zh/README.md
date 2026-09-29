# Technical Documentation Translation

Translate complete English technical documents into reviewable Simplified
Chinese RST or Markdown while preserving meaning, structure, and code.
The workflow and reference material are written in Chinese for translators.

## Install

Select this skill with the repository installer:

```sh
npx skills add processmission/agent-skills --skill docs-translate-zh
```

To install this checkout manually for Codex, run from the repository root:

```sh
mkdir -p ~/.codex/skills
cp -R skills/docs-translate-zh ~/.codex/skills/
```

## Use

Invoke `$docs-translate-zh` with the source repository, documentation scope,
and target language directory. Specify whether the task includes building,
committing, or publishing; translation alone does not authorize deployment.

For example:

> 使用 $docs-translate-zh 将 docs/system/ 下的英文文档译成中文，保持原有
> RST 目录结构，维护双语术语，并验证中文 HTML。此次不提交或部署。

The [skill instructions](SKILL.md) cover full-article translation, review,
source tracking, and optional Sphinx and GitHub Pages validation. When an
accepted Chinese technical term is used, retain its English name in
parentheses at every occurrence. Preserve executable code and identifiers.

## References and terminology checks

- [Terminology policy](references/terminology.md): translation decisions and
  project glossary maintenance.
- [Project appendices and scanner usage](references/term-scan.md): QEMU,
  Linux, Yocto, BitBake, and Zephyr terminology with source references.
- [Translation review](references/translation-review.md): fidelity, context,
  structure, and coverage checks.
- [Sphinx and publishing](references/sphinx-publishing.md): builds, links,
  search, and authorized deployment.

Run the read-only scanner with Python 3.10 or newer; no third-party packages
are required. From this skill directory:

```sh
python3 scripts/term_scan.py inventory /path/to/english/docs --project qemu
python3 scripts/term_scan.py check /path/to/zh_CN --project qemu
python3 scripts/term_scan.py candidates /path/to/english/docs --project qemu
```

The Markdown appendices are the scanner's data source. Findings are lexical
review candidates, not proof of translation errors or complete coverage.
The tool does not modify documents. See the usage reference for JSONL output,
custom glossaries, exit codes, and known limitations.
