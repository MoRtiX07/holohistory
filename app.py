"""
Hologram Persona Chatbot - FastAPI Server
Provides REST API endpoints, authentic persona simulation, QR code generation,
and serves the modern holographic web interface.
"""

import os
import io
import sys
import socket
import glob
import re
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except (ImportError, Exception):
    CHROMA_AVAILABLE = False
    chromadb = None
    embedding_functions = None
from google import genai
from google.genai import types
import qrcode
from PIL import Image, ImageDraw, ImageOps
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.isdir(DATA_DIR):
    for candidate in [os.path.join(os.getcwd(), "data"), os.path.join(os.path.dirname(BASE_DIR), "data")]:
        if os.path.isdir(candidate):
            DATA_DIR = candidate
            break

DB_DIR = os.path.join(BASE_DIR, "chroma_db")
IMAGES_DIR = os.path.join(BASE_DIR, "static", "images")
if not os.path.isdir(IMAGES_DIR):
    for candidate in [os.path.join(os.getcwd(), "static", "images"), os.path.join(os.path.dirname(BASE_DIR), "static", "images")]:
        if os.path.isdir(candidate):
            IMAGES_DIR = candidate
            break
os.makedirs(IMAGES_DIR, exist_ok=True)
TOP_K = 3
MASTER_PIN = "1879"  # Year Einstein was born


def get_local_ip():
    """Returns machine LAN IP address so phones on the same Wi-Fi can connect."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_tunnel_url():
    """Detects active public Cloudflare sharing tunnel URL."""
    # 1. Environment variable
    env_url = os.environ.get("PUBLIC_TUNNEL_URL")
    if env_url:
        return env_url.rstrip("/")

    # 2. Local cached .tunnel_url file
    tunnel_file = os.path.join(BASE_DIR, ".tunnel_url")
    if os.path.exists(tunnel_file):
        try:
            with open(tunnel_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("http"):
                    return content.rstrip("/")
        except Exception:
            pass

    # 3. No active tunnel found

    return None

PERSONA_METADATA = {
    "einstein": {
        "id": "einstein",
        "name": "Albert Einstein",
        "title": "Theoretical Physicist & Nobel Laureate",
        "era": "1879 - 1955",
        "accent": "#00f0ff",
        "glow": "rgba(0, 240, 255, 0.4)",
        "tagline": "Discoverer of Special & General Relativity, Quantum Light pioneer",
        "quote": "Imagination is more important than knowledge.",
        "avatarUrl": "/images/einstein_avatar.jpg",
        "starters": [
            "How did you first conceive of Special Relativity?",
            "Tell me about the compass your father gave you as a child.",
            "What were your views on world peace and humanity?",
            "Why did you leave Germany for Princeton?"
        ],
        "categories": {
            "Discoveries": [
                "How did you first conceive of Special Relativity?",
                "Can you explain why nothing can travel faster than light?",
                "What is your famous equation E=mc² really telling us?"
            ],
            "Childhood": [
                "Tell me about the compass your father gave you as a child.",
                "Were you really bad at mathematics in school as the myth says?",
                "What did you love most about playing the violin as a young man?"
            ],
            "Philosophy": [
                "Why did you say 'God does not play dice with the universe'?",
                "What are your views on world peace and international cooperation?",
                "What is the connection between music, simplicity, and science?"
            ],
            "Advice": [
                "What is your advice to a student trying to understand physics?",
                "How can one cultivate true creative imagination?"
            ]
        },
        "milestones": [
            {"year": "1879", "event": "Born in Ulm, Germany; early wonder with father's pocket compass"},
            {"year": "1905", "event": "Annus Mirabilis: Published Special Relativity, E=mc², Photoelectric Effect"},
            {"year": "1915", "event": "Completed General Relativity: Gravity as curvature of spacetime"},
            {"year": "1921", "event": "Awarded Nobel Prize in Physics for discovery of photoelectric law"},
            {"year": "1933", "event": "Emigrated to Princeton Institute for Advanced Study in New Jersey"},
            {"year": "1939", "event": "Warned Roosevelt of atomic possibilities; championed pacifism"}
        ],
        "artifacts": [
            {
                "id": "relativity",
                "title": "Spacetime Curvature & E=mc²",
                "year": "1915",
                "tag": "GENERAL RELATIVITY",
                "image": "/images/einstein_relativity_artifact.jpg",
                "summary": "Geometrical theory proving matter curves the 4D fabric of space and time.",
                "prompt": "Explain your discovery of spacetime curvature and how mass bends the paths of light."
            },
            {
                "id": "photoelectric",
                "title": "Quantum Light & Photoelectric Effect",
                "year": "1905",
                "tag": "NOBEL PRIZE",
                "image": "/images/einstein_photoelectric_artifact.jpg",
                "summary": "Proved light travels in discrete packets of energy (photons), launching quantum physics.",
                "prompt": "How did your 1905 photoelectric paper prove that light behaves like discrete packets of energy?"
            }
        ],
        "surprises": [
            "Tell me about 'Lina', your cherished violin, and how playing Mozart helped you think through physics.",
            "Is it true you never wore socks, and why was simplicity so sacred to your worldview?",
            "Recount the dramatic 1919 solar eclipse expedition that proved your theory of general relativity.",
            "Why did you decline the offer to become the President of Israel in 1952?"
        ],
        "voiceSettings": {
            "pitch": 0.90,
            "rate": 0.92,
            "voiceKeywords": ["german", "david", "george", "male", "mature", "en-gb", "en-us"]
        },
        "voiceGuidance": """
Tone & Mannerisms for Albert Einstein:
- Speak with gentle warmth, modesty, philosophical depth, and playful curiosity.
- Address the inquirer warmly (e.g., 'My friend', 'You see, my dear friend').
- Frequently explain physics using intuitive thought experiments (riding a beam of light, clocks on trains, bending space like fabric).
- Reflect on simplicity, your love for Mozart and the violin, your time at the Bern patent office, and your unyielding commitment to pacifism, civil rights, and human fellowship.
- Use natural conversational cadences reflecting your German-Swiss heritage.
"""
    },
    "kalam": {
        "id": "kalam",
        "name": "Dr. A.P.J. Abdul Kalam",
        "title": "11th President of India & Aerospace Scientist",
        "era": "1931 - 2015",
        "accent": "#ffb703",
        "glow": "rgba(255, 183, 3, 0.4)",
        "tagline": "The Missile Man of India, Visionary Educator & Author of Wings of Fire",
        "quote": "Dreams are not what you see in sleep, they are things which do not let you sleep.",
        "avatarUrl": "/images/kalam_avatar.jpg",
        "starters": [
            "What was your childhood like in Rameswaram?",
            "How did you overcome the failure of the first SLV-3 launch?",
            "What is your message to young dreamers and students?",
            "Tell me about your Vision 2020 for a developed India."
        ],
        "categories": {
            "Space & Missiles": [
                "How did you overcome the failure of the first SLV-3 launch?",
                "What was the pivotal moment during the Pokhran-II tests in 1998?",
                "What was your role in developing the Agni and Prithvi missiles?"
            ],
            "Childhood": [
                "What was your childhood like in Rameswaram?",
                "How did your father's boat business and your mother shape your character?",
                "How did distributing newspapers teach you the value of discipline?"
            ],
            "Youth Dreams": [
                "What is your message to young dreamers and students?",
                "Why do you say dreams transform into thoughts, and thoughts into action?",
                "How can a student from a modest background achieve great heights?"
            ],
            "Vision 2020": [
                "Tell me about your Vision 2020 for a developed India.",
                "How can technology and education transform rural villages?"
            ]
        },
        "milestones": [
            {"year": "1931", "event": "Born in Rameswaram, Tamil Nadu; sold newspapers to support education"},
            {"year": "1960", "event": "Graduated in Aerospace Engineering from Madras Institute of Technology"},
            {"year": "1980", "event": "Project Director for India's first SLV-3; launched Rohini satellite"},
            {"year": "1998", "event": "Chief Scientific Adviser & architect of Pokhran-II; authored Vision 2020"},
            {"year": "1999", "event": "Published inspirational autobiography 'Wings of Fire'"},
            {"year": "2002", "event": "Elected 11th President of India ('The People's President')"}
        ],
        "artifacts": [
            {
                "id": "slv3",
                "title": "SLV-3 Rocket & Rohini Mission",
                "year": "1980",
                "tag": "ISRO SPACE LAUNCH",
                "image": "/images/kalam_rocket_artifact.jpg",
                "summary": "India's first satellite launch vehicle, injecting Rohini RS-1 successfully into orbit.",
                "prompt": "Recount the historic July 18, 1980 launch of SLV-3 and how your team overcame early failures."
            },
            {
                "id": "missiles",
                "title": "Guided Missiles & Defense Systems",
                "year": "1989",
                "tag": "AGNI & PRITHVI",
                "image": "/images/kalam_vision_artifact.jpg",
                "summary": "Indigenous aerospace defense technology establishing India's strategic self-reliance.",
                "prompt": "Explain the engineering challenges in developing India's Agni and Prithvi missile programs."
            }
        ],
        "surprises": [
            "Tell me about the 1979 SLV-3 crash into the Bay of Bengal and the leadership lesson Prof. Satish Dhawan taught you.",
            "How did your morning walks in Rameswaram watching sea birds spark your lifelong dream of flying?",
            "What happened during the top-secret desert preparations for Pokhran-II in 1998?",
            "Why did you prefer teaching and mentoring young students over political ceremonial events?"
        ],
        "voiceSettings": {
            "pitch": 1.08,
            "rate": 0.98,
            "voiceKeywords": ["india", "en-in", "hi-in", "ravi", "veena", "prabhat", "mohan"]
        },
        "voiceGuidance": """
Tone & Mannerisms for Dr. A.P.J. Abdul Kalam:
- Speak with affectionate warmth, infectious humility, optimism, and deep spiritual discipline.
- Address the user kindly as 'my young friend', 'dear student', or 'fellow dreamer'.
- Emphasize hard work, learning from failures (like the first SLV-3 satellite launch), and having an indomitable spirit.
- Fondly recall your childhood in Rameswaram distributing newspapers, your parents' values, your teachers, and your work at ISRO/DRDO.
- Always inspire courage and self-reliance: 'Dreams transform into thoughts, and thoughts result in action.'
"""
    },
    "tesla": {
        "id": "tesla",
        "name": "Nikola Tesla",
        "title": "Inventor, Futurist & Electrical Pioneer",
        "era": "1856 - 1943",
        "accent": "#bd00ff",
        "glow": "rgba(189, 0, 255, 0.4)",
        "tagline": "Father of Alternating Current, Wireless Energy Visionary",
        "quote": "If you want to find the secrets of the universe, think in terms of energy, frequency and vibration.",
        "avatarUrl": "/images/tesla_avatar.jpg",
        "starters": [
            "How does your alternating current (AC) motor work?",
            "What really happened during the War of the Currents with Edison?",
            "What was your grand vision for the Wardenclyffe Tower?",
            "Can you explain how you visualize inventions before building them?"
        ],
        "categories": {
            "AC & Inventions": [
                "How does your alternating current (AC) motor work?",
                "What inspired the design of the famous Tesla Coil?",
                "How did your remote-controlled boat demonstration shock the public in 1898?"
            ],
            "Mental Lab": [
                "Can you explain how you visualize inventions before building them?",
                "How did your mother's mechanical inventions inspire your boyhood?",
                "How did you visualize the rotating magnetic field while walking in Budapest?"
            ],
            "War of Currents": [
                "What really happened during the War of the Currents with Edison?",
                "How did your partnership with George Westinghouse change the world?",
                "What was it like illuminating the 1893 Chicago World's Fair?"
            ],
            "Wardenclyffe": [
                "What was your grand vision for the Wardenclyffe Tower?",
                "Do you believe free wireless energy will one day power the earth?"
            ]
        },
        "milestones": [
            {"year": "1856", "event": "Born in Smiljan during a midnight lightning storm"},
            {"year": "1882", "event": "Visualized rotating magnetic field in Budapest park reciting Faust"},
            {"year": "1888", "event": "Patented AC Polyphase Induction Motor; partnered with Westinghouse"},
            {"year": "1893", "event": "Illuminated Chicago World's Columbian Exposition using AC power"},
            {"year": "1898", "event": "Demonstrated world's first radio-controlled teleautomaton boat"},
            {"year": "1901", "event": "Constructed Wardenclyffe Tower in Shoreham for wireless global power"}
        ],
        "artifacts": [
            {
                "id": "tesla_coil",
                "title": "AC Motor & Resonant Tesla Coil",
                "year": "1893",
                "tag": "ELECTRICAL RESONANCE",
                "image": "/images/tesla_coil_artifact.jpg",
                "summary": "Polyphase AC motor and resonant high-voltage transformer generating millions of volts.",
                "prompt": "Demonstrate the operating principle of your alternating current motor and high-voltage Tesla Coil."
            },
            {
                "id": "wardenclyffe",
                "title": "Wardenclyffe Wireless Global Tower",
                "year": "1901",
                "tag": "WIRELESS ENERGY",
                "image": "/images/tesla_wardenclyffe_artifact.jpg",
                "summary": "Worldwide wireless power and message broadcasting tower utilizing Earth resonance.",
                "prompt": "Describe your grand vision for Wardenclyffe Tower and transmitting wireless electricity across the planet."
            }
        ],
        "surprises": [
            "Describe the moment in Budapest park in 1882 when you suddenly saw the rotating magnetic field and drew it with a stick.",
            "What strange phenomenon occurred inside your Colorado Springs lab during the artificial lightning experiments in 1899?",
            "Tell me about your friendship with Mark Twain and the experiments he participated in at your lab.",
            "Why did you believe the numbers 3, 6, and 9 held the key to understanding the entire universe?"
        ],
        "voiceSettings": {
            "pitch": 0.88,
            "rate": 1.02,
            "voiceKeywords": ["european", "croatian", "serbian", "slavic", "richard", "oliver", "en-gb"]
        },
        "voiceGuidance": """
Tone & Mannerisms for Nikola Tesla:
- Speak with visionary intensity, refined European eloquence, and passionate devotion to electrical science.
- Describe how you visualize inventions entirely within your mind in precise detail before touching physical materials.
- Speak with reverence about electrical resonance, the rotating magnetic field, high-frequency currents, and your wireless energy dreams at Wardenclyffe.
- Refer with dignified clarity to the War of the Currents and your conviction that alternating current is nature's true harmony.
- Express your profound conviction: 'The present is theirs; the future, for which I really worked, is mine.'
"""
    }
}

PERSONA_SYSTEM_TEMPLATE = """You are simulating {name} ({era}) for an interactive educational hologram exhibit.

Answer every question strictly in the first person as {name}, using the CONTEXT below (drawn from real historical writings, speeches, and biographical records) as your primary source of truth.

{voice_guidance}

Rules:
1. Speak authentically in character with the exact personality, tone, vocabulary, and worldview described above.
2. Ground your factual claims in the CONTEXT below. If the context does not cover the question, state so honestly in character (e.g., "I don't recall writing or speaking on that matter during my lifetime").
3. Strictly maintain the historical horizon: Never claim to know about events, technologies, or people after your lifetime ({era}).
4. Deliver answers rapidly in 2 to 3 concise, captivating sentences (around 35 to 60 words total). Get straight to the core essence with zero delay or filler, speaking directly from the hologram emitter.

CONTEXT:
{context}
"""

app = FastAPI(title="Hologram Persona Chatbot API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients cached in memory
_embed_fn = None
_chroma_client = None
_gemini_client = None


def get_embed_fn():
    global _embed_fn
    if not CHROMA_AVAILABLE:
        return None
    if _embed_fn is None:
        _embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _embed_fn


def get_chroma_client():
    global _chroma_client
    if not CHROMA_AVAILABLE:
        return None
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path=DB_DIR)
    return _chroma_client


def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
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

    overlapped = []
    for i, c in enumerate(chunks):
        if i > 0:
            tail = chunks[i - 1][-overlap:]
            c = tail + " " + c
        overlapped.append(c)
    return overlapped


STOP_WORDS = {
    'what', 'when', 'where', 'which', 'who', 'whom', 'whose', 'why', 'how',
    'your', 'you', 'about', 'did', 'tell', 'explain', 'describe', 'were', 'was',
    'are', 'is', 'the', 'and', 'that', 'this', 'for', 'with', 'from', 'have',
    'had', 'has', 'not', 'but', 'can', 'could', 'would', 'should', 'all', 'any',
    'like', 'such', 'into', 'some', 'more', 'most', 'been', 'being', 'their', 'them',
    'they', 'there', 'here', 'than', 'then', 'also', 'just', 'well', 'much', 'many',
    'does', 'do', 'doing', 'give', 'me', 'my', 'his', 'her', 'our'
}


def _stem_word(word: str) -> str:
    for suffix in ('hood', 'ing', 'tion', 'ness', 'ment', 'ies', 'es', 's', 'ed', 'ly', 'al', 'ic', 'ity'):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[:-len(suffix)]
    return word


def _score_chunk(chunk: str, question: str) -> float:
    c_low = chunk.lower()
    q_low = question.lower()
    clean_q = re.sub(r'[^\w\s]', ' ', q_low).strip()
    words = [w for w in clean_q.split() if w not in STOP_WORDS and len(w) > 2]
    
    score = 0.0
    if len(clean_q) > 4 and clean_q in c_low:
        score += 50.0
        
    c_words = [re.sub(r'[^\w]', '', w) for w in c_low.split()]
    c_stems = [_stem_word(w) for w in c_words if len(w) > 2]
    
    for w in words:
        w_stem = _stem_word(w)
        if w in c_words:
            score += 10.0 * min(c_words.count(w), 5)
        elif w_stem in c_stems:
            score += 8.0 * min(c_stems.count(w_stem), 5)
        elif len(w_stem) >= 4 and any(w_stem in s or s in w_stem for s in c_stems):
            score += 4.0
            
    return score


def retrieve_fallback_context(persona_name: str, question: str, k: int = TOP_K):
    """Direct in-memory knowledge retrieval with high-precision scoring matching ChromaDB."""
    persona_file = os.path.join(DATA_DIR, f"{persona_name}.txt")
    if not os.path.isfile(persona_file):
        return "(no relevant context found)", []
    try:
        with open(persona_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
        chunks = chunk_text(raw_text)
        if not chunks:
            return "(no relevant context found)", []
        
        scored = sorted([(_score_chunk(c, question), c) for c in chunks], key=lambda x: x[0], reverse=True)
        top_chunks = [c for _, c in scored[:k]]
        return "\n\n---\n\n".join(top_chunks), top_chunks
    except Exception as e:
        print(f"Fallback retrieval error for {persona_name}: {e}")
        return "(no relevant context found)", []


def get_collection(persona_name: str):
    if not CHROMA_AVAILABLE:
        return None
    client = get_chroma_client()
    if not client:
        return None
    embed_fn = get_embed_fn()
    try:
        return client.get_collection(name=persona_name, embedding_function=embed_fn)
    except Exception:
        # Auto-build collection from data/{persona_name}.txt if available
        persona_file = os.path.join(DATA_DIR, f"{persona_name}.txt")
        if os.path.isfile(persona_file):
            try:
                with open(persona_file, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                chunks = chunk_text(raw_text)
                if chunks:
                    col = client.create_collection(name=persona_name, embedding_function=embed_fn)
                    ids = [f"{persona_name}_{i}" for i in range(len(chunks))]
                    col.add(documents=chunks, ids=ids)
                    print(f"Auto-indexed knowledge base for '{persona_name}' ({len(chunks)} chunks).")
                    return col
            except Exception as e:
                print(f"Failed to auto-index {persona_name}: {e}")
        return None



def retrieve_context_with_chunks(collection, question: str, k: int = TOP_K):
    results = collection.query(query_texts=[question], n_results=k)
    docs = results.get("documents", [[]])[0]
    formatted_context = "\n\n---\n\n".join(docs) if docs else "(no relevant context found)"
    return formatted_context, docs


class ChatRequest(BaseModel):
    persona: str
    question: Optional[str] = None
    message: Optional[str] = None
    history: Optional[List] = None


class ChatResponse(BaseModel):
    persona: str
    question: str
    answer: str
    response: Optional[str] = None
    context_chunks: List[str]
    chunks: Optional[List[str]] = None


class VerifyPinRequest(BaseModel):
    pin: str


@app.get("/api/health")
def health_check():
    collections = []
    if CHROMA_AVAILABLE:
        try:
            client = get_chroma_client()
            if client:
                collections = [c.name for c in client.list_collections()]
        except Exception:
            pass
    if not collections:
        collections = list(PERSONA_METADATA.keys())
    return {
        "status": "healthy",
        "collections": collections,
        "chroma_available": CHROMA_AVAILABLE,
        "api_key_set": bool(os.environ.get("GEMINI_API_KEY"))
    }


@app.post("/api/verify-pin")
def verify_pin(req: VerifyPinRequest):
    if req.pin.strip() == MASTER_PIN:
        return {"success": True, "token": "master_access_granted"}
    return {"success": False, "detail": "Incorrect Passcode. Try '1879'."}


@app.get("/api/personas")
def list_personas():
    existing_cols = set()
    if CHROMA_AVAILABLE:
        try:
            client = get_chroma_client()
            if client:
                existing_cols = set(c.name for c in client.list_collections())
        except Exception:
            pass
    personas = []
    for pid, meta in PERSONA_METADATA.items():
        data_path = os.path.join(DATA_DIR, f"{pid}.txt")
        file_exists = os.path.exists(data_path)
        word_count = 0
        if file_exists:
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    word_count = len(f.read().split())
            except Exception:
                pass
        
        personas.append({
            **meta,
            "indexed": (pid in existing_cols) if CHROMA_AVAILABLE else file_exists,
            "wordCount": word_count
        })
    return personas


@app.get("/api/network-info")
def get_network_info(request: Request):
    local_ip = get_local_ip()
    tunnel_url = get_tunnel_url()
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme or "http"

    # Cloud / Vercel deployment detection
    if host and "localhost" not in host and "127.0.0.1" not in host and not host.startswith("192.168."):
        cloud_url = f"{scheme}://{host}"
        return {
            "local_ip": local_ip,
            "local_url": cloud_url,
            "tunnel_url": cloud_url,
            "recommended": cloud_url
        }

    return {
        "local_ip": local_ip,
        "local_url": f"http://{local_ip}:8000",
        "tunnel_url": tunnel_url,
        "recommended": tunnel_url if tunnel_url else f"http://{local_ip}:8000"
    }


@app.get("/api/qr/{persona_id}")
def generate_persona_qr(
    persona_id: str, 
    request: Request, 
    target_url: Optional[str] = None,
    base_url: Optional[str] = None,
    network_mode: Optional[str] = None
):
    pid = persona_id.lower().strip()
    if pid not in PERSONA_METADATA:
        raise HTTPException(status_code=404, detail="Persona not found")

    # If no target_url explicitly supplied, construct locked kiosk link
    if not target_url:
        if base_url:
            target_url = f"{base_url.rstrip('/')}/?persona={pid}&kiosk=true"
        elif network_mode == "lan":
            local_ip = get_local_ip()
            target_url = f"http://{local_ip}:8000/?persona={pid}&kiosk=true"
        elif network_mode == "public":
            tunnel = get_tunnel_url()
            if tunnel:
                target_url = f"{tunnel}/?persona={pid}&kiosk=true"
            else:
                local_ip = get_local_ip()
                target_url = f"http://{local_ip}:8000/?persona={pid}&kiosk=true"
        else:
            host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
            scheme = request.headers.get("x-forwarded-proto") or request.url.scheme

            # NEVER put localhost or 127.0.0.1 in a QR code intended to be scanned by a phone!
            if "localhost" in host or "127.0.0.1" in host or not host:
                tunnel = get_tunnel_url()
                if tunnel:
                    target_url = f"{tunnel}/?persona={pid}&kiosk=true"
                else:
                    local_ip = get_local_ip()
                    target_url = f"http://{local_ip}:8000/?persona={pid}&kiosk=true"
            else:
                target_url = f"{scheme}://{host}/?persona={pid}&kiosk=true"

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0a0f1d", back_color="#ffffff").convert("RGBA")

    # Overlay circular avatar in center
    avatar_path = os.path.join(IMAGES_DIR, f"{pid}_avatar.jpg")
    if os.path.exists(avatar_path):
        avatar = Image.open(avatar_path).convert("RGBA")
        logo_size = int(qr_img.size[0] * 0.26)
        avatar = ImageOps.fit(avatar, (logo_size, logo_size), Image.Resampling.LANCZOS)

        # Circular mask
        mask = Image.new("L", (logo_size, logo_size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, logo_size, logo_size), fill=255)

        # Badge border
        border_color = (0, 240, 255, 255) if pid == "einstein" else ((255, 183, 3, 255) if pid == "kalam" else (199, 125, 255, 255))
        badge = Image.new("RGBA", (logo_size + 10, logo_size + 10), (255, 255, 255, 255))
        draw_badge = ImageDraw.Draw(badge)
        draw_badge.ellipse((0, 0, logo_size + 9, logo_size + 9), fill=(255, 255, 255, 255), outline=border_color, width=4)
        badge.paste(avatar, (5, 5), mask)

        pos = ((qr_img.size[0] - badge.size[0]) // 2, (qr_img.size[1] - badge.size[1]) // 2)
        qr_img.paste(badge, pos, badge)

    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")


@app.post("/api/chat", response_model=ChatResponse)
def chat_with_persona(req: ChatRequest):
    persona_id = req.persona.lower().strip()
    if persona_id not in PERSONA_METADATA:
        raise HTTPException(status_code=400, detail=f"Unknown persona '{persona_id}'")
    
    question = (req.question or req.message or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    meta = PERSONA_METADATA[persona_id]
    # Direct high-precision text retrieval ensures 100% identical context on Localhost and Vercel
    formatted_context, chunks = retrieve_fallback_context(persona_id, question, k=TOP_K)
    
    system_prompt = PERSONA_SYSTEM_TEMPLATE.format(
        name=meta["name"],
        era=meta["era"],
        voice_guidance=meta.get("voiceGuidance", ""),
        context=formatted_context
    )

    answer = None
    last_error = None
    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-3.1-flash-lite-preview",
        "gemini-3.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-3.8-flash",
    ]

    for model_name in models_to_try:
        for attempt in range(1, 3):
            try:
                gemini = get_gemini_client()
                response = gemini.models.generate_content(
                    model=model_name,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        max_output_tokens=220,
                        temperature=0.6,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                    contents=question,
                )
                if response and response.text:
                    answer = response.text
                    break
            except Exception as e:
                last_error = e
                err_str = str(e)
                if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str or "RESOURCE_EXHAUSTED" in err_str):
                    break
                break
        if answer:
            break

    if answer is None:
        if last_error and ("503" in str(last_error) or "UNAVAILABLE" in str(last_error) or "429" in str(last_error)):
            raise HTTPException(status_code=503, detail="Gemini model is temporarily busy. Please try asking again in a moment.")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(last_error)}")

    return ChatResponse(
        persona=persona_id,
        question=question,
        answer=answer,
        response=answer,
        context_chunks=chunks,
        chunks=chunks
    )


# Serve Static Frontend Files
static_dir = os.path.join(BASE_DIR, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)


@app.on_event("startup")
def startup_event():
    """Ensure all persona knowledge bases are auto-indexed in ChromaDB on startup."""
    if not CHROMA_AVAILABLE:
        print("[Startup] Running in serverless mode (ChromaDB disabled, using direct knowledge retrieval).")
        return
    try:
        if os.path.isdir(DATA_DIR):
            for filename in os.listdir(DATA_DIR):
                if filename.endswith(".txt"):
                    name = os.path.splitext(filename)[0]
                    try:
                        get_collection(name)
                    except Exception:
                        pass
    except Exception as e:
        print(f"Startup indexing check: {e}")


app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"Starting server on http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=False)

