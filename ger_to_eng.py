<<<<<<< HEAD
import time
import numpy as np
import soundfile as sf
import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from kokoro import KPipeline

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# Load Kokoro pipeline once at module level (English)
kokoro_pipeline = KPipeline(lang_code="a")  # 'a' = American English


def english_text_to_audio(text, filename="translated_output_english.wav", voice="af_heart", play_audio=True):
    """
    Converts English text to speech using Kokoro (local neural TTS).
    """
    generator = kokoro_pipeline(text, voice=voice)

    # Kokoro yields (grapheme, phoneme, audio) chunks; concatenate for full text
    audio_chunks = [audio for _, _, audio in generator]
    full_audio = np.concatenate(audio_chunks)

    sf.write(filename, full_audio, 24000)

    if play_audio:
        print("Playing audio...\n")
        sd.play(full_audio, samplerate=24000)
        sd.wait()
        print("Playback finished.")

    return filename


def german_audio_to_english_text():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(" GERMAN SPEECH -> ENGLISH TEXT ")
        print("Speak in German now...\n")

        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    print("Processing Speech...\n")

    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    write("temp_de.wav", audio.sample_rate, audio_data)

    start = time.time()

    segments, info = model.transcribe(
        "temp_de.wav",
        language="de",
        task="translate",
        beam_size=5
    )

    english_text = ""
    for segment in segments:
        english_text += segment.text + " "
    english_text = english_text.strip()

    processing_time = time.time() - start

    print(" RESULT ")
    print("English Translation:", english_text)
    print("\nProcessing Time :", round(processing_time, 2), "seconds")
    print(f"Detected Language : {info.language} (confidence: {info.language_probability:.2%})")
    print("\nModel : Whisper Base (Faster-Whisper) — task=translate")

    # --- Generate English audio from the translated text (Kokoro) ---
    audio_filename = english_text_to_audio(
        english_text,
        filename="translated_output_english.wav",
        voice="af_heart",
        play_audio=True
    )

    return english_text, audio_filename


if __name__ == "__main__":
    text, audio_path = german_audio_to_english_text()
=======
import time
import numpy as np
import soundfile as sf
import sounddevice as sd
import speech_recognition as sr
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from kokoro import KPipeline

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

# Load Kokoro pipeline once at module level (English)
kokoro_pipeline = KPipeline(lang_code="a")  # 'a' = American English


def english_text_to_audio(text, filename="translated_output_english.wav", voice="af_heart", play_audio=True):
    """
    Converts English text to speech using Kokoro (local neural TTS).
    """
    generator = kokoro_pipeline(text, voice=voice)

    # Kokoro yields (grapheme, phoneme, audio) chunks; concatenate for full text
    audio_chunks = [audio for _, _, audio in generator]
    full_audio = np.concatenate(audio_chunks)

    sf.write(filename, full_audio, 24000)

    if play_audio:
        print("Playing audio...\n")
        sd.play(full_audio, samplerate=24000)
        sd.wait()
        print("Playback finished.")

    return filename


def german_audio_to_english_text():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print(" GERMAN SPEECH -> ENGLISH TEXT ")
        print("Speak in German now...\n")

        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    print("Processing Speech...\n")

    audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    write("temp_de.wav", audio.sample_rate, audio_data)

    start = time.time()

    segments, info = model.transcribe(
        "temp_de.wav",
        language="de",
        task="translate",
        beam_size=5
    )

    english_text = ""
    for segment in segments:
        english_text += segment.text + " "
    english_text = english_text.strip()

    processing_time = time.time() - start

    print(" RESULT ")
    print("English Translation:", english_text)
    print("\nProcessing Time :", round(processing_time, 2), "seconds")
    print(f"Detected Language : {info.language} (confidence: {info.language_probability:.2%})")
    print("\nModel : Whisper Base (Faster-Whisper) — task=translate")

    # --- Generate English audio from the translated text (Kokoro) ---
    audio_filename = english_text_to_audio(
        english_text,
        filename="translated_output_english.wav",
        voice="af_heart",
        play_audio=True
    )

    return english_text, audio_filename


if __name__ == "__main__":
    text, audio_path = german_audio_to_english_text()
>>>>>>> 24174a789e47fe9851ac9bf3e6ff5351c8ca5bbb
    print(f"\nAudio saved to: {audio_path}")