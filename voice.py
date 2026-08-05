from gtts import gTTS
from playsound import playsound
import os


def speak_text(text):

    print("\nGenerating Speech...")

    tts = gTTS(
        text=text,
        lang="te",
        slow=False
    )

    filename = "translated_voice.mp3"

    tts.save(filename)

    playsound(filename)

    os.remove(filename)

    print("Speech Completed.")
