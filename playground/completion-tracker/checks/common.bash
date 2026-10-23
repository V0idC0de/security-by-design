set -euo pipefail

require_command() {
    command -v "$1" >/dev/null || { printf 'Missing tool: %s\n' "$1" >&2; return 2; }
}

require_file() {
    [[ -f "$1" ]] || return 1
    [[ -r "$1" ]] || { printf 'File is not readable.\n' >&2; return 2; }
}

history_has() {
    local history_file=${HISTFILE:-"$HOME/.bash_history"}
    require_file "$history_file" || return $?
    require_command grep || return $?
    grep -Eq -- "^[[:space:]]*((command|sudo)[[:space:]]+)?$1" "$history_file"
}

git_has_file() {
    local repository=$1 reference=$2 filename=$3
    require_command git || return $?
    [[ -d "$repository/.git" ]] || return 1
    if git -C "$repository" cat-file -e "$reference:$filename" 2>/dev/null; then
        return 0
    fi
    return 1
}

terraform_apply_run() {
    history_has "terraform([[:space:]]+-chdir=[^[:space:]]+)?[[:space:]]+apply[[:space:]].*-var-file([=[:space:]]+)[\"']?(\./)?inputs/sample\\.$1\\.tfvars\\.json([\"'[:space:]]|$)"
}
