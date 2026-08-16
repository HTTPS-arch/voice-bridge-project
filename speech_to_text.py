import os
import time
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
from whisper_model import model


def speech_to_text():
    """
    Captures microphone audio and transcribes it using Faster-Whisper.

    Returns:
        tuple: (recognized_text, speech_confidence, capture_time, transcription_time)

    capture_time  = how long the microphone spent listening (depends on
                    how long the speaker talks, not a performance metric)
    transcription_time = actual Whisper processing time (the real
                          performance metric for STT speed)
    """

    # Initialize Microphone
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("SPEECH TO TEXT")
        print("Speak Now...\n")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        capture_start = time.time()

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=15
            )
        except sr.WaitTimeoutError:
            print("No speech detected. Please try again.")
            return "", "0%", 0.0, 0.0

    capture_time = time.time() - capture_start

    print("Processing Speech...\n")

    audio_data = np.frombuffer(
        audio.get_raw_data(),
        dtype=np.int16
    )

    write(
        "temp.wav",
        audio.sample_rate,
        audio_data
    )

    transcription_start = time.time()

    segments, info = model.transcribe(
        "temp.wav",
        language="en",
        beam_size=5
    )

    # -----------------------------
    # Collect recognized text
    # and confidence information
    # -----------------------------
    recognized_text = ""
    logprobs = []

    for segment in segments:
        recognized_text += segment.text + " "
        logprobs.append(segment.avg_logprob)

    transcription_time = time.time() - transcription_start

    recognized_text = recognized_text.strip()

    # Safe to delete the temporary file after
    # the segments generator has been fully consumed.
    os.remove("temp.wav")

    # -----------------------------
    # Calculate speech confidence
    # -----------------------------
    if logprobs:
        avg_logprob = sum(logprobs) / len(logprobs)
        confidence = np.exp(avg_logprob) * 100
        speech_confidence = f"{confidence:.1f}%"
    else:
        speech_confidence = "0%"

    print("RESULT")
    print("Recognized Text:", recognized_text)
    print("\nAudio Capture Duration:", round(capture_time, 2), "seconds")
    print("Transcription Processing Time:", round(transcription_time, 2), "seconds")
    print("Speech Confidence:", speech_confidence)
    print("\nASR Model: Whisper Base (Faster-Whisper)")

    return recognized_text, speech_confidence, capture_time, transcription_time


if __name__ == "__main__":
    speech_to_text()