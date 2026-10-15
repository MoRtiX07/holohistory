# 🌌 Hologram Persona Chatbot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-orange.svg)](https://www.trychroma.com/)
[![Gemini](https://img.shields.io/badge/AI-Google_Gemini-4285F4.svg)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive, AI-powered holographic exhibition system that lets you converse directly with historical giants—grounded strictly in their real historical writings, documented speeches, and scientific publications using a **RAG (Retrieval-Augmented Generation)** architecture.

---

## ✨ Key Features

- 🏛️ **Historical Personas**:
  - **Albert Einstein** (Theoretical Physicist, 1879–1955)
  - **Dr. A. P. J. Abdul Kalam** (Aerospace Scientist & President of India, 1931–2015)
  - **Nikola Tesla** (Electrical Inventor & Visionary, 1856–1943)
- 🔮 **Sci-Fi Hologram Interface**:
  - Cyberpunk/futuristic glassmorphism UI with neon accents.
  - Speech synthesis (AI answers read aloud in distinct persona voices).
  - Telemetry HUD with real-time token tracking, response latency, and chunk grounding.
  - Museum Artifact Gallery & Persona Surprise Inquiries.
- 🧠 **Zero-Hallucination RAG Architecture**:
  - Persona source texts are chunked and vectorized using `sentence-transformers/all-MiniLM-L6-v2`.
  - ChromaDB retrieves the top most relevant primary-source excerpts.
  - Google Gemini generates conversational first-person responses constrained strictly by retrieved facts.
- 📱 **Mobile & Global Sharing Ready**:
  - Dynamic QR code generation for instant mobile phone connectivity on the same Wi-Fi.
  - Integrated Cloudflare tunnel launcher to share the live hologram instantly with anyone worldwide over public HTTPS.
- 🎙️ **Multi-Modal Interfaces**:
  - **Web Application**: Full-featured holographic web experience.
  - **Terminal CLI**: Lightweight interactive terminal session (`chatbot.py`).
  - **Voice Mode**: Real-time microphone listening + local speech-to-text via OpenAI Whisper (`voice_chatbot.py`).

---

## 🏗️ Technical Architecture

```
User Query (Text / Speech)
          │
          ▼
Embedding Model (all-MiniLM-L6-v2) ──► Query Vector
                                           │
                                           ▼
                                 Chroma Vector Database
                                 (Indexes data/*.txt)
                                           │
                                           ▼
System Prompt + Retrieved Excerpts ◄───────┘
          │
          ▼
Google Gemini API (gemini-flash-latest)
          │
          ▼
Authentic In-Character First-Person Response
(Web UI / Text-to-Speech / Terminal)
```

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.10 or higher**
- A free **Google Gemini API Key** ([Get one here at Google AI Studio](https://aistudio.google.com/apikey))

---

### Method A: One-Click Launcher (Recommended)

#### On Windows:
Double-click `run_project.bat` or run in terminal:
```cmd
run_project.bat
```
*This automatically sets up the virtual environment, installs dependencies, loads configuration, starts the web server on `http://localhost:8000`, and offers to launch a public sharing tunnel.*

#### On macOS / Linux:
```bash
chmod +x run_project.sh
./run_project.sh
```

---

### Method B: Manual Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hologram-persona-chatbot.git
   cd hologram-persona-chatbot
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Gemini API Key**:
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
   *(Or set it as an environment variable: `export GEMINI_API_KEY=your_key`)*

5. **Start the Web Application**:
   ```bash
   python app.py
   ```
   Open your browser to: **[http://localhost:8000](http://localhost:8000)**

---

## 🌐 Sharing Publicly with Anyone

Want friends, teachers, or colleagues to test your chatbot on their phones from anywhere?

### Option 1: Mobile on Local Wi-Fi
1. Start the server (`python app.py`).
2. Open the **Admin / Mobile** panel inside the web app.
3. Scan the generated QR code with any phone connected to the same Wi-Fi.

### Option 2: Worldwide Instant Public Link
Run Cloudflare tunnel (no router configuration or port forwarding needed):
```bash
npx -y cloudflared tunnel --url http://127.0.0.1:8000
```
This generates a temporary secure public URL (e.g., `https://random-subdomain.trycloudflare.com`) that anyone in the world can open on their mobile browser!

---

## 💬 Command-Line & Voice Modes

### Interactive CLI Chatbot:
```bash
python chatbot.py einstein
# Or:
python chatbot.py kalam
python chatbot.py tesla
```

### Voice Chatbot (Requires Microphone & FFmpeg):
```bash
python voice_chatbot.py einstein
```
*Press Enter, speak your question, and listen to the voice reply through your speakers.*

---

## ➕ Adding New Historical Personas

Adding a new persona is effortless:

1. Create a new text file under `data/`, e.g., `data/curie.txt`.
2. Populate it with speeches, letters, biographical writings, and quotes.
3. Run the indexing script (or just start `app.py`, which auto-indexes any new `.txt` files):
   ```bash
   python build_knowledge_base.py
   ```
4. Chat with your new persona:
   ```bash
   python chatbot.py curie
   ```

---

## 🧪 Verification & Automated Tests

Run the test suite to verify endpoints, vector chunk grounding, latency, and artifact queries:
```bash
python verify_features.py
```

---

## 📁 Repository Structure

```
.
├── app.py                      # FastAPI web server, API routes, auto-indexer
├── build_knowledge_base.py     # RAG chunking & ChromaDB vector database builder
├── chatbot.py                  # Standalone CLI chatbot
├── voice_chatbot.py            # Speech-to-speech chatbot (Whisper + pyttsx3)
├── verify_features.py          # Automated verification test script
├── download_portraits.py       # Downloads historical portraits
├── run_project.bat             # Windows one-click launcher
├── run_project.sh              # Unix/macOS one-click launcher
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variable template
├── .gitignore                  # Git ignore rules (protects keys & venv)
├── data/                       # Primary historical source texts
│   ├── einstein.txt
│   ├── kalam.txt
│   └── tesla.txt
└── static/                     # Web application frontend
    ├── index.html              # Holographic UI markup
    ├── styles.css              # Futuristic glassmorphism styles & animations
    ├── app.js                  # Frontend controller & audio engine
    └── images/                 # Persona portraits, artifacts & QR codes
```

---

## 📜 License

This project is licensed under the MIT License - feel free to use and modify for educational, academic, and research projects.
