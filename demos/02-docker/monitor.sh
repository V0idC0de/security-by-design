#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

reset=$'\033[0m'
bold=$'\033[1m'
cyan=$'\033[36m'
yellow=$'\033[33m'
dim=$'\033[2m'

printf '%s%sDocker-Container%s\n' "$bold" "$cyan" "$reset"
printf '%s%s%s\n' "$dim" '----------------------------------------' "$reset"
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Mounts}}\t{{.Ports}}\t{{.Status}}'

printf '\n\n\n\n'
printf '%s%sContainer-Mounts%s\n' "$bold" "$cyan" "$reset"
printf '%s%s%s\n' "$dim" '----------------------------------------' "$reset"

has_mounts=false

while IFS= read -r container; do
    mounts=$(docker inspect -f '{{range .Mounts}}{{if eq .Type "volume"}}{{.Name}} -> {{.Destination}}{{"\n"}}{{end}}{{end}}' "$container")
    [[ -n "$mounts" ]] || continue

    has_mounts=true
    printf '%s  %s%s%s\n' "$yellow" "$bold" "$container" "$reset"

    while IFS= read -r mount; do
        [[ -n "$mount" ]] || continue
        printf '      %s%s%s\n' "$cyan" "$mount" "$reset"
    done <<< "$mounts"
done < <(docker ps --format '{{.Names}}')

if [[ "$has_mounts" == false ]]; then
    printf '%s--- Keine gemounteten Docker-Volumes gefunden ---%s\n' "$dim" "$reset"
fi

printf '\n\n\n'
printf '%s%sDocker-Volumes%s\n' "$bold" "$cyan" "$reset"
printf '%s%s%s\n' "$dim" '----------------------------------------' "$reset"

found=false

while IFS= read -r volume; do
    [[ "$volume" == demo* ]] || continue

    found=true
    printf '%s  📦  %s%s%s\n' "$yellow" "$bold" "$volume" "$reset"

    volume_path=$(docker volume inspect -f '{{.Mountpoint}}' "$volume")
    printf '      %sPfad:%s %s\n' "$dim" "$reset" "$volume_path"
    ls -l "$volume_path"
    printf '\n'
done < <(docker volume ls --format '{{.Name}}')

if [[ "$found" == false ]]; then
    printf '%s--- Keine demo-Volumes gefunden ---%s\n' "$dim" "$reset"
fi