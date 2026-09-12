from __future__ import annotations

import hashlib
import os
import urllib.request
from pathlib import Path
from threading import Lock

import torch
import whisper

MODEL_NAME = "turbo"
DEFAULT_LANGUAGE = "ru"

_model = None
_model_lock = Lock()


def _whisper_cache_dir() -> Path:
    """Return the same cache directory used by OpenAI Whisper."""
    default = Path.home() / ".cache"
    cache_root = Path(os.getenv("XDG_CACHE_HOME", default))
    return cache_root / "whisper"


def _download_model_with_progress() -> Path:
    """Download the official Whisper model while showing percentage progress."""
    url = whisper._MODELS[MODEL_NAME]
    expected_sha256 = url.split("/")[-2]
    target_dir = _whisper_cache_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / Path(url).name

    if target.is_file():
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest == expected_sha256:
            print("[WHISPER] Model already downloaded (100%)", flush=True)
            return target
        print("[WHISPER] Existing model checksum is invalid; downloading again...", flush=True)

    partial = target.with_suffix(target.suffix + ".part")
    print("[WHISPER] Downloading model...", flush=True)

    with urllib.request.urlopen(url) as source, partial.open("wb") as output:
        total = int(source.info().get("Content-Length") or 0)
        downloaded = 0
        last_percent = -1

        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
            downloaded += len(chunk)

            if total:
                percent = min(100, downloaded * 100 // total)
                if percent != last_percent:
                    print(f"[WHISPER] Downloading model: {percent}%", flush=True)
                    last_percent = percent

    digest = hashlib.sha256(partial.read_bytes()).hexdigest()
    if digest != expected_sha256:
        partial.unlink(missing_ok=True)
        raise RuntimeError(
            "Whisper model was downloaded, but its SHA256 checksum does not match."
        )

    partial.replace(target)
    print("[WHISPER] Model downloaded (100%)", flush=True)
    return target


def load_model():
    """Load the Whisper model once and reuse it for all voice messages."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                model_path = _download_model_with_progress()
                print("[WHISPER] Loading model into memory...", flush=True)
                _model = whisper.load_model(str(model_path))
                print("[WHISPER] Model loaded", flush=True)
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
