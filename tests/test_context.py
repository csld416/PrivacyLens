from pathlib import Path

from privacylens.config import load_context
from privacylens.context import HeuristicContextClassifier
from privacylens.models import Candidate


ROOT = Path(__file__).resolve().parents[1]
CLASSIFIER = HeuristicContextClassifier(load_context(ROOT / "config" / "context.yaml"))


def candidate(text, entity_type, source="pattern"):
    return Candidate(text, entity_type, 0, len(text), (0, 0, 100, 20), source)


def test_safe_placeholder_is_kept():
    decision = CLASSIFIER.classify(candidate("<YOUR_API_KEY>", "API_KEY"), "Documentation example")
    assert decision.action == "KEEP"


def test_actual_api_key_is_replaced_even_in_documentation():
    decision = CLASSIFIER.classify(candidate("sk-demo-secret", "API_KEY"), "Documentation example")
    assert decision.action == "REPLACE"
    assert decision.replacement == "<API_KEY>"


def test_allowlisted_loopback_address_is_kept():
    decision = CLASSIFIER.classify(candidate("127.0.0.1", "IP_ADDRESS"), "localhost tutorial")
    assert decision.action == "KEEP"


def test_policy_sensitive_project_is_replaced():
    decision = CLASSIFIER.classify(
        candidate("Project Apollo", "PROJECT_NAME", "context-policy"),
        "Internal deployment",
    )
    assert decision.action == "REPLACE"
    assert decision.replacement == "<PROJECT_NAME>"

