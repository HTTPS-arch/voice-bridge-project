# NLLB-200 Model Configuration

MODEL_NAME = "facebook/nllb-200-distilled-600M"

SOURCE_LANGUAGE = "eng_Latn"

# Default target language (used only for model warm-up)
TARGET_LANGUAGE = "fra_Latn"

# Supported target languages for user selection
LANGUAGES = {
    "1": {"name": "French", "code": "fra_Latn"},
    "2": {"name": "German", "code": "deu_Latn"},
}