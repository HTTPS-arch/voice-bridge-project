# Google Cloud Translation API v3 Configuration

GOOGLE_PROJECT_ID = "voicebridge-504507"

SOURCE_LANGUAGE = "en"

# Default target language (used only for reference)
TARGET_LANGUAGE = "fr"

# Supported target languages for user selection
LANGUAGES = {
    "1": {"name": "French", "code": "fr"},
    "2": {"name": "German", "code": "de"},
}

# ----------------------------
# Defaults for automated/non-interactive runs
# ----------------------------
# Change these to switch the default test language/voice without
# needing to type choices into the terminal each run.
DEFAULT_TARGET_LANG_KEY = "2"       # "1" = French, "2" = German
DEFAULT_VOICE_GENDER = "female"     # "male" or "female"