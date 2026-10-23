#!/usr/bin/env bash
require_file "$HOME/lab-repository/sample.py"
require_command grep
if grep -q 'AKIA' "$HOME/lab-repository/sample.py"; then
    exit 1
else
    result=$?
    [[ "$result" == 1 ]] || exit "$result"
fi
