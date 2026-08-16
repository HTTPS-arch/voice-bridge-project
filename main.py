import time
from speech_to_text import speech_to_text
from translator import translate_text
from text_to_speech import speak_text
from config import LANGUAGES, DEFAULT_TARGET_LANG_KEY, DEFAULT_VOICE_GENDER

def main():

    print("=" * 60)
    print("VOICEBRIDGE PROJECT")
    print("=" * 60)

    # ----------------------------
    # No manual prompts - using config defaults.
    # A live call pipeline won't have anyone typing menu choices,
    # so testing should reflect that from the start.
    # To change defaults, edit DEFAULT_TARGET_LANG_KEY and
    # DEFAULT_VOICE_GENDER in config.py.
    # ----------------------------
    target_lang = LANGUAGES[DEFAULT_TARGET_LANG_KEY]["code"]
    target_lang_name = LANGUAGES[DEFAULT_TARGET_LANG_KEY]["name"]
    gender = DEFAULT_VOICE_GENDER

    print(f"\nTarget language : {target_lang_name}")
    print(f"Voice           : {gender}")

    # ----------------------------
    # Start total pipeline timer
    # ----------------------------
    pipeline_start = time.time()

    # Step 1: Speech to Text
    recognized_text, speech_accuracy, capture_time, transcription_time = speech_to_text()

    # Step 2: Translate
    translated_text, translation_time = translate_text(recognized_text, target_lang)

    print("\n" + "=" * 60)
    print("FINAL OUTPUT")
    print("=" * 60)

    print(f"\nRecognized Text : {recognized_text}")
    print(f"Translated Text : {translated_text}")

    # Step 3: Text to Speech
    tts_time = speak_text(translated_text, gender=gender)

    # ----------------------------
    # Total pipeline time
    # ----------------------------
    # processing_only_time = pure computation time (STT transcription +
    # translation + TTS generation). This is the real performance metric.
    #
    # capture_time is reported separately since it reflects how long the
    # speaker talked, not system performance.
    #
    # total_pipeline_time is the full wall-clock time including audio
    # capture, useful for understanding real end-to-end latency in an
    # actual call scenario.
    total_pipeline_time = time.time() - pipeline_start
    processing_only_time = transcription_time + translation_time + tts_time

    print("\n" + "=" * 60)
    print("PERFORMANCE METRICS")
    print("=" * 60)
    print(f"\nSpeech Recognition Accuracy    : {speech_accuracy}")
    print(f"\nAudio Capture Duration         : {capture_time:.3f} seconds  (depends on speaker, not a performance metric)")
    print(f"Transcription Processing Time  : {transcription_time:.3f} seconds")
    print(f"Translation Time               : {translation_time:.3f} seconds")
    print(f"Text-to-Speech Generation Time : {tts_time:.3f} seconds")
    print(f"{'-' * 50}")
    print(f"Processing Time (Trans+TTS+STT proc) : {processing_only_time:.3f} seconds")
    print(f"Total Pipeline Time (incl. audio capture) : {total_pipeline_time:.3f} seconds")

if __name__ == "__main__":
    main()