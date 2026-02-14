import faiss
import numpy as np
import os
import pickle
import requests
from tqdm import tqdm
from backend.ranker import recency_score


OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

INDEX_PATH = "data/ticket_index.faiss"
TICKETS_PATH = "data/tickets.pkl"

def embed(texts):
    """
    Get embeddings for a list of texts using the Ollama embedding model.

    Args:
        texts (list): List of strings to embed.
    Returns:
        np.ndarray: Array of embeddings.
    """
    vectors = []
    for text in tqdm(texts, desc="Generating embeddings", unit="ticket"):
        try:
            res = requests.post(
                OLLAMA_EMBED_URL,
                json={"model": EMBED_MODEL, "prompt": text},
                timeout=60
            )
            res.raise_for_status()
            response_data = res.json()
            
            # Check if the response contains the expected key
            if "embedding" in response_data:
                vec = response_data["embedding"]
            else:
                raise ValueError(f"Unexpected response format from Ollama API. Response: {response_data}")
            
            vectors.append(vec)
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get embeddings from Ollama. Make sure Ollama is running and the model '{EMBED_MODEL}' is installed. Error: {e}")
    
    return np.array(vectors).astype("float32")


class VectorSearch:
    """
    A simple vector store using FAISS for similarity search.

    Args:
        tickets (list): List of support ticket dictionaries.

    Methods:
        search(query, k=3): Search for the top-k similar tickets to the query.
    """
    def __init__(self, tickets):
        if os.path.exists(INDEX_PATH) and os.path.exists(TICKETS_PATH):
            print("Loading existing FAISS index and tickets...")
            self.index = faiss.read_index(INDEX_PATH)

            with open(TICKETS_PATH, "rb") as f:
                self.tickets = pickle.load(f)
        else:
            print(f"Building FAISS index for first run....")
            self.tickets = tickets
            texts = [t["problem_text"] for t in tickets]
            self.embeddings = embed(texts)

            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            faiss.normalize_L2(self.embeddings)
            self.index.add(self.embeddings)

            # Save the index and tickets for future use
            faiss.write_index(self.index, INDEX_PATH)
            with open(TICKETS_PATH, "wb") as f:
                pickle.dump(tickets, f)

    def search(self, query, k=3):
        q_emb = embed([query])
        faiss.normalize_L2(q_emb)
        scores, idxs = self.index.search(q_emb, k)

        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if score < 0.5:
                continue
            ticket = self.tickets[idx]
            recency = recency_score(ticket.get("finished_datetime"))
            vector_final_score = 0.7 * score + 0.3 * recency
            results.append({
                "ticket": ticket,
                "similarity": float(score),
                "recency": float(recency),
                "vector_final_score": float(vector_final_score)
            })

        results.sort(key=lambda x: x["vector_final_score"], reverse=True)
        return results