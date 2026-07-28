from translator import translate_text
from utils.timer import measure_time

print("=" * 50)
print("Machine Translation using NLLB-200")
print("=" * 50)

while True:
    text = input("\nEnter English Text (type 'exit' to quit): ")

    if text.lower() == "exit":
        print("Exiting...")
        break

    translated_text, execution_time = measure_time(
        translate_text,
        text
    )

    print("\nTranslated Text:")
    print(translated_text)

    print(f"\nExecution Time: {execution_time:.3f} seconds")