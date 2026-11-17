import time
import numpy as np

from whisper_model import model


def speech_to_text(audio_data, sample_rate=16000):

    if audio_data is None or len(audio_data) == 0:
        return "", "", "0%", 0.0

    # Convert int16 PCM audio to normalized float32.
    audio_data = np.asarray(audio_data, dtype=np.float32)

    if audio_data.max() > 1.0 or audio_data.min() < -1.0:
        audio_data = audio_data / 32768.0

    transcription_start = time.time()

    segments, info = model.transcribe(
    audio_data,
    language=None,
    beam_size=5,
    vad_filter=False,
    condition_on_previous_text=False,
    no_speech_threshold=0.8
)

    recognized_text = ""
    logprobs = []

    for segment in segments:
        recognized_text += segment.text + " "
        logprobs.append(segment.avg_logprob)

    transcription_time = time.time() - transcription_start
    recognized_text = recognized_text.strip()
    detected_language = info.language

    if logprobs:
        avg_logprob = sum(logprobs) / len(logprobs)
        confidence = np.exp(avg_logprob) * 100
        speech_confidence = f"{confidence:.1f}%"
    else:
        speech_confidence = "0%"

    print("\n--- SPEECH TO TEXT RESULT ---")
    print("Recognized Text:", recognized_text)
    print("Detected Language:", detected_language)
    print("Transcription Time:", round(transcription_time, 2), "seconds")
    print("Speech Confidence:", speech_confidence)

    return (
        recognized_text,
        detected_language,
        speech_confidence,
        transcription_time,
    )