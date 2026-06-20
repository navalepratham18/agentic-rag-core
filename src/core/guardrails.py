import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class GuardrailProcessor:
    def __init__(self):
        # In a real Bedrock setup, this is configured via the AWS Console policies.
        # Locally, we simulate prompt injection and toxicity filters.
        self.injection_keywords = {
            "ignore all previous", 
            "system prompt", 
            "bypass", 
            "jailbreak",
            "you are now",
            "forget your instructions"
        }

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Scans the user query for malicious intent before it ever reaches the cache or agent.
        Returns (is_safe, error_message).
        """
        query_lower = query.lower()
        
        # 1. Prompt Injection Check
        if any(keyword in query_lower for keyword in self.injection_keywords):
            logger.warning(f"SECURITY ALERT: Prompt injection attempt detected: '{query}'")
            return False, "Guardrail Block: Query violates security policy."

        # 2. Length Limit (Prevents Denial of Service via massive token payloads)
        if len(query) > 1000:
            logger.warning("SECURITY ALERT: Query length exceeded maximum threshold.")
            return False, "Guardrail Block: Query is too long."

        return True, ""

# Global guardrail instance
guardrails = GuardrailProcessor()