# Zephyr Agent Skills

Agent skills for [Zephyr Project](https://www.zephyrproject.org/) development,
debugging, exploration, patch review, and safety evidence work.

Source repository: <https://github.com/processmission/agent-skills>

## Install

From the root of the Zephyr repository, run:

```sh
curl -fsSL https://raw.githubusercontent.com/processmission/agent-skills/main/skills/zephyr/install.sh | bash
```

By default, the installer adds every skill in the `skills/zephyr/` catalog to
the current project for Codex and Claude Code. It also adds `.agents/`,
`.claude/skills/`, `.zephyr-skills/`, and `skills-lock.json` to the
repository's local Git exclude file, so installation and agent task artifacts
do not dirty the worktree. It does not modify the repository's `.gitignore`.

To install from a local checkout, or to select an individual skill:

```sh
./skills/zephyr/install.sh --target /path/to/zephyr
./skills/zephyr/install.sh --target /path/to/zephyr --skill zephyr-debug
```

## Repository workflow

Each Zephyr skill is self-contained, can be installed independently, and does
not require another Zephyr skill. Every skill includes the same compact audit
workflow. For non-trivial tasks that write to the workspace, agent plans, audit
records, command journals, decisive logs, and other temporary evidence go under
`.zephyr-skills/<agent-task>/`. Put generated intermediate debugging documents,
debug scripts, and Bash or Python scaffolding and harness scripts in
`.zephyr-skills/<agent-task>/scripts/`, never in a build directory. Put
non-Zephyr third-party source or libraries acquired solely for the agent's task,
and temporary binaries produced by agent-only probes or tools, in
`.zephyr-skills/<agent-task>/output/`. Do not copy normal Zephyr build artifacts
there. Keep Zephyr-native build trees, binaries, and routine test outputs in a
path chosen by the user or the relevant Zephyr tool's default. In a Git
worktree, add `/.zephyr-skills/` to the repository-local exclude file returned
by `git rev-parse --git-path info/exclude` before writing audit artifacts, and
verify that `git status --short` contains no `.zephyr-skills/` paths.

## Skills

### `zephyr-debug`

Reproduce and isolate Zephyr build, toolchain, QEMU, boot, board, or runtime
failures. Use targeted Zephyr logging, QEMU GDB stubs, or OpenOCD and J-Link
remote debugging according to the target and available tools.

### `zephyr-explore`

Investigate Zephyr source, branch history, external precedent, and design
constraints before making changes. Use it to clarify current behavior,
maintainer boundaries, and compatibility requirements.

### `zephyr-patch-review`

Review Zephyr diffs or patch stacks for correctness, integration impact, test
coverage, reviewer boundaries, and merge readiness. Report only actionable,
source-backed findings.

### `zephyr-safety-evidence`

Plan or review Zephyr safety evidence, requirements traceability, and
certification gaps for ASIL, ISO 26262, IEC 61508, SIL, MC/DC, HARA,
FMEA/FMEDA, and tool qualification work. It never presents draft or partial
evidence as completed certification.
