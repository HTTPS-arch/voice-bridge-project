import time
from translator import translate_text


def measure_time(fn, *args):
    """
    Measures the execution time of a function.

    Args:
        fn: The function to execute.
        *args: Arguments to pass to the function.

    Returns:
        tuple: (function_result, execution_time_in_seconds)
    """
    start = time.time()
    result = fn(*args)
    execution_time = time.time() - start
    return result, execution_time


print("=" * 50)
print("Machine Translation using NLLB-200")
print("=" * 50)

while True:
    text = input("\nEnter English Text (type 'exit' to quit): ").strip()

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