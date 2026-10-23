#!/usr/bin/env bash
require_file "$HOME/lab-project/sbom-os.json"
require_command jq
jq -e '.bomFormat == "CycloneDX" and any(.components[]; (.purl // "") | startswith("pkg:deb/"))' "$HOME/lab-project/sbom-os.json" >/dev/null
