#!/usr/bin/env bash
require_file "$HOME/lab-project/sbom.json"
require_command jq
jq -e '.bomFormat == "CycloneDX" and (.components | map(.name) | sort) == ["certifi", "charset-normalizer", "idna", "requests", "urllib3"]' "$HOME/lab-project/sbom.json" >/dev/null
