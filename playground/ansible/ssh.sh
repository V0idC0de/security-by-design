#!/usr/bin/env bash

config="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../ssh" && pwd)/config"
host="$(awk '/^[[:space:]]*Host[[:space:]]+/ { print $2; exit }' "$config")"

exec ssh -F "$config" "$host" "$@"
