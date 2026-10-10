"""Context-aware sensitivity classifier interface and MVP heuristic.

The Stage I implementation is a transparent policy heuristic. It is not an LLM
and the project must not present it as one. A future local model can implement
the same classifier interface without changing the video pipeline.
"""

import ipaddress
from abc import ABC, abstractmethod
from difflib import SequenceMatcher

from .config import PrivacyContext
from .models import Candidate, PrivacyDecision


PLACEHOLDERS = {
    "API_KEY": "<API_KEY>",
    "EMAIL": "<EMAIL>",
    "IP_ADDRESS": "<IP_ADDRESS>",
    "PASSWORD": "<PASSWORD>",
    "TOKEN": "<TOKEN>",
    "PROJECT_NAME": "<PROJECT_NAME>",
    "CUSTOMER": "<CUSTOMER>",
    "INTERNAL_HOST": "<INTERNAL_HOST>",
    "PERSON": "<PERSON>",
}

# OCR often misreads "<YOUR_API_KEY>" as "<YOUR_APLLKEY>" or similar. Fuzzy
# matching is limited to bracketed placeholders so that a real secret value
# can never be kept merely because it resembles an allowlisted literal.
PLACEHOLDER_SIMILARITY = 0.85

class SensitivityClassifier(ABC):
    @abstractmethod
    def classify(self, candidate: Candidate, surrounding_text: str) -> PrivacyDecision:
        """Return a structured KEEP or REPLACE decision."""


class HeuristicContextClassifier(SensitivityClassifier):
    def __init__(self, context: PrivacyContext):
        self.context = context

    def classify(self, candidate: Candidate, surrounding_text: str) -> PrivacyDecision:
        normalized = candidate.text.strip().upper()
        replacement = PLACEHOLDERS.get(candidate.entity_type, "<SENSITIVE>")

        if self._is_safe_literal(normalized):
            return PrivacyDecision(
                "KEEP",
                candidate.entity_type,
                candidate.text,
                "Value is explicitly allowlisted as a safe teaching placeholder.",
            )

        if candidate.source == "context-policy":
            return PrivacyDecision(
                "REPLACE",
                candidate.entity_type,
                replacement,
                "Value is listed as sensitive in the user context policy.",
            )

        if candidate.entity_type == "IP_ADDRESS" and self._safe_ip(candidate.text):
            return PrivacyDecision(
                "KEEP",
                candidate.entity_type,
                candidate.text,
                "Address belongs to a network allowlisted by the context policy.",
            )

        if candidate.entity_type in self.context.always_replace:
            return PrivacyDecision(
                "REPLACE",
                candidate.entity_type,
                replacement,
                "Entity type is covered by a mandatory replacement policy.",
            )

        lowered = surrounding_text.lower()
        if any(keyword in lowered for keyword in self.context.sensitive_context):
            return PrivacyDecision(
                "REPLACE",
                candidate.entity_type,
                replacement,
                "Nearby text contains a sensitive-context keyword.",
            )

        if any(keyword in lowered for keyword in self.context.safe_context):
            return PrivacyDecision(
                "KEEP",
                candidate.entity_type,
                candidate.text,
                "Nearby text indicates a safe example or documentation context.",
            )

        return PrivacyDecision(
            "REPLACE",
            candidate.entity_type,
            replacement,
            "Conservative fallback for a detected sensitive candidate.",
        )

    def _is_safe_literal(self, normalized: str) -> bool:
        if normalized in self.context.safe_literals:
            return True
        if not (normalized.startswith("<") and normalized.endswith(">")):
            return False
        return any(
            literal.startswith("<")
            and SequenceMatcher(None, normalized, literal).ratio() >= PLACEHOLDER_SIMILARITY
            for literal in self.context.safe_literals
        )

    def _safe_ip(self, value: str) -> bool:
        try:
            address = ipaddress.ip_address(value)
            return any(address in ipaddress.ip_network(network) for network in self.context.safe_networks)
        except ValueError:
            return False

