#!/bin/bash

PROJECT_DIR="$HOME/tldrgen"
VENV_PATH="$PROJECT_DIR/.venv"
PYTHON_SCRIPT="$PROJECT_DIR/tldrgen.py"

if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi
"$VENV_PATH/bin/python3" "$PYTHON_SCRIPT" "$@"
