#!/usr/bin/env bash
hook="$HOME/lab-repository/.git/hooks/pre-commit"
require_file "$hook"
[[ -x "$hook" ]]
