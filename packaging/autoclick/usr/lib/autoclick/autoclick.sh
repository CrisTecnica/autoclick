#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
if [ -f "$DIR/venv/bin/python3" ]; then
    exec "$DIR/venv/bin/python3" "$DIR/main.py" "$@"
else
    exec python3 "$DIR/main.py" "$@"
fi
