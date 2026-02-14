import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"

def generate_response(ticket, ranked_solutions):
    solutions_text = "\n".join(
        [f"Solution {s['level']}: {s['text']}" for s in ranked_solutions]
    )

    # Guardrail present in prompt to prevent hallucination
    prompt = f"""
        You are a technical support assistant.
        Only use the information provided below. 
        Do not invent new steps.

        Ticket ID: {ticket['ticket_id']}
        System: {ticket['system']}

        Known solutions:
        {solutions_text}

        Generate a concise, structured troubleshooting response.
    """

    res = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=90
    )

    return res.json()["response"]