#!/usr/bin/env bash
git_has_file "$HOME/lab-repository" HEAD sample.py
require_command grep
content=$(git -C "$HOME/lab-repository" show HEAD:sample.py)
if grep -q 'AKIA' <<< "$content"; then
    exit 1
else
    result=$?
    [[ "$result" == 1 ]] || exit "$result"
fi
