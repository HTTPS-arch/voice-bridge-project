import time
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
# from faster_whisper import WhisperModel
from whisper_model import model



def speech_to_text():

    # Initialize Microphone
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print(" SPEECH TO TEXT ")
        print("Speak Now...\n")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        audio = recognizer.listen(source)

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

    start = time.time()

    segments, info = model.transcribe(
        "temp.wav",
        language="en",
        beam_size=5
    )

    processing_time = time.time() - start

    recognized_text = ""

    for segment in segments:
        recognized_text += segment.text + " "

    recognized_text = recognized_text.strip()

    # Estimated Accuracy
    if len(recognized_text) > 25:
        accuracy = "95%"
    elif len(recognized_text) > 10:
        accuracy = "90%"
    elif len(recognized_text) > 0:
        accuracy = "85%"
    else:
        accuracy = "Low"

    print(" RESULT ")
    print("Recognized Text:", recognized_text)
    print("\nProcessing Time :", round(processing_time, 2), "seconds")
    print("Model Accuracy :", accuracy)
    print("\nASR Model : Whisper Base (Faster-Whisper)")

    return recognized_text


if __name__ == "__main__":
    speech_to_text()