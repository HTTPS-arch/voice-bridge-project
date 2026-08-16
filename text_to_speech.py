import time
import wave
import os
import io
import pygame
from piper import PiperVoice
from huggingface_hub import hf_hub_download

# ----------------------------
# Piper voice model setup
# ----------------------------
# Model files will be auto-downloaded from Hugging Face if not found locally.
# They will be stored in the "piper_voices" folder in your project root.

MODEL_DIR = "piper_voices"
MODEL_BASE_NAME = "de_DE-thorsten-medium"
MODEL_ONNX = f"{MODEL_BASE_NAME}.onnx"
MODEL_JSON = f"{MODEL_BASE_NAME}.onnx.json"

# Full paths
MODEL_ONNX_PATH = os.path.join(MODEL_DIR, MODEL_ONNX)
MODEL_JSON_PATH = os.path.join(MODEL_DIR, MODEL_JSON)

# Hugging Face repo details
HF_REPO_ID = "rhasspy/piper-voices"
HF_SUBFOLDER = "de/de_DE/thorsten/medium"

_voice = None


def _ensure_model_downloaded():
    """
    Check if the Piper model files exist locally.
    If not, download them from Hugging Face Hub.
    """
    # Create the directory if it doesn't exist
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Check if both files exist
    if not (os.path.exists(MODEL_ONNX_PATH) and os.path.exists(MODEL_JSON_PATH)):
        print("Piper model files not found locally. Downloading from Hugging Face...")
        print("This may take a few minutes depending on your internet speed.")

        # Download the .onnx file
        hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=MODEL_ONNX,
            subfolder=HF_SUBFOLDER,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,
        )

        # Download the .onnx.json file
        hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=MODEL_JSON,
            subfolder=HF_SUBFOLDER,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,
        )

        print("Download complete! Model files are ready.")
    else:
        print("Piper model files found locally. Skipping download.")


def _load_voice():
    """
    Load the Piper voice model once and reuse it across calls, and run
    a warm-up synthesis so the first *real* call isn't penalized by
    ONNX runtime's one-time graph optimization / initialization cost.

    Without this warm-up, the first real synthesis call absorbs a large
    one-time setup cost that isn't representative of Piper's actual
    ongoing performance - the same reason the earlier local translation
    model had a warm-up step before real timing began.
    """
    global _voice
    if _voice is None:
        # Ensure the model is downloaded before loading
        _ensure_model_downloaded()

        print("Loading Piper voice model...")
        _voice = PiperVoice.load(MODEL_ONNX_PATH)

        print("Warming up Piper (first-call setup cost, not timed)...")
        dummy_buffer = io.BytesIO()
        with wave.open(dummy_buffer, "wb") as dummy_wav:
            _voice.synthesize_wav("Hallo", dummy_wav)

        print("Piper voice model ready.")
    return _voice


def speak_text(text, gender="female"):
    """
    Converts text to speech using Piper (local, offline) and plays it back.

    Note: gender parameter is kept for compatibility with the rest of
    the pipeline, but the current voice model (Thorsten) is male only.

    Returns:
        float: generation_time_seconds (pure synthesis time, after
        warm-up - excludes playback duration and one-time setup cost).
    """
    voice = _load_voice()
    output_file = "output_piper.wav"

    print("\n Speaking (Piper - German voice)...")

    start_time = time.time()

    with wave.open(output_file, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    generation_time = time.time() - start_time

    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    os.remove(output_file)

    return generation_time


if __name__ == "__main__":
    sample_text = "Ich bin Softwareentwickler, das spielt eine Rolle."
    gen_time = speak_text(sample_text)
    print(f"Piper TTS Generation Time: {gen_time:.3f} seconds")