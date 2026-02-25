import os
import json

VECTOR_FOLDER = "vectorstore"

def get_top_topics():
    if not os.path.exists(VECTOR_FOLDER):
        return []
    
    all_text = []
    files = [f for f in os.listdir(VECTOR_FOLDER) if f.endswith("_chunks.json")]
    
    if not files:
        return []

    for file in files:
        with open(os.path.join(VECTOR_FOLDER, file), "r", encoding="utf-8") as f:
            chunks = json.load(f)
            all_text.extend(chunks)

    # Common JEE Topics to track
    keywords = ["Thermodynamics", "Organic", "Calculus", "Probability", "Mechanics", 
                "Optics", "Inorganic", "Integration", "Matrices", "Kinetics"]
    
    found = []
    text_blob = " ".join(all_text).lower()
    
    for kw in keywords:
        count = text_blob.count(kw.lower())
        if count > 0:
            found.append({"topic": kw, "count": count})
    
    return sorted(found, key=lambda x: x['count'], reverse=True)[:5]