import time
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from translator import translate_text

# Load once at module level
model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def english_audio_to_german_text():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(" ENGLISH SPEECH -> GERMAN TEXT ")
        print("Speak in English now...\n")

        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    print("Processing Speech...\n")

    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    write("temp_en.wav", audio.sample_rate, audio_data)

    # --- Step 1: Speech to Text (English) ---
    start_stt = time.time()

    segments, info = model.transcribe(
        "temp_en.wav",
        language="en",
        beam_size=5
    )

    english_text = ""
    for segment in segments:
        english_text += segment.text + " "
    english_text = english_text.strip()

    stt_time = time.time() - start_stt

    # --- Step 2: Translate English -> German ---
    start_translate = time.time()
    german_text = translate_text(english_text)
    translate_time = time.time() - start_translate

    # --- Results ---
    print(" RESULT ")
    print("English Text :", english_text)
    print("German Text  :", german_text)
    print(f"\nSTT Time         : {stt_time:.2f} seconds")
    print(f"Translation Time  : {translate_time:.2f} seconds")
    print(f"Detected Language : {info.language} (confidence: {info.language_probability:.2%})")
    print("\nASR Model         : Whisper Base (Faster-Whisper)")
    print("Translation Model : NLLB-200 (facebook/nllb-200-distilled-600M)")

    return english_text, german_text


if __name__ == "__main__":
    english_audio_to_german_text()