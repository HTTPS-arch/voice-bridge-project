import os
import time
import subprocess
import soundfile as sf
import sounddevice as sd

# ----------------------------
# Voice Model Config
# ----------------------------
# Update these paths to wherever you downloaded the .onnx voice models.
VOICE_MODELS = {
    "male": "voices/de_DE-thorsten-medium.onnx",
    "female": "voices/de_DE-eva_k-x_low.onnx",
}


def text_to_speech(text, voice="male", filename=None, play_audio=True):
    """
    Converts German text to speech using Piper (local neural TTS, VITS-based).
    voice: "male" or "female"
    """

    voice = voice.lower()

    if voice not in VOICE_MODELS:
        raise ValueError(f"Voice '{voice}' not supported. Choose 'male' or 'female'.")

    model_path = VOICE_MODELS[voice]

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Voice model not found at '{model_path}'.\n"
            f"Download the .onnx and .onnx.json files for this voice "
            f"and place them in the 'voices/' folder."
        )

    if filename is None:
        filename = f"translated_output_{voice}.wav"

    print("\n TEXT TO SPEECH (AI Model - Piper) ")
    print(f"Voice   : {voice}")
    print("Generating speech...\n")

    start = time.time()

    # Piper reads text from stdin and writes a WAV file
    subprocess.run(
        ["piper", "--model", model_path, "--output_file", filename],
        input=text.encode("utf-8"),
        check=True,
    )

    generation_time = time.time() - start

    print(f"Speech generated in {generation_time:.2f} seconds")
    print(f"Saved as         : {filename}\n")

    if play_audio:
        print("Playing audio...\n")
        data, sample_rate = sf.read(filename)
        sd.play(data, samplerate=sample_rate)
        sd.wait()
        print("Playback finished.")

    return filename


# Run only if this file is executed directly
# if __name__ == "__main__":
#     sample_text = "Hallo, wie geht es dir?"

#     text_to_speech(sample_text, voice="male")
#     text_to_speech(sample_text, voice="female")