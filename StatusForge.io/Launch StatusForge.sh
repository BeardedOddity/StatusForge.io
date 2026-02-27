#!/bin/bash
# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to the virtual environment python
PYTHON_EXE="$DIR/venv/bin/python"

# --- THE AUTO-INSTALLER ---
# Check if venv exists, if not, forge the environment
if [ ! -f "$PYTHON_EXE" ]; then
    echo "==================================================="
    echo " 🛠️ STATUSFORGE: First-Time Setup Detected"
    echo "==================================================="
    echo "Forging the environment... Please wait."
    
    # Build the sandbox
    python3 -m venv "$DIR/venv"
    
    # Activate and install dependencies
    source "$DIR/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$DIR/requirements.txt"
    
    echo ""
    echo "==================================================="
    echo " ✅ Setup complete! Booting the engine..."
    echo "==================================================="
    sleep 3
fi
# --------------------------

# Run the engine in the background
nohup "$PYTHON_EXE" "$DIR/Engine/presence.py" > /dev/null 2>&1 &

echo "StatusForge Engine started in background (PID: $!)"
