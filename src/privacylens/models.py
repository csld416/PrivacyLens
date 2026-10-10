"""Shared data models for OCR, detection, and privacy decisions."""

from dataclasses import dataclass
from typing import Tuple


BBox = Tuple[int, int, int, int]


@dataclass(frozen=True)
class OCRWord:
    text: str
    bbox: BBox
    confidence: float


@dataclass(frozen=True)
class Candidate:
    text: str
    entity_type: str
    start: int
    end: int
    bbox: BBox
    source: str = "pattern"


@dataclass(frozen=True)
class PrivacyDecision:
    action: str
    entity_type: str
    replacement: str
    reason: str

