from app.security.output_validator import OutputValidator

def test_output_validation():
    """Demonstrate output validation."""

    text_validator = OutputValidator()

    outputs = [
        "The capital of France is Paris.",
        "Contact support at help@company.com for assistance.",
        "Here's how to hack into the system...",
    ]

    print("\nOutput Validation Demo:\n")

    for output in outputs:
        is_valid, cleaned, reason = text_validator.ValidateText(output)
        status = "VALID" if is_valid else "CLEANED"
        print(f"{status}: {output[:50]}...")
        if reason:
            print(f"Reason: {reason}")
            print(f"Cleaned: {cleaned[:50]}...")

if __name__ == "__main__":
    test_output_validation()