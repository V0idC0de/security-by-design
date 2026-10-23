#!/usr/bin/env bash
git_has_file "$HOME/demo-workflows" HEAD sample.yaml
count=$(git -C "$HOME/demo-workflows" rev-list --count HEAD -- sample.yaml)
[[ "$count" -ge 2 ]]
