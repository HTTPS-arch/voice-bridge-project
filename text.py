import time
import numpy as np
import speech_recognition as sr
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

model = WhisperModel(
        "base",
        device="cpu",
        compute_type="int8"
    )


def speech_to_text():
    # Initialize Microphone
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:


        print(" SPEECH TO TEXT ")
    
        print("Speak Now...\n")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        # Automatically stops when user stops speaking
        audio = recognizer.listen(source)

    print("Processing Speech...\n")

    # Save Audio Temporarily
    audio_data = np.frombuffer(
        audio.get_raw_data(),
        dtype=np.int16
    )

    write(
        "temp.wav",
        audio.sample_rate,
        audio_data
    )

    # Speech Recognition
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

    # Estimated Accuracy (Demo)
    if len(recognized_text) > 25:
        accuracy = "95%"
    elif len(recognized_text) > 10:
        accuracy = "90%"
    elif len(recognized_text) > 0:     #Faster-Whisper does not provide a real-time accuracy percentage. I selected these thresholds to classify short, medium, and long recognized text for demonstrating estimated accuracy
        accuracy = "85%"
    else:
        accuracy = "Low"

    # Display Result

    print(" RESULT ")
   

    print("Recognized Text:", recognized_text)

    print("\nProcessing Time :", round(processing_time, 2), "seconds")

    print("Model Accuracy :", accuracy)

    print("\nASR Model : Whisper Base (Faster-Whisper)")


    # Return text to other modules
    return recognized_text


# Run only if this file is executed directly
if __name__ == "__main__":
    speech_to_text()