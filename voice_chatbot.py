"""
Step 5: voice version of the persona chatbot.

Run it with:
    python voice_chatbot.py einstein

Flow each turn:
    1. Press Enter, then speak your question (records for RECORD_SECONDS)
    2. Whisper transcribes it locally (no API needed for this part)
    3. Your existing RAG + Claude pipeline answers in character
    4. The answer is spoken aloud through your speakers

Type 'q' instead of pressing Enter (blank) to quit.

Requires everything chatbot.py needs (GEMINI_API_KEY set), plus:
    pip install -r requirements.txt     (now includes whisper, sounddevice, pyttsx3)
    ffmpeg installed and on PATH (Whisper needs this to process audio)
      - Windows: download from https://www.gyan.dev/ffmpeg/builds/, add the
        bin folder to your PATH, then open a NEW terminal
      - Mac: brew install ffmpeg
      - Linux: sudo apt install ffmpeg
"""

import os
import sys
import queue
import tempfile

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write as write_wav
import whisper
import pyttsx3
from google import genai

# reuse everything already built in chatbot.py
from chatbot import get_collection, retrieve_context, ask_llm

SAMPLE_RATE = 16000
RECORD_SECONDS = 6  # how long we listen after you press Enter


def record_audio(duration=RECORD_SECONDS, fs=SAMPLE_RATE):
    print(f"Listening... (speak now, {duration}s)")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    print("Done listening.")
    tmp_path = os.path.join(tempfile.gettempdir(), "persona_question.wav")
    write_wav(tmp_path, fs, audio)
    return tmp_path


def transcribe(whisper_model, audio_path):
    # force English so Whisper doesn't try to guess the language on short clips
    # (that guessing is what was causing the garbled/foreign-looking transcripts)
    result = whisper_model.transcribe(audio_path, fp16=False, language="en")
    return result["text"].strip()


def speak(text):
    # pyttsx3 on Windows has a known issue where reusing one engine instance
    # across multiple say()/runAndWait() calls stops working after the first
    # time. Creating a fresh engine per call avoids that.
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", 165)
    tts_engine.say(text)
    tts_engine.runAndWait()
    tts_engine.stop()


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python voice_chatbot.py <persona_name>\nExample: python voice_chatbot.py einstein")

    persona_name = sys.argv[1].lower()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY environment variable not set. Set it the same way as before.")

    collection = get_collection(persona_name)
    client = genai.Client(api_key=api_key)

    print("Loading Whisper speech-to-text model (first run downloads it)...")
    whisper_model = whisper.load_model("base")  # good balance of speed/accuracy for a demo

    print(f"\nVoice chat with {persona_name.title()} is ready.")
    print("Press Enter then speak your question. Type 'q' + Enter to quit.\n")

    while True:
        cmd = input("[Enter to ask, q to quit]: ").strip().lower()
        if cmd == "q":
            break

        audio_path = record_audio()
        question = transcribe(whisper_model, audio_path)
        print(f"You said: {question}")

        if not question:
            print("Didn't catch that, try again.\n")
            continue

        context = retrieve_context(collection, question)
        answer = ask_llm(client, persona_name, question, context)
        print(f"\n{persona_name.title()}: {answer}\n")

        speak(answer)


if __name__ == "__main__":
    main()
