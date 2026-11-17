
import time
import wave
import io
import os

from piper import PiperVoice

# ----------------------------
# Piper voice model setup
# ----------------------------

MODEL_DIR = "piper_voices"

VOICE_MODELS = {
    "de": {
        "name": "German",
        "model": "de_DE-thorsten-medium",
        "warmup": "Hallo",
    },
    "en": {
        "name": "English",
        "model": "en_US-lessac-medium",
        "warmup": "Hello",
    },
}

# Store loaded models so they are loaded only once.
_loaded_voices = {}


def _load_voice(language):
    """
    Load the Piper voice for the requested language.
    Reuse the model if it has already been loaded.
    """

    language = language.lower().split("-")[0]

    if language not in VOICE_MODELS:
        raise ValueError(
            f"Unsupported target language: {language}. Use 'en' or 'de'."
        )

    if language not in _loaded_voices:
        model_name = VOICE_MODELS[language]["model"]
        model_path = os.path.join(MODEL_DIR, f"{model_name}.onnx")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Piper model not found: {model_path}"
            )

        print(f"Loading Piper {VOICE_MODELS[language]['name']} voice...")

        voice = PiperVoice.load(model_path)

        # Warm-up synthesis
        dummy_buffer = io.BytesIO()

        with wave.open(dummy_buffer, "wb") as dummy_wav:
            voice.synthesize_wav(
                VOICE_MODELS[language]["warmup"],
                dummy_wav
            )

        _loaded_voices[language] = voice

        print(
            f"Piper {VOICE_MODELS[language]['name']} voice ready."
        )

    return _loaded_voices[language]


def synthesize_to_wav(text, target_language="de"):
    """
    Convert translated text into WAV audio using Piper.

    Args:
        text: Text to synthesize.
        target_language: 'en' or 'de'.

    Returns:
        tuple:
            wav_bytes: Generated WAV audio as bytes.
            generation_time: Synthesis time in seconds.
    """

    if not text or not text.strip():
        raise ValueError("Cannot synthesize empty text.")

    language = target_language.lower().split("-")[0]

    voice = _load_voice(language)

    print(
        f"Generating speech using Piper "
        f"({VOICE_MODELS[language]['name']})..."
    )

    start_time = time.time()

    audio_buffer = io.BytesIO()

    with wave.open(audio_buffer, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    generation_time = time.time() - start_time

    wav_bytes = audio_buffer.getvalue()

    return wav_bytes, generation_time
