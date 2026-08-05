from deep_translator import GoogleTranslator
from config import SOURCE_LANGUAGE, TARGET_LANGUAGE

# ==========================================
# Load Google Translator
# ==========================================

print("Loading Google Translator...")
print("Google Translator Loaded Successfully!\n")


# ==========================================
# Translation Function
# ==========================================

def translate_text(text):

    if not text.strip():
        return ""

    try:

        translated_text = GoogleTranslator(
            source=SOURCE_LANGUAGE,
            target=TARGET_LANGUAGE
        ).translate(text)

        return translated_text

    except Exception as e:

        print("Translation Error :", e)

        return "Translation Failed"


# ==========================================
# Test Translator
# ==========================================

if __name__ == "__main__":

    print("=" * 50)
    print("GOOGLE TRANSLATOR")
    print("=" * 50)

    while True:

        text = input("\nEnter English Text (type 'exit' to quit): ")

        if text.lower() == "exit":
            print("\nProgram Closed.")
            break

        translated = translate_text(text)

        print("\nOriginal Text   :", text)
        print("Translated Text :", translated)