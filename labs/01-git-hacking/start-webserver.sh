#!/usr/bin/env bash

server_url="http://127.0.0.1:8000"
server_path="${WEBSERVER_PATH:-/lab-webserver}"

if curl --silent --fail --output /dev/null --max-time 1 "$server_url"; then
    exit 0
fi

{
    nohup python "$server_path/server.py" \
        > "$server_path/server.log" 2>&1 < /dev/null &
} 2>/dev/null

if ! curl --silent --fail --output /dev/null \
    --retry 10 \
    --retry-connrefused \
    --retry-delay 1 \
    --retry-max-time 5 \
    --max-time 1 \
    "$server_url"; then
    echo "Warning: The lab web server did not start on port 8000. Please contact your instructor." >&2
fi