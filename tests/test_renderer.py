from privacylens.context import PLACEHOLDERS
from privacylens.models import Candidate, PrivacyDecision
from privacylens.renderer import replace_text


def test_replaces_only_sensitive_value_and_preserves_label():
    text = "EMAIL=demo@example.com"
    start = text.index("demo@example.com")
    item = Candidate("demo@example.com", "EMAIL", start, len(text), (0, 0, 100, 20))
    decision = PrivacyDecision("REPLACE", "EMAIL", PLACEHOLDERS["EMAIL"], "test")
    assert replace_text(text, [(item, decision)]) == "EMAIL=<EMAIL>"

