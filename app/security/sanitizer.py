import re
from typing import Optional
# from langsmith import traceable

class InputSanitizer:

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"forget\s+(all\s+)?previous",
        r"new\s+instruction\s*:",
        r"system\s*prompt",
        r"---\s*end\s*(of)?\s*prompt",
        r"pretend\s+you\s+are",
        r"act\s+as\s(if\s+)?you",
        r"bypass\s+(all\s+)?restrictions",
        r"reveal\s+(your\the)\s+(system | instructions | prompt)",
        r"you\s+are\s+now\s+(DAN | jailbroken)",
    ]

    def __init__(self):
        self.patterns = [
            re.compile(p, re.IGNORECASE) 
            for p in self.INJECTION_PATTERNS
        ]

    # Check if input is safe. 
    def InputCheck(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Returns: (is_safe, rejection_reason)
        """
        for pattern in self.patterns:
            if pattern.search(text):
                return False, "Block: potential prompt injection detected",       
        return True, None

    # Remove dangerous delimiters from input
    def InputClean():
        text= re.sub(r'[-]{3,}', '', text)
        text= re.sub(r'[-\=]{3,}', '', text)
        text= re.replace('{{', '{ {').replace('}}', '} }')
        return text.strip()

