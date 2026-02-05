#!/bin/bash
# Start script for Claw Personal Assistant

echo "Starting Claw Personal Assistant..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found, trying python..."
    if ! command -v python &> /dev/null; then
        echo "Error: Python is required but not installed."
        exit 1
    fi
    PYTHON_CMD=python
else
    PYTHON_CMD=python3
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
fi

# Start the assistant
echo "Starting assistant..."
$PYTHON_CMD claw_main.py