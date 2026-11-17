
from faster_whisper import WhisperModel

print("Loading Whisper Small Model on CPU...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("Whisper CPU Model Ready!")
