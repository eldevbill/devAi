#!/bin/bash

# This script is a wrapper to run the Crypto AI Orchestrator Python script.
# It ensures that the Python script is executed with the correct interpreter and dependencies.

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Path to the Python orchestrator script
PYTHON_SCRIPT="$SCRIPT_DIR/crypto_ai_orchestrator.py"

# Path to the virtual environment
VENV_DIR="$SCRIPT_DIR/.venv"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python orchestrator script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment and install dependencies
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Install dependencies from requirements.txt
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies from requirements.txt."
        exit 1
    fi
else
    echo "Warning: requirements.txt not found. Skipping dependency installation."
fi

# Execute the Python script with all arguments passed to this shell script
python3 "$PYTHON_SCRIPT" "$@"
