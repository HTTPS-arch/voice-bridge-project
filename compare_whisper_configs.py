import time
from faster_whisper import WhisperModel
from generate_test_audio import GROUND_TRUTH_TEXT, OUTPUT_FILE

# ----------------------------
# Configurations to compare
# Each entry: (model_size, beam_size, label)
# ----------------------------
CONFIGS = [
    ("base", 5, "Current setup (base, beam=5)"),
    ("small", 3, "small, beam=3"),
    ("base", 2, "base, beam=2"),
    ("tiny", 5, "tiny, beam=5"),
]


def word_accuracy(reference, hypothesis):
    """
    Simple word-level accuracy: what percentage of words in the
    reference text also appear (in order-independent fashion) in
    the transcribed text. Not a full WER calculation, but a fast,
    honest approximation for comparing configs side by side.
    """
    ref_words = reference.lower().replace(".", "").split()
    hyp_words = hypothesis.lower().replace(".", "").split()

    matches = sum(1 for w in ref_words if w in hyp_words)
    return (matches / len(ref_words)) * 100 if ref_words else 0.0


def run_config(model_size, beam_size):
    print(f"\nLoading model: {model_size}...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    start = time.time()
    segments, info = model.transcribe(
        OUTPUT_FILE,
        language="en",
        beam_size=beam_size
    )

    text = ""
    logprobs = []
    for segment in segments:
        text += segment.text + " "
        logprobs.append(segment.avg_logprob)

    elapsed = time.time() - start
    text = text.strip()

    if logprobs:
        import numpy as np
        avg_logprob = sum(logprobs) / len(logprobs)
        confidence = np.exp(avg_logprob) * 100
    else:
        confidence = 0.0

    accuracy = word_accuracy(GROUND_TRUTH_TEXT, text)

    return {
        "text": text,
        "time": elapsed,
        "confidence": confidence,
        "word_accuracy": accuracy,
    }


def main():
    print("=" * 70)
    print("WHISPER CONFIG COMPARISON")
    print("=" * 70)
    print(f"\nGround truth text:\n  {GROUND_TRUTH_TEXT}")
    print(f"\nTest audio file: {OUTPUT_FILE}")
    print("(Run generate_test_audio.py first if this file doesn't exist yet)")

    results = []

    for model_size, beam_size, label in CONFIGS:
        result = run_config(model_size, beam_size)
        result["label"] = label
        results.append(result)

        print(f"\n--- {label} ---")
        print(f"Transcribed : {result['text']}")
        print(f"Time        : {result['time']:.3f}s")
        print(f"Confidence  : {result['confidence']:.1f}%")
        print(f"Word Accuracy vs ground truth: {result['word_accuracy']:.1f}%")

    print("\n" + "=" * 70)
    print("SUMMARY (sorted by speed)")
    print("=" * 70)
    print(f"{'Config':<30}{'Time (s)':<12}{'Confidence':<14}{'Word Accuracy'}")
    for r in sorted(results, key=lambda x: x["time"]):
        print(f"{r['label']:<30}{r['time']:<12.3f}{r['confidence']:<14.1f}{r['word_accuracy']:.1f}%")


if __name__ == "__main__":
    main()