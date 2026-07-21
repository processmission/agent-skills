---
# SPDX-FileCopyrightText: Copyright (c) 2026 Process Mission
# SPDX-License-Identifier: MIT
name: zephyr-debug
description: >-
  Use when reproducing or isolating the root cause of a Zephyr build,
  toolchain, QEMU, boot, board, or runtime failure.
---

# Zephyr Debug

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

## Diagnose

1. Capture expected and observed behavior, the narrowest reproducer, and the
   first decisive log.
2. Exclude wrong revisions, boards, configuration, stale output, and generated
   artifact or toolchain mismatches before changing source.
3. Locate the first broken invariant across Kconfig, CMake, devicetree,
   generated files, runner commands, boot flow, and runtime state.
4. Test each hypothesis with the smallest reversible probe and distinguish
   observations from inferences.
5. For diagnosis-only requests, stop at the supported cause and remaining
   uncertainty. Implement a fix and regression gate only when requested.

## Choose a debugging path

- Use Zephyr logging and targeted instrumentation when the failure remains
  observable without stopping the system.
- Use a QEMU GDB stub for reproducible emulated failures, early boot, exception
  state, memory inspection, breakpoints, and instruction-level stepping.
- Use the board's configured debug runner with OpenOCD or J-Link for hardware
  failures. Select the runner from the board, probe, and user environment; do
  not assume that one backend is universally available.
- Combine logs with GDB when console history or timing explains state that a
  stopped target cannot.

## Run a remote GDB session

1. Preserve the exact ELF and build configuration that reproduce the failure.
   Use the matching toolchain GDB and keep symbols in the Zephyr build tree.
2. Start the remote endpoint with the configured Zephyr runner: a QEMU GDB
   stub for emulation, or a debug server backed by OpenOCD or J-Link for
   hardware. Prefer runner-generated arguments over guessed probe, transport,
   reset, or device settings.
3. If installed, use Tmux for concurrent panes; otherwise use Zellij, then
   separate terminals. Keep the debug server or QEMU in one pane, GDB in a
   second, and optional console or log monitoring in a third.
4. Generate a task-specific GDB command file under
   `.zephyr-skills/<agent-task>/scripts/`, including the symbol file, remote
   endpoint, breakpoints or watchpoints, thread inspection, and
   evidence-producing commands. Avoid changing global GDB configuration.
5. Connect with `target remote` or `target extended-remote` as required by the
   server. Capture the server command, GDB command file, decisive backtraces,
   register or memory state, and target logs in the audit directory.
6. For a live hardware target, prefer attach semantics when flashing or reset
   is not requested. Record any operation that changes target state.

## Use Zephyr logging and instrumentation

- Enable the Zephyr logging subsystem and the narrowest useful module or
  subsystem log level through task-specific configuration or overlays.
- Add `LOG_DBG`, `LOG_INF`, `LOG_WRN`, `LOG_ERR`, or hexdump probes at state
  transitions, error paths, ownership changes, and relevant interrupt or
  scheduling boundaries.
- Include stable identifiers and state in messages, but never log secrets or
  unbounded data. Keep probes minimal and easy to remove or gate.
- Account for timing changes from added logging, synchronous output, transport
  buffering, and log overflow. Recheck the failure with reduced instrumentation
  before treating the result as causal.
- Save decisive console output under `.zephyr-skills/<agent-task>/logs/` and
  state which logging configuration and probes produced it.

## Guardrails

- Do not hide a failure by weakening assertions or tests.
- Stop only QEMU processes started for the task; never kill broad process
  groups.
- Stop only debug servers and multiplexer sessions started for the task.
