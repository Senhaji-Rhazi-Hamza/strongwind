#!/bin/sh
set -e

if [ ! -f "$DATA_PATH" ]; then
    gpu-obs data generate --path "$DATA_PATH"
fi

exec "$@"
