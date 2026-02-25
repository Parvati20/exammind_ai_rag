import os
import json
import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

VECTOR_FOLDER = "vectorstore"
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
# Safety fallback for API URL
NVIDIA_API_URL = os.getenv("NVIDIA_API_URL") or "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_index(year):
    path = os.path.join(VECTOR_FOLDER, f"{year}.index")
    return faiss.read_index(path) if os.path.exists(path) else None

def load_chunks(year):
    path = os.path.join(VECTOR_FOLDER, f"{year}_chunks.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def retrieve_chunks(query, k=20):
    if not os.path.exists(VECTOR_FOLDER): return []
    years = [f.replace(".index", "") for f in os.listdir(VECTOR_FOLDER) if f.endswith(".index")]
    query_vector = np.array(embed_model.encode([query])).astype("float32")
    
    collected = []
    for year in years:
        idx = load_index(year)
        chnks = load_chunks(year)
        if idx and chnks:
            D, I = idx.search(query_vector, 5)
            for i in I[0]:
                if i < len(chnks): collected.append(f"[{year}] {chnks[i]}")
    return collected[:k]

def call_llama(prompt):
    url = f"{NVIDIA_API_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    
    payload = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "system", "content": "You are a Senior JEE Analyst. Provide trends and weightage analysis. No MCQs."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"API Error: {r.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

def ask_question(query):
    chunks = retrieve_chunks(query)
    if not chunks:
        return {"query": query, "answer": "Context not found in database."}
    
    answer = call_llama(f"Analyze these exam patterns: {' '.join(chunks)}\n\nQuery: {query}")
    return {"query": query, "answer": answer}