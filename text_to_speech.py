import pyttsx3

def speak_text(text, gender="female"):

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    selected_voice = None

    for voice in voices:
        name = voice.name.lower()
        if gender == "female" and ("female" in name or "zira" in name or "susan" in name):
            selected_voice = voice.id
            break
        elif gender == "male" and ("male" in name or "david" in name or "mark" in name):
            selected_voice = voice.id
            break

    # Fallback if name-matching fails (common on Windows: index 0 = male, index 1 = female)
    if not selected_voice:
        index = 1 if gender == "female" else 0
        if index < len(voices):
            selected_voice = voices[index].id

    if selected_voice:
        engine.setProperty('voice', selected_voice)

    engine.setProperty('rate', 160)

    print(f"\n Speaking ({gender} voice)...")
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    speak_text("Hello, this is a test.", gender="female")