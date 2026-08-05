from text import speech_to_text
from translator import translate_text
from voice import speak_text


def main():

    print("=" * 60)
    print("VOICEBRIDGE PROJECT")
    print("=" * 60)

    # Step 1: Speech to Text
    recognized_text = speech_to_text()

    if not recognized_text:
        print("\nNo speech detected.")
        return

    # Step 2: Translation
    translated_text = translate_text(recognized_text)

    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)

    print(f"\nRecognized Text : {recognized_text}")
    print(f"Translated Text : {translated_text}")

    print("\nGenerating Voice...")

    # Step 3: Text to Speech
    speak_text(translated_text)

    print("\nVoiceBridge Completed Successfully.")


if __name__ == "__main__":
    main()