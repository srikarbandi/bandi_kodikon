# backend/emotion_voice.py
"""
Transcribe audio bytes -> transcript using OpenAI Whisper (local).
Also provides analyze_audio_bytes() which calls your text emotion analyzer.
"""

import os
import tempfile
from typing import Optional, Tuple, Dict, Any

from pydub import AudioSegment

# Try import of whisper
try:
    import whisper
except Exception as e:
    whisper = None
    print("Warning: whisper not available. Install openai-whisper. Error:", e)

# Import your text-emotion analyzer. Make sure backend/emotion_text.py
# defines `analyze_emotion(text: str) -> dict`.
try:
    from backend.emotion_text import analyze_emotion
except Exception:
    # Fallback stub if teammate hasn't implemented it yet.
    def analyze_emotion(text: str) -> dict:
        # simple placeholder until real analyser is present
        label = "unknown"
        if text:
            label = "neutral"
        return {"label": label, "confidence": 0.0}

# -------------------------
# Model caching
# -------------------------
_MODEL_NAME = os.environ.get("WHISPER_MODEL", "tiny")
_MODEL = None
if whisper is not None:
    try:
        _MODEL = whisper.load_model(_MODEL_NAME)
    except Exception as e:
        print("Warning: failed to load whisper model at import:", e)
        _MODEL = None

# -------------------------
# Helpers
# -------------------------
def _save_bytes_to_wav(audio_bytes: bytes, sr: int = 16000) -> str:
    """
    Save raw audio bytes (mp3/wav/m4a/webm etc) to a normalized 16k mono WAV file.
    Returns path to saved wav.
    """
    # write temp input file
    tmp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
    tmp_in.write(audio_bytes)
    tmp_in.flush()
    tmp_in.close()
    # convert using pydub
    audio = AudioSegment.from_file(tmp_in.name)
    audio = audio.set_frame_rate(sr).set_channels(1).set_sample_width(2)
    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.export(tmp_out.name, format="wav")
    return tmp_out.name

# -------------------------
# Public API
# -------------------------
def transcribe_audio_bytes(audio_bytes: bytes, model_name: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Transcribe audio bytes into text using Whisper.
    Returns (transcript, meta).
    """
    global _MODEL, _MODEL_NAME
    if whisper is None:
        raise RuntimeError("Whisper package not installed. Run `pip install openai-whisper`.")

    use_model = model_name or _MODEL_NAME
    # load model if not loaded or model_name changed
    if _MODEL is None or _MODEL_NAME != use_model:
        _MODEL = whisper.load_model(use_model)
        _MODEL_NAME = use_model

    wav_path = _save_bytes_to_wav(audio_bytes)
    result = _MODEL.transcribe(wav_path, language=None)  # auto-detect language
    transcript = (result.get("text") or "").strip()
    meta = {"language": result.get("language"), "segments": result.get("segments")}
    return transcript, meta

def analyze_audio_bytes(audio_bytes: bytes, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Transcribe audio bytes and run text-based emotion analysis.
    Returns: {"transcript": str, "meta": {...}, "emotion": {...}}
    """
    try:
        transcript, meta = transcribe_audio_bytes(audio_bytes, model_name=model_name)
    except Exception as e:
        # bubble up minimal info for UI
        return {"transcript": "", "meta": {}, "emotion": {"error": str(e)}}

    # call text emotion analyzer (teammate's module)
    try:
        emotion_result = analyze_emotion(transcript)
    except Exception as e:
        emotion_result = {"error": f"emotion analyzer error: {e}"}

    return {"transcript": transcript, "meta": meta, "emotion": emotion_result}
