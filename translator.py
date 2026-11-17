
import os
import time

from dotenv import load_dotenv
from google.cloud import translate_v3 as translate

from config import GOOGLE_PROJECT_ID, SUPPORTED_LANGUAGES

# Load Google Cloud credentials from .env
load_dotenv()

print("Initializing Google Cloud Translation client...")

client = translate.TranslationServiceClient()

parent = f"projects/{GOOGLE_PROJECT_ID}/locations/global"

print("Google Cloud Translation client ready.")


def get_target_language(source_language):
    """Choose the opposite language automatically."""

    language_pairs = {
        "en": "de",
        "de": "en",
    }

    if source_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported source language: {source_language}"
        )

    return language_pairs[source_language]


def translate_text(text, source_language):
    """
    Translate English to German or German to English.

    Returns:
        (translated_text, execution_time)
    """

    if not text or not text.strip():
        return "", 0.0

    source_language = source_language.lower()

    target_language = get_target_language(source_language)

    start_time = time.time()

    response = client.translate_text(
        parent=parent,
        contents=[text],
        source_language_code=source_language,
        target_language_code=target_language,
    )

    execution_time = time.time() - start_time

    translated_text = response.translations[0].translated_text

    return translated_text, execution_time


if __name__ == "__main__":

    samples = [
        ("Hello, how are you?", "en"),
        ("Hallo, wie geht es dir?", "de"),
    ]

    for sample, language in samples:

        result, exec_time = translate_text(sample, language)

        print("\nOriginal:", sample)
        print("Source language:", language)
        print("Translated:", result)
        print(f"Execution time: {exec_time:.3f} seconds")
