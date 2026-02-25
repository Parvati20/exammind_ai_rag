# import os
# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from PyPDF2 import PdfReader

# DATA_FOLDER = "data"
# INDEX_FOLDER = "vectorstore"

# os.makedirs(INDEX_FOLDER, exist_ok=True)

# print("🚀 Loading embedding model...")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# def extract_text(pdf_path):
#     reader = PdfReader(pdf_path)
#     texts = []

#     for i, page in enumerate(reader.pages):
#         text = page.extract_text()
#         if text:
#             texts.append(text)

#         if i % 50 == 0:
#             print(f"Processed {i} pages...")

#     return texts

# def chunk_text(texts, chunk_size=800):
#     chunks = []
#     for text in texts:
#         for i in range(0, len(text), chunk_size):
#             chunks.append(text[i:i+chunk_size])
#     return chunks

# for file in os.listdir(DATA_FOLDER):
#     if file.endswith(".pdf"):
#         year = file.replace(".pdf", "")
#         pdf_path = os.path.join(DATA_FOLDER, file)
#         index_path = os.path.join(INDEX_FOLDER, f"{year}.index")

#         print(f"\n📄 Processing {file}")

#         texts = extract_text(pdf_path)
#         chunks = chunk_text(texts)

#         print("🧠 Generating embeddings...")
#         embeddings = model.encode(
#             chunks,
#             batch_size=32,
#             show_progress_bar=True
#         )

#         embeddings = np.array(embeddings).astype("float32")

#         dim = embeddings.shape[1]
#         index = faiss.IndexFlatL2(dim)
#         index.add(embeddings)

#         faiss.write_index(index, index_path)

#         print(f"✅ Index saved for {year}")

# print("🎉 All years processed successfully!")

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import PyPDF2

DATA_FOLDER = "data"
VECTOR_FOLDER = "vectorstore"

# Folder create karne ke liye safety check
os.makedirs(VECTOR_FOLDER, exist_ok=True)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def chunk_text(text, chunk_size=700): # Thoda bada chunk size context ke liye behtar hai
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

# ==========================================
# UNIVERSAL PROCESSOR (For Years & Uploads)
# ==========================================
def process_file(file_path, identifier):
    """
    file_path: PDF ka path
    identifier: '2020' ya 'javascript_notes' (file ka naam)
    """
    print(f"🚀 Processing: {identifier}...")

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        print(f"⚠️ No text found in {identifier}")
        return

    chunks = chunk_text(text)

    # Save chunks JSON
    chunk_path = os.path.join(VECTOR_FOLDER, f"{identifier}_chunks.json")
    with open(chunk_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f)

    # Create embeddings
    embeddings = embed_model.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    index_path = os.path.join(VECTOR_FOLDER, f"{identifier}.index")
    faiss.write_index(index, index_path)

    print(f"✅ Vector store ready for: {identifier}")

# Purana function jo ab naya logic use karega
def create_index_for_year(year):
    pdf_path = os.path.join(DATA_FOLDER, f"{year}.pdf")
    if os.path.exists(pdf_path):
        process_file(pdf_path, year)
    else:
        print(f"❌ {year}.pdf not found")

if __name__ == "__main__":
    # Initial setup for JEE papers
    years = ["2020", "2021", "2022", "2023", "2024", "2025"]
    for year in years:
        create_index_for_year(year)