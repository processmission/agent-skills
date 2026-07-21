#!/usr/bin/env bash

set -euo pipefail

readonly DEFAULT_SKILL_SOURCE="https://github.com/processmission/agent-skills/tree/main/skills/zephyr"
readonly REQUIRED_EXCLUDES=(
    ".agents/"
    ".claude/skills/"
    ".zephyr-skills/"
    "skills-lock.json"
)

usage() {
    cat <<'EOF'
Install the Zephyr agent skills into a Git repository.

Usage:
  install.sh [install] [--target DIR] [skills options...]

Options:
  --target DIR          Install into DIR instead of the current directory.
  -s, --skill NAME      Install one skill instead of every Zephyr skill.
  -a, --agent NAME...   Override the default agents (codex and claude-code).
  -y, --yes             Skip confirmation prompts.
  -h, --help            Show this help.

Environment:
  ZEPHYR_SKILLS_SOURCE  Override the skills source passed to `npx skills add`.

By default, the installer installs every skill in the Zephyr catalog for Codex
and Claude Code. It also adds .agents/, .claude/skills/, .zephyr-skills/, and
skills-lock.json to the repository's local Git exclude file.
EOF
}

die() {
    printf 'zephyr-skills: %s\n' "$*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 ||
        die "required command not found: $1"
}

resolve_skill_source() {
    if [[ -n "${ZEPHYR_SKILLS_SOURCE:-}" ]]; then
        printf '%s\n' "$ZEPHYR_SKILLS_SOURCE"
        return
    fi

    local script_path=""
    local script_dir=""

    if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
        script_path="${BASH_SOURCE[0]}"
        script_dir="$(cd "$(dirname "$script_path")" && pwd)"
    fi

    if [[ -n "$script_dir" &&
          -f "$script_dir/README.md" &&
          -f "$script_dir/zephyr-debug/SKILL.md" ]]; then
        printf '%s\n' "$script_dir"
        return
    fi

    printf '%s\n' "$DEFAULT_SKILL_SOURCE"
}

resolve_target_root() {
    local requested_target="$1"
    local target_dir
    local git_root

    target_dir="$(cd "$requested_target" 2>/dev/null && pwd -P)" ||
        die "target directory does not exist: $requested_target"
    git_root="$(git -C "$target_dir" rev-parse --show-toplevel 2>/dev/null)" ||
        die "target directory is not inside a Git repository: $target_dir"

    [[ "$target_dir" == "$git_root" ]] ||
        die "run from the repository root or pass --target $git_root"

    printf '%s\n' "$git_root"
}

add_local_exclude() {
    local target_root="$1"
    local entry="$2"
    local exclude_file
    local bare_entry
    local escaped_entry
    local probe_path

    exclude_file="$(git -C "$target_root" rev-parse --git-path info/exclude)"
    if [[ "$exclude_file" != /* ]]; then
        exclude_file="$target_root/$exclude_file"
    fi

    mkdir -p "$(dirname "$exclude_file")"
    touch "$exclude_file"

    bare_entry="${entry%/}"
    escaped_entry="$(printf '%s' "$bare_entry" | sed 's/[][\.^$*+?{}|()]/\\&/g')"

    if ! grep -Eq "^/?${escaped_entry}/?$" "$exclude_file"; then
        printf '/%s\n' "$entry" >>"$exclude_file"
    fi

    if [[ "$entry" == */ ]]; then
        probe_path="${entry}.zephyr-skills-install-probe"
    else
        probe_path="$entry"
    fi

    git -C "$target_root" check-ignore --no-index -q "$probe_path" ||
        die "failed to configure local Git exclude for $entry"
}

main() {
    local target_dir="."
    local skill_source
    local target_root
    local saw_skill=0
    local saw_agent=0
    local saw_yes=0
    local arg
    local -a forwarded_args=()

    if [[ "${1:-}" == "install" ]]; then
        shift
    fi

    while [[ "$#" -gt 0 ]]; do
        arg="$1"
        case "$arg" in
            --target)
                [[ "$#" -ge 2 ]] || die "--target requires a directory"
                target_dir="$2"
                shift 2
                ;;
            -s|--skill)
                saw_skill=1
                forwarded_args+=("$arg")
                shift
                ;;
            -a|--agent)
                saw_agent=1
                forwarded_args+=("$arg")
                shift
                ;;
            -y|--yes)
                saw_yes=1
                forwarded_args+=("$arg")
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            -g|--global)
                die "global installation is not supported; run from a project root"
                ;;
            -l|--list|--all)
                die "$arg is not an install option for this script"
                ;;
            *)
                forwarded_args+=("$arg")
                shift
                ;;
        esac
    done

    require_command git
    require_command grep
    require_command npx
    require_command sed

    skill_source="$(resolve_skill_source)"
    target_root="$(resolve_target_root "$target_dir")"

    if [[ "$saw_skill" -eq 0 ]]; then
        forwarded_args+=(--skill '*')
    fi
    if [[ "$saw_agent" -eq 0 ]]; then
        forwarded_args+=(--agent codex claude-code)
    fi
    if [[ "$saw_yes" -eq 0 ]]; then
        forwarded_args+=(-y)
    fi

    printf 'Installing Zephyr agent skills into %s\n' "$target_root"
    (
        cd "$target_root"
        npx --yes skills add "$skill_source" "${forwarded_args[@]}"
    )

    for arg in "${REQUIRED_EXCLUDES[@]}"; do
        add_local_exclude "$target_root" "$arg"
    done

    printf 'Installed Zephyr agent skills.\n'
    printf 'Configured repository-local Git excludes in %s.\n' \
        "$(git -C "$target_root" rev-parse --git-path info/exclude)"
}

main "$@"
