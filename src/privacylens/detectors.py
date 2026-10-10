"""Deterministic candidate detection.

These detectors are intentionally described as rules, not AI.
"""

import ipaddress
import re
from typing import Iterable, List, Sequence

from .config import SensitiveTerm
from .models import Candidate, OCRWord


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
IPV4_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
ASSIGNMENT_RE = re.compile(
    r"(?P<label>API[_-]?KEY|PASSWORD|PASSWD|PWD|TOKEN)\s*[:=]\s*"
    r"(?P<value><[^>\s]+>|[^\s]+)",
    re.IGNORECASE,
)
GENERIC_API_KEY_RE = re.compile(r"\bsk-[A-Z0-9][A-Z0-9_-]{5,}\b", re.IGNORECASE)


def _candidate(word: OCRWord, entity_type: str, start: int, end: int, source: str = "pattern") -> Candidate:
    return Candidate(
        text=word.text[start:end],
        entity_type=entity_type,
        start=start,
        end=end,
        bbox=word.bbox,
        source=source,
    )


def detect_patterns(word: OCRWord) -> List[Candidate]:
    found: List[Candidate] = []

    for match in EMAIL_RE.finditer(word.text):
        found.append(_candidate(word, "EMAIL", match.start(), match.end()))

    for match in IPV4_RE.finditer(word.text):
        try:
            ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        found.append(_candidate(word, "IP_ADDRESS", match.start(), match.end()))

    occupied = [(item.start, item.end) for item in found]
    for match in ASSIGNMENT_RE.finditer(word.text):
        label = match.group("label").upper().replace("-", "_")
        entity_type = "API_KEY" if label in {"API_KEY", "APIKEY"} else "TOKEN" if label == "TOKEN" else "PASSWORD"
        start, end = match.span("value")
        found.append(_candidate(word, entity_type, start, end))
        occupied.append((start, end))

    for match in GENERIC_API_KEY_RE.finditer(word.text):
        if any(start <= match.start() and match.end() <= end for start, end in occupied):
            continue
        found.append(_candidate(word, "API_KEY", match.start(), match.end()))

    return _deduplicate(found)


def detect_sensitive_terms(word: OCRWord, terms: Sequence[SensitiveTerm]) -> List[Candidate]:
    found = []
    lowered = word.text.lower()
    for term in terms:
        start = lowered.find(term.value.lower())
        while start >= 0:
            found.append(_candidate(word, term.entity_type, start, start + len(term.value), "context-policy"))
            start = lowered.find(term.value.lower(), start + len(term.value))
    return found


def detect_candidates(word: OCRWord, terms: Sequence[SensitiveTerm]) -> List[Candidate]:
    return _deduplicate([*detect_patterns(word), *detect_sensitive_terms(word, terms)])


def _deduplicate(candidates: Iterable[Candidate]) -> List[Candidate]:
    unique = {}
    for item in candidates:
        unique[(item.entity_type, item.start, item.end)] = item
    return sorted(unique.values(), key=lambda item: (item.start, item.end, item.entity_type))

