from pii_detector import PIIDetector

def TestPIIMasking(): 
    input_pii_detector = PIIDetector()

    text = input("Enter text containing PII: ")

    print("\nOriginal text:")
    print(text)

    # Detect PII
    detected = input_pii_detector.DetectPII(text)

    print("\nDetected PII:")

    if detected:
        for pii_type, matches in detected.items():
            print(f"{pii_type}: {matches}")
    else:
        print("No PII detected.")

    masked = input_pii_detector.MaskPII(text)

    print("\nMasked text:")
    print(masked)


if __name__ == "__main__":
    TestPIIMasking()