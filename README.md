# IT Support Ticket Chatbot

AI-powered technical support assistant that provides troubleshooting solutions based on historical ticket data using RAG (Retrieval-Augmented Generation).

## Setup

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running locally

### Installation

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod -R u+w .
chmod +x start.sh
./start.sh
```

**IMPORTANT:** Ensure all read and write permission are given for the folders and files while running in Linux.

This will:
1. Create a Python virtual environment (`.venv`)
2. Install all dependencies from `requirements.txt`
3. Pull required Ollama models (`nomic-embed-text`, `llama3.1:8b`)
4. Start Ollama service in the background
5. Launch the Streamlit application

### Manual Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows: 
.venv\Scripts\activate
# Linux/Mac: 
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull nomic-embed-text
ollama pull llama3.1:8b

# Start Ollama (if not running)
ollama serve

# Run the app
streamlit run app.py
```

## Usage

1. **Enter your issue:** Describe your technical problem in the text area
2. **Find solutions:** Click "Find Solutions" to search historical tickets
3. **Review AI response:** Read the AI-generated troubleshooting guide
4. **Try recommended solutions:** Expand each solution to see detailed steps
5. **Provide feedback:** 
   - Click "This solution worked" if successful (increments success + attempt count)
   - Click "This solution didn't work" if unsuccessful (increments attempt count only)
   - Click "None of the solutions worked" to report all solutions as unsuccessful
6. **System learns:** Feedback updates the ranking algorithm for future queries

## Architecture

### Technology Stack
- **Frontend:** Streamlit web interface
- **Vector Database:** FAISS (Facebook AI Similarity Search) with cosine similarity
- **Embeddings:** Ollama nomic-embed-text model (768-dimensional vectors)
- **LLM:** Ollama Llama 3.1 (8B parameter model) for response generation
- **Feedback Store:** SQLite database (`data/feedback.db`)
- **Data Source:** Excel file (`data/tickets_dataset.xlsx`) with historical support tickets

### Backend Modules
- **`data_loader.py`:** Loads and parses ticket data from Excel (includes safe datetime parsing)
- **`embedding_search.py`:** Generates embeddings and performs vector similarity search
- **`ranker.py`:** Ranks solutions using feedback score, recency, and escalation penalty
- **`feedback.py`:** Manages SQLite database for tracking solution success rates
- **`llm.py`:** Interfaces with Ollama for AI-generated troubleshooting responses

### Scoring System

**Vector Search Score:**
```
final_score = 0.7 × similarity_score + 0.3 × recency_score
```
- Similarity threshold: 0.5 (tickets below this are filtered out)
- Recency decay: exponential with 180-day half-life

**Solution Ranking Score:**
```
final_score = 0.7 × feedback_score - 0.1 × (level - 1)
```
- Feedback uses Laplace smoothing: `(success_count + 1) / (attempt_count + 1)`
- Escalation penalty: prioritizes lower-level solutions (Solution 1 > Solution 2 > Solution 3)

## Key Features

- **Semantic Search:** Uses FAISS vector similarity to find relevant historical tickets (not just keyword matching).
- **Persistent Embeddings:** Pre-loads FAISS index and embeddings from `data/` if available; generates and saves them on first run for faster startup.
- **Hybrid Scoring:** Combines semantic similarity with recency weighting for better ticket matching
- **AI-Powered Responses:** Generates structured troubleshooting guides using Llama 3.1
- **Multi-Level Solutions:** Ranks up to 3 solution levels with success rate and recency metrics
- **Adaptive Ranking:** Updates solution priorities based on user feedback with Laplace smoothing
- **Feedback Tracking:** Persistent SQLite database tracks success/attempt counts per ticket-solution pair
- **Guardrails:**
  - Similarity threshold prevents irrelevant matches
  - LLM prompt instructs not to hallucinate solutions
  - Fallback message when no similar tickets found
- **Local & Private:** Runs entirely on local hardware using Ollama (no data sent to external APIs)

## Assumptions & Design Decisions

- **Similarity threshold:** Tickets with cosine similarity < 0.5 are considered irrelevant
- **Solution independence:** Solutions can be tried in any order (though ranking suggests optimal sequence)
- **Recency bias:** Newer tickets weighted higher due to system updates and evolving issues
- **Escalation hierarchy:** Lower-level solutions preferred (reflect typical troubleshooting workflow)
- **Mature solutions prioritized:** Laplace smoothing prevents new solutions with 1/1 success from dominating
- **Single-ticket retrieval:** System returns best matching ticket (k=1) to avoid overwhelming users
- **Feedback model:**
  - "This solution worked": `success_count += 1`, `attempt_count += 1`
  - "This solution didn't work": `attempt_count += 1` only
  - "None worked": increments attempt count for all solutions on matched ticket