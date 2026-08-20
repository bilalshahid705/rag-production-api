import re

class PIIDetector:

    PATTERNS = {
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),

        "phone": re.compile(
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
        ),

        "ssn": re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b"
        ),

        "credit_card": re.compile(
            r"\b\d{4}[-\s]?\d{4}[-\s]?"
            r"\d{4}[-\s]?\d{4}\b"
        ),
    }

    MASK_MAP = {
        "email": "[EMAIL_REDACTED]",
        "credit_card": "[CREDIT_CARD_REDACTED]",
        "phone": "[PHONE_REDACTED]",
        "ssn": "[SSN_REDACTED]",
    }

    # Detect PII types present in text.
    def DetectPII(self, text: str) -> dict[str, list[str]]:
        """Detect PII in text."""
        found = {}
        for pii_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                found[pii_type] = matches
        return found

    def MaskPII(self, text: str) -> str:
        """Mask PII in text."""
        masked = text
        for pii_type, pattern in self.PATTERNS.items():
            if pii_type == "email":
                masked = re.sub(pattern, "[EMAIL REDACTED]", masked)
            elif pii_type == "phone":
                masked = re.sub(pattern, "[PHONE REDACTED]", masked)
            elif pii_type == "ssn":
                masked = re.sub(pattern, "[SSN REDACTED]", masked)
            elif pii_type == "credit_card":
                masked = re.sub(pattern, "[CARD REDACTED]", masked)
            elif pii_type == "ip_address":
                masked = re.sub(pattern, "[IP REDACTED]", masked)
        return masked