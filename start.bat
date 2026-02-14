@echo off

@REM Create Python virtual environment (only if it doesn't exist)
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

@REM Activate the virtual environment
call .venv\Scripts\activate.bat

@REM Install required Python packages
pip install -r requirements.txt

@REM Pull Ollama models (instead of running them)
@REM echo Pulling Ollama models...
ollama pull nomic-embed-text
ollama pull llama3.1:8b

@REM Start Ollama service in background (if not already running)
start /B ollama serve

@REM Wait a moment for Ollama to start
timeout /t 5 /nobreak

@REM Run the Streamlit application
streamlit run app.py