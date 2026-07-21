---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: zephyr-safety-evidence
description: >-
  Use when planning or reviewing Zephyr safety evidence, safety requirements
  traceability, certification gaps, or claims involving ASIL, ISO 26262,
  IEC 61508, SIL, MC/DC, HARA, FMEA/FMEDA, tool qualification, or safety
  cases.
---

# Zephyr Safety Evidence

## Audit workflow

For every non-trivial task that writes to the workspace, choose a stable task
slug and keep agent-only records under:

```text
.zephyr-skills/<agent-task>/
├── audit.md        # Baseline, decisions, evidence, verification, and gaps
├── commands.md     # Redacted commands, working directories, and results
├── scripts/        # Intermediate debug documents, scripts, and harnesses
├── output/         # Non-Zephyr dependencies and temporary binaries
└── logs/           # Decisive build, test, runtime, or diagnostic logs
```

Put every generated intermediate debugging document, debug script, and
scaffolding or harness script, including Bash and Python scripts, under
`scripts/`, never in a build directory. Put non-Zephyr third-party source or
libraries acquired solely for the agent's task, and temporary binaries produced
by agent-only probes or tools, under `output/`. Do not copy normal Zephyr build
artifacts there. Keep other agent plans and temporary evidence in the same task
directory. In a Git worktree, add
`/.zephyr-skills/` to the repository-local exclude file returned by
`git rev-parse --git-path info/exclude` before writing audit artifacts. Preserve
existing entries, avoid duplicates, and verify before handoff that
`git status --short` contains no `.zephyr-skills/` paths. Keep Zephyr-native
build trees, binaries, and test outputs separate: honor a user-specified path,
otherwise use defaults such as configured `build.dir-fmt`, `build/`, or
`twister-out/`. Record the effective paths, do not stage `.zephyr-skills/`
unless requested, and report the task directory and unresolved gaps at handoff.

## Evidence workflow

1. Read the [safety guardrails](references/safety-guardrails.md) in full before
   producing safety-facing output.
2. Bound the claim to a safety scope layer, owner, source baseline, and evidence
   boundary.
3. Create only the artifacts the task needs: traceability, evidence, scope, or
   assumptions.
4. For implementation claims, link requirements to code or configuration and
   verification evidence. For product, process, or assessment claims, link the
   applicable requirement, process, or assessment evidence and mark code or
   test fields as not applicable or as gaps.
5. Separate facts, assumptions, human judgments, and gaps, and state what the
   evidence does not prove.
6. Leave certification, risk acceptance, and scope-closure decisions to the
   responsible humans and assessors.

Never treat draft or partial evidence as proof of product ASIL compliance,
IEC 61508 SIL/SC compliance, or completed certification.
