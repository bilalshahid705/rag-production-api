from app.security.output_validator import OutputValidator
from app.security.pii_detector import PIIDetector
from app.security.sanitizer import InputSanitizer
from langsmith import traceable 

class SecurityPipeline:
    def __init__(self) -> None:
        self.sanitizer = InputSanitizer()
        self.pii_detector = PIIDetector()
        self.output_validator = OutputValidator()

    
    @traceable(name="security_check_input")
    def CheckInput(self, text: str) -> tuple[bool, str, list[str]]:

        notes = []

        #S tep 1: Check for injection
        is_safe, reason = self.sanitizer.InputCheck(text)
        if not is_safe:
            return False, "", [reason]

        # Step 2: Clean Input
        cleaned_input = self.sanitizer.InputClean(text)

        # Step 3: Mask PII before it reaches the LLM
        pii_found = self.pii_detector.DetectPII(cleaned_input)
        if pii_found: 
            cleaned_input = self.pii_detector.MaskPII(cleaned_input)
            notes.append(f"Input PII masked: {list(pii_found.keys())}")

        return True, cleaned_input, notes

    
    @traceable(name="security_check_output")
    def CheckOutput(self, text: str) -> tuple[str, list[str]]:
        _, cleaned_output, reason = self.output_validator.ValidateText(text)
        notes = [reason] if reason else []
        return cleaned_output, notes

