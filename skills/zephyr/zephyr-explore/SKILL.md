---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: zephyr-explore
description: >-
  Use when Zephyr source, branch history, external precedent, or design
  constraints must be investigated before a decision can be made.
---

# Zephyr Explore

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

## Investigate

1. Bound the question to paths, symbols, configuration, and behavior.
2. Search current source, tests, documentation, and `MAINTAINERS.yml` before
   using history or external material.
3. For branch comparisons, use the user-specified target. Otherwise resolve the
   configured upstream and use `git merge-base HEAD <upstream>`; report a
   missing target or upstream instead of guessing.
4. Use local history when current source does not explain intent or a
   compatibility constraint.
5. Consult primary external sources only when local evidence is insufficient.
6. Stop when the evidence supports the next design, review, or verification
   decision.

## Report

- Separate implemented, verified, documented, inferred, and unknown behavior.
- Cite decisive paths, symbols, commits, or external revisions.
- Treat external code as precedent unless import is explicitly in scope and
  license-compatible.
