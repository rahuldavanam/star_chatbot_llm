#!/bin/bash
set -e

# Create Python virtual environment (only if it doesn't exist)
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Pull Ollama models (instead of running them)
# echo "Pulling Ollama models..."
ollama pull nomic-embed-text
ollama pull llama3.1:8b

# Start Ollama service in background (if not already running)
ollama serve &

# Wait a moment for Ollama to start
sleep 5

# Run the Streamlit application
streamlit run app.py