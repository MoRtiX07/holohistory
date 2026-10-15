"""
Step 3 of the project: turn each persona's text file into a searchable
knowledge base (a vector database).

Run this ONCE (and again whenever you edit/add files in data/):
    python build_knowledge_base.py

What it does:
1. Reads every .txt file in data/  (filename without extension = persona name)
2. Splits the text into small overlapping chunks
3. Embeds each chunk into a vector using a free local embedding model
4. Stores everything in a local Chroma database folder: chroma_db/
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = "data"
DB_DIR = "chroma_db"
CHUNK_SIZE = 500      # characters per chunk
CHUNK_OVERLAP = 100    # overlap so we don't cut sentences awkwardly


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks, breaking on paragraph boundaries where possible."""
    text = re.sub(r"\n{2,}", "\n\n", text.strip())
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and not p.strip().startswith("#")]

    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) <= chunk_size:
            current += ("\n\n" if current else "") + para
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)

    # add simple overlap between consecutive chunks
    overlapped = []
    for i, c in enumerate(chunks):
        if i > 0:
            tail = chunks[i - 1][-overlap:]
            c = tail + " " + c
        overlapped.append(c)
    return overlapped


def main():
    if not os.path.isdir(DATA_DIR):
        raise SystemExit(f"No '{DATA_DIR}' folder found. Create it and add persona .txt files first.")

    txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]
    if not txt_files:
        raise SystemExit(f"No .txt files found in '{DATA_DIR}'. Add at least one persona file first.")

    print("Loading embedding model (first run downloads it, ~90MB)...")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=DB_DIR)

    for filename in txt_files:
        persona_name = os.path.splitext(filename)[0]
        filepath = os.path.join(DATA_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        chunks = chunk_text(raw_text)
        if not chunks:
            print(f"  Skipping {filename} — no usable text found.")
            continue

        # one collection per persona, rebuilt fresh each time
        try:
            client.delete_collection(persona_name)
        except Exception:
            pass
        collection = client.create_collection(name=persona_name, embedding_function=embed_fn)

        ids = [f"{persona_name}_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)

        print(f"  {persona_name}: {len(chunks)} chunks indexed")

    print(f"\nDone. Knowledge base saved to '{DB_DIR}/'. Personas available: {[os.path.splitext(f)[0] for f in txt_files]}")


if __name__ == "__main__":
    main()
