---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: zephyr-patch-review
description: >-
  Use when reviewing Zephyr diffs or patch stacks for correctness,
  integration, coverage, reviewer boundaries, or merge readiness.
---

# Zephyr Patch Review

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

## Review

1. Bound the review to an explicit base and intended behavior; separate
   unrelated changes before judging the patch.
2. Inspect correctness and semantic integration, including ownership, lifetime,
   locking, error paths, generated artifacts, and 32/64-bit assumptions.
3. Check the affected Kconfig, CMake, devicetree, architecture, board, SoC,
   toolchain, documentation, and API-lifecycle boundaries.
4. Verify that targeted tests and logs support each behavior claim and state the
   remaining coverage gaps.
5. Check patch order, reviewer-sized separation, bisectability, and applicable
   SPDX and license conventions for new files.

## Ownership and precedent

- Use `MAINTAINERS.yml` for affected areas, reviewers, labels, and tests;
  `CODEOWNERS` is not authoritative in this tree.
- Consult local history for unfamiliar APIs, regressions, or subsystem boundary
  changes. Prefer `git log --follow`, `git log -S`, `git blame`, and `git show`.
- Query the current Gerrit change and patch-set state, or an upstream pull
  request when explicitly in scope, only for merge readiness. Read current
  submit, approval, and blocker policy instead of hard-coding it.
- Treat unavailable history as a gap, not evidence of a defect.

## Findings

- Report only actionable, source-backed findings, with file and line references
  when available.
- Explain the failure mode, impact, and any missing or inadequate verification.
- If there are no findings, say so and list residual verification gaps.
