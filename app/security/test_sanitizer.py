from sanitizer import InputSanitizer

def TestSanitizer():
    input_sanitizer = InputSanitizer()

    while True:
        user_input = input("\nEnter your message: ")

        if user_input.lower() in {"exit", "quit"}:
            break

        is_safe, reason = input_sanitizer.InputCheck(user_input)

        print(f"\nSafe: {is_safe}")

        if reason:
            print(f"Reason: {reason}")
        else:
            print(f"Cleaned: {input_sanitizer.InputCheck(user_input)}")



if __name__ == "__main__":
    TestSanitizer()
