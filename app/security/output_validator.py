import re
from typing import Optional
from app.security.pii_detector import PIIDetector

class OutputValidator:
    """Validate LLM outputs before returning to user."""

    def __init__(self):
        self.pii_detector = PIIDetector()

    def ValidateText(self, output: str) -> tuple[bool, str, Optional[str]]:
        """
        Validate output.
        Returns: (is_valid, cleaned_output, reason_if_invalid)
        """
        # Check for PII leakage
        pii_found = self.pii_detector.DetectPII(output)
        if pii_found:
            cleaned_text = self.pii_detector.MaskPII(output)
            return False, cleaned_text, f"PII detected and masked: {list(pii_found.keys())}"

        # Check for harmful content patterns
        harmful_patterns = [
            r"here('s| is) (how|the way) to (hack|steal|attack)",
            r"password is",
            r"api[_\s]?key",
        ]

        for pattern in harmful_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return (
                    False,
                    "[CONTENT BLOCKED]",
                    "Potentially harmful content detected",
                )

        return True, output, None