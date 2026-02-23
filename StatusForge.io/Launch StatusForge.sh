#!/bin/bash
# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the virtual environment python
PYTHON_EXE="$DIR/venv/bin/python"

# Check if venv exists, if not, alert user
if [ ! -f "$PYTHON_EXE" ]; then
    echo "Error: Virtual Environment not found at $PYTHON_EXE"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Run the engine in the background
nohup "$PYTHON_EXE" "$DIR/Engine/presence.py" > /dev/null 2>&1 &

echo "StatusForge Engine started in background (PID: $!)"