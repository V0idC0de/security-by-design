#!/usr/bin/env bash
config="$HOME/lab-repository/.pre-commit-config.yaml"
require_file "$config"
[[ -s "$config" ]]
