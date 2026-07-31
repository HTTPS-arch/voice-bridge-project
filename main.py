from speech_to_text import speech_to_text
from translator import translate_text

def main():

    print("=" * 60)
    print("VOICEBRIDGE PROJECT")
    print("=" * 60)

    # Step 1: Speech to Text
    recognized_text, speech_accuracy = speech_to_text()

    # Step 2: Translate
    translated_text, translation_accuracy = translate_text(recognized_text)

    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)

    print(f"\nRecognized Text : {recognized_text}")
    print(f"Translated Text : {translated_text}")

    # Real Accuracy (calculated from model confidence scores)
    speech_val = float(speech_accuracy.strip('%'))
    translation_val = float(translation_accuracy.strip('%'))
    overall_accuracy = (speech_val + translation_val) / 2

    print(f"\nSpeech Recognition Accuracy (Real)  : {speech_accuracy}")
    print(f"Translation Accuracy (Real)         : {translation_accuracy}")
    print(f"Overall System Accuracy (Real)      : {overall_accuracy:.1f}%")

if __name__ == "__main__":
    main()