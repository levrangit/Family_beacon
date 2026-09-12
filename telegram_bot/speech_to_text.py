from __future__ import annotations

from pathlib import Path
from threading import Lock

import torch
import whisper

MODEL_NAME = "turbo"
DEFAULT_LANGUAGE = "ru"

_model = None
_model_lock = Lock()


def load_model():
    """Load the Whisper model once and reuse it for all voice messages."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = whisper.load_model(MODEL_NAME)
    return _model


def transcribe_audio(audio_path: str | Path, language: str = DEFAULT_LANGUAGE) -> str:
    """Transcribe an audio file with the local Whisper turbo model."""
    model = load_model()
    result = model.transcribe(
        str(audio_path),
        language=language,
        fp16=torch.cuda.is_available(),
    )
    return str(result.get("text") or "").strip()
