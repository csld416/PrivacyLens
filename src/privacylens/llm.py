"""Local language-model context classifier over an Ollama-compatible API.

The model decides KEEP or REPLACE for candidates that the deterministic policy
leaves open, using the user's privacy context and the text on the same frame.
Requests are only sent to a loopback address so that OCR text never leaves the
machine. Hailo's hailo-ollama server exposes an Ollama-compatible API; running
this client against it is planned for Stage II and has not been verified.
"""

import json
import urllib.request
from typing import Callable, Dict, Optional, Tuple
from urllib.parse import urlparse

from .config import PrivacyContext
from .context import HeuristicContextClassifier, SensitivityClassifier, placeholder_for
from .models import Candidate, PrivacyDecision


DEFAULT_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen3:4b-instruct"
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}

DECISION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["KEEP", "REPLACE"]},
        "reason": {"type": "string"},
    },
    "required": ["action", "reason"],
}

SYSTEM_PROMPT = (
    "You are a privacy reviewer for a screen recording that will be published. "
    "Decide whether one detected value must be hidden before publishing. "
    "Use the video purpose, the audience, the privacy guidance, and the other text "
    "visible on the same screen. "
    "Answer REPLACE if showing the value could expose a real system, account, person, "
    "or internal information in this context. "
    "Answer KEEP only if the value is clearly a public example, documentation sample, "
    "or otherwise harmless in this context. "
    "The video purpose describes the whole video; judge the detected value by what this "
    "particular screen shows. "
    'Respond with JSON only: {"action": "KEEP" or "REPLACE", "reason": "<one short sentence>"}'
    "\n\nExamples (not from this video):\n"
    "Screen: 'Getting started: set HOST=10.9.9.9 or replace it with your own machine.' "
    "Value 10.9.9.9 -> KEEP (sample value readers replace)\n"
    "Screen: 'payments-prod cluster | node ip 10.44.1.7 | CPU 81%' "
    "Value 10.44.1.7 -> REPLACE (address of a specific real system)\n"
    "Screen: 'Textbook figure: hosts 192.168.3.2 and 192.168.3.3 on one subnet.' "
    "Value 192.168.3.2 -> KEEP (teaching illustration)\n"
    "Screen: 'ssh deploy@172.20.5.11  # Contoso customer staging' "
    "Value 172.20.5.11 -> REPLACE (a customer's server)"
)

ChatFunction = Callable[[str, str], str]


class OllamaClient:
    def __init__(self, url: str = DEFAULT_URL, model: str = DEFAULT_MODEL, timeout: float = 120.0):
        host = urlparse(url).hostname
        if host not in LOOPBACK_HOSTS:
            raise ValueError("refusing non-local language-model endpoint: {}".format(url))
        self.url = url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def available(self) -> bool:
        """Return True if the server is reachable and has the model installed."""
        try:
            tags = self._request("/api/tags", None, timeout=5.0)
        except (OSError, ValueError):
            return False
        names = {item.get("name", "") for item in tags.get("models", [])}
        return self.model in names or self.model + ":latest" in names

    def chat(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "format": DECISION_SCHEMA,
            "options": {"temperature": 0, "seed": 0},
        }
        response = self._request("/api/chat", payload, timeout=self.timeout)
        return str(response["message"]["content"])

    def _request(self, path: str, payload: Optional[dict], timeout: float) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.url + path,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))


class LLMContextClassifier(SensitivityClassifier):
    """Policy rules first, then a local language model, then the keyword fallback."""

    def __init__(self, context: PrivacyContext, chat: ChatFunction):
        self.context = context
        self.chat = chat
        self.rules = HeuristicContextClassifier(context)
        self._cache: Dict[Tuple[str, str, str], PrivacyDecision] = {}

    def classify(self, candidate: Candidate, surrounding_text: str) -> PrivacyDecision:
        policy = self.rules.policy_decision(candidate)
        if policy is not None:
            return policy

        key = (candidate.text, candidate.entity_type, surrounding_text)
        if key not in self._cache:
            self._cache[key] = self._ask_model(candidate, surrounding_text)
        return self._cache[key]

    def build_prompt(self, candidate: Candidate, surrounding_text: str) -> str:
        guidance = "\n".join("- " + item for item in self.context.guidance) or "- (none)"
        return (
            "Video purpose: {purpose}\n"
            "Audience: {audience}\n"
            "Privacy guidance:\n{guidance}\n\n"
            "Text visible on the same screen:\n{screen}\n\n"
            "Detected value: {value}\n"
            "Detected type: {entity_type}"
        ).format(
            purpose=self.context.purpose,
            audience=self.context.audience,
            guidance=guidance,
            screen=surrounding_text,
            value=candidate.text,
            entity_type=candidate.entity_type,
        )

    def _ask_model(self, candidate: Candidate, surrounding_text: str) -> PrivacyDecision:
        try:
            raw = self.chat(SYSTEM_PROMPT, self.build_prompt(candidate, surrounding_text))
            answer = json.loads(raw)
            action = str(answer["action"]).strip().upper()
            reason = str(answer.get("reason", "")).strip() or "No reason given by the model."
            if action not in {"KEEP", "REPLACE"}:
                raise ValueError("unexpected action: {}".format(action))
        except (OSError, ValueError, KeyError, TypeError) as error:
            fallback = self.rules.keyword_decision(candidate, surrounding_text)
            return PrivacyDecision(
                fallback.action,
                fallback.entity_type,
                fallback.replacement,
                "Language model unavailable or invalid output ({}); {}".format(
                    type(error).__name__, fallback.reason
                ),
                "rule-fallback",
            )

        replacement = candidate.text if action == "KEEP" else placeholder_for(candidate.entity_type)
        return PrivacyDecision(action, candidate.entity_type, replacement, reason, "llm")
