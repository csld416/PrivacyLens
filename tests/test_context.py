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



def test_same_ip_decision_depends_on_context():
    value = "192.168.10.24"
    documentation = CLASSIFIER.classify(candidate(value, "IP_ADDRESS"), "Documentation example SERVER_IP=" + value)
    internal = CLASSIFIER.classify(candidate(value, "IP_ADDRESS"), "Internal configuration SERVER_IP=" + value)
    assert documentation.action == "KEEP"
    assert internal.action == "REPLACE"
    assert internal.replacement == "<IP_ADDRESS>"


def test_ocr_misread_placeholder_is_still_kept():
    for misread in ("<YOUR_APLLKEY>", "<YOUR_APILKEY>", "<YOUR_APL_KEY>"):
        decision = CLASSIFIER.classify(candidate(misread, "API_KEY"), "Documentation example")
        assert decision.action == "KEEP", misread


def test_fuzzy_placeholder_match_never_keeps_unbracketed_value():
    decision = CLASSIFIER.classify(candidate("YOUR_APLLKEY", "API_KEY"), "Documentation example")
    assert decision.action == "REPLACE"
