from privacylens.detectors import detect_patterns
from privacylens.models import OCRWord


def word(text):
    return OCRWord(text=text, bbox=(0, 0, 100, 20), confidence=99.0)


def types_and_values(text):
    return [(item.entity_type, item.text) for item in detect_patterns(word(text))]


def test_detects_email():
    assert types_and_values("EMAIL=demo@example.com") == [("EMAIL", "demo@example.com")]


def test_detects_valid_ipv4_only():
    assert types_and_values("SERVER_IP=192.168.10.24") == [("IP_ADDRESS", "192.168.10.24")]
    assert types_and_values("SERVER_IP=999.168.10.24") == []


def test_detects_assigned_secrets():
    assert types_and_values("API_KEY=sk-demo-secret") == [("API_KEY", "sk-demo-secret")]
    assert types_and_values("PASSWORD=demo-password") == [("PASSWORD", "demo-password")]
    assert types_and_values("TOKEN=demo-token") == [("TOKEN", "demo-token")]


def test_detects_teaching_placeholder_for_context_decision():
    assert types_and_values("API_KEY=<YOUR_API_KEY>") == [("API_KEY", "<YOUR_API_KEY>")]

