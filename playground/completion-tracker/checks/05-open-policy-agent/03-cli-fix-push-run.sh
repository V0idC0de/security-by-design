#!/usr/bin/env bash
git_has_file "$HOME/demo-open-policy-agent" HEAD main.tf
git_has_file "$HOME/demo-open-policy-agent" HEAD settings.yaml
history_has 'git[[:space:]]+add[[:space:]].*main\.tf([[:space:]]|$)'
history_has 'git[[:space:]]+add[[:space:]].*settings\.yaml([[:space:]]|$)'
history_has 'git[[:space:]]+commit([[:space:]]|$)'
history_has 'git[[:space:]]+push([[:space:]]|$)'
