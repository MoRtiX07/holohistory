"""
Hologram Persona Chatbot - Interactive Terminal CLI
Run it with:
    python chatbot.py einstein
    python chatbot.py kalam
    python chatbot.py tesla

Requires GEMINI_API_KEY environment variable (or set in .env file).
Get a free key at: https://aistudio.google.com/apikey
"""

import os
import sys
import time
import chromadb
from chromadb.utils import embedding_functions
from google import genai
from google.genai import types

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


DB_DIR = "chroma_db"
TOP_K = 3  # how many chunks of context to retrieve per question

PERSONA_SYSTEM_PROMPT = """You are simulating {name} for an educational demo project.

Answer every question in the first person, as if you were {name}, using the
CONTEXT below (drawn from their real writings/speeches/biography) as your
source of truth. Match their known speaking style and documented views as
closely as the context allows.

Rules:
- If the context does not contain enough information to answer confidently,
  say so honestly in character (e.g. "I don't believe I ever wrote about that")
  rather than inventing facts.
- Keep answers concise (3-6 sentences) and conversational, like a spoken reply.
- Never claim to have knowledge of events after {name}'s lifetime.

CONTEXT:
{context}
"""


def get_collection(persona_name):
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        return client.get_collection(name=persona_name, embedding_function=embed_fn)
    except Exception:
        raise SystemExit(
            f"No knowledge base found for '{persona_name}'. "
            f"Did you run build_knowledge_base.py first, and does data/{persona_name}.txt exist?"
        )


def retrieve_context(collection, question, k=TOP_K):
    results = collection.query(query_texts=[question], n_results=k)
    docs = results.get("documents", [[]])[0]
    return "\n\n---\n\n".join(docs) if docs else "(no relevant context found)"


def ask_llm(client, persona_name, question, context, max_retries=3):
    system_prompt = PERSONA_SYSTEM_PROMPT.format(name=persona_name.title(), context=context)

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    max_output_tokens=1024,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),  # skip internal reasoning tokens, keep full budget for the visible answer
                ),
                contents=question,
            )
            if response.text:
                return response.text
            return "(the model returned an empty response — try rephrasing the question)"
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries:
                    print(f"  (model busy, retrying... attempt {attempt}/{max_retries})")
                    time.sleep(3)
                    continue
                return "(the model is overloaded right now — please try again in a moment)"
            raise


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python chatbot.py <persona_name>\nExample: python chatbot.py einstein")

    persona_name = sys.argv[1].lower()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit(
            "GEMINI_API_KEY environment variable not set.\n"
            "Get a free key at https://aistudio.google.com/apikey and set it with:\n"
            "  export GEMINI_API_KEY=your_key_here   (Mac/Linux)\n"
            "  set GEMINI_API_KEY=your_key_here       (Windows cmd)"
        )

    collection = get_collection(persona_name)
    client = genai.Client(api_key=api_key)

    print(f"\nChatting with {persona_name.title()}. Type 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue

        context = retrieve_context(collection, question)
        answer = ask_llm(client, persona_name, question, context)
        print(f"\n{persona_name.title()}: {answer}\n")


if __name__ == "__main__":
    main()
