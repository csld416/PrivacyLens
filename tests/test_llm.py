import json
from pathlib import Path

import pytest

from privacylens.config import load_context
from privacylens.llm import LLMContextClassifier, OllamaClient
from privacylens.models import Candidate


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = load_context(ROOT / "config" / "context.yaml")


def candidate(text, entity_type, source="pattern"):
    return Candidate(text, entity_type, 0, len(text), (0, 0, 100, 20), source)


class FakeChat:
    def __init__(self, reply):
        self.reply = reply
        self.prompts = []

    def __call__(self, system, user):
        self.prompts.append(user)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def test_model_decides_ambiguous_candidate():
    chat = FakeChat(json.dumps({"action": "KEEP", "reason": "Documentation sample."}))
    decision = LLMContextClassifier(CONTEXT, chat).classify(
        candidate("192.168.10.24", "IP_ADDRESS"), "DOCUMENTATION EXAMPLE\nSERVER_IP=192.168.10.24"
    )
    assert (decision.action, decision.replacement, decision.decided_by) == ("KEEP", "192.168.10.24", "llm")
    assert decision.reason == "Documentation sample."


def test_model_replace_uses_typed_placeholder():
    chat = FakeChat(json.dumps({"action": "REPLACE", "reason": "Internal server."}))
    decision = LLMContextClassifier(CONTEXT, chat).classify(
        candidate("192.168.10.24", "IP_ADDRESS"), "INTERNAL CONFIGURATION"
    )
    assert (decision.action, decision.replacement, decision.decided_by) == ("REPLACE", "<IP_ADDRESS>", "llm")


def test_prompt_contains_user_context_and_screen_text():
    chat = FakeChat(json.dumps({"action": "REPLACE", "reason": "x"}))
    LLMContextClassifier(CONTEXT, chat).classify(candidate("192.168.10.24", "IP_ADDRESS"), "SCREEN LINE")
    prompt = chat.prompts[0]
    assert CONTEXT.purpose in prompt
    assert CONTEXT.guidance[0] in prompt
    assert "SCREEN LINE" in prompt
    assert "Detected value: 192.168.10.24" in prompt


def test_mandatory_policy_never_reaches_model():
    chat = FakeChat(json.dumps({"action": "KEEP", "reason": "should not be used"}))
    classifier = LLMContextClassifier(CONTEXT, chat)
    secret = classifier.classify(candidate("sk-demo-secret", "API_KEY"), "Documentation example")
    placeholder = classifier.classify(candidate("<YOUR_API_KEY>", "API_KEY"), "Production terminal")
    assert (secret.action, secret.decided_by) == ("REPLACE", "rule")
    assert (placeholder.action, placeholder.decided_by) == ("KEEP", "rule")
    assert chat.prompts == []


@pytest.mark.parametrize("reply", ["not json", json.dumps({"action": "MAYBE"}), OSError("down")])
def test_invalid_or_missing_model_falls_back_to_rules(reply):
    decision = LLMContextClassifier(CONTEXT, FakeChat(reply)).classify(
        candidate("192.168.10.24", "IP_ADDRESS"), "Internal configuration"
    )
    assert (decision.action, decision.decided_by) == ("REPLACE", "rule-fallback")


def test_same_frame_candidate_is_asked_once():
    chat = FakeChat(json.dumps({"action": "REPLACE", "reason": "x"}))
    classifier = LLMContextClassifier(CONTEXT, chat)
    for _ in range(3):
        classifier.classify(candidate("192.168.10.24", "IP_ADDRESS"), "same screen")
    assert len(chat.prompts) == 1


def test_client_refuses_non_local_endpoint():
    with pytest.raises(ValueError):
        OllamaClient("https://api.example.com")
    assert OllamaClient("http://localhost:11434").url == "http://localhost:11434"
