import os
import time
from dotenv import load_dotenv
from google.cloud import translate_v3 as translate
from config import GOOGLE_PROJECT_ID, SOURCE_LANGUAGE, TARGET_LANGUAGE

# ----------------------------
# Load environment variables from .env file
# ----------------------------
# This automatically sets GOOGLE_APPLICATION_CREDENTIALS from the .env
# file in the project root, so you no longer need to run
# $env:GOOGLE_APPLICATION_CREDENTIALS=... manually every terminal session.
load_dotenv()

# ----------------------------
# Google Cloud Translation Client Setup
# ----------------------------
print("Initializing Google Cloud Translation client...")
client = translate.TranslationServiceClient()
parent = f"projects/{GOOGLE_PROJECT_ID}/locations/global"
print("Translation client ready.")


# ----------------------------
# Translation Function
# ----------------------------
def translate_text(text, target_language=TARGET_LANGUAGE):
    """
    Translates text using Google Cloud Translation API v3.

    Returns:
        tuple: (translated_text, execution_time_seconds)

    Note: Google Cloud Translation API v3 does not return a token-level
    confidence score the way the previous NLLB-200 local model did.
    We report execution time instead, as a meaningful, honest metric
    for API-based translation performance.
    """

    start_time = time.time()

    response = client.translate_text(
        parent=parent,
        contents=[text],
        source_language_code=SOURCE_LANGUAGE,
        target_language_code=target_language,
    )

    execution_time = time.time() - start_time

    translated_text = response.translations[0].translated_text

    return translated_text, execution_time


if __name__ == "__main__":
    sample = "Hello, how are you?"
    result, exec_time = translate_text(sample, "de")
    print("Original:", sample)
    print("Translated:", result)
    print(f"Execution Time: {exec_time:.3f} seconds")