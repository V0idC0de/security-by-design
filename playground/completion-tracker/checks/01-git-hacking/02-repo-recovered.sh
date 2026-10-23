#!/usr/bin/env bash
require_command find
require_command git
[[ -d "$HOME/git-hack" ]] || exit 1
git_directory=$(find "$HOME/git-hack" -maxdepth 4 -type d -name .git -print -quit)
[[ -n "$git_directory" ]] || exit 1
git -C "${git_directory%/.git}" rev-parse --verify HEAD >/dev/null
