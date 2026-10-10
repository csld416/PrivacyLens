"""Cover sensitive OCR regions and draw semantic replacements."""

from typing import Sequence, Tuple

import cv2
import numpy as np

from .models import Candidate, PrivacyDecision


def replace_text(text: str, replacements: Sequence[Tuple[Candidate, PrivacyDecision]]) -> str:
    transformed = text
    for candidate, decision in sorted(replacements, key=lambda item: item[0].start, reverse=True):
        if decision.action == "REPLACE":
            transformed = transformed[: candidate.start] + decision.replacement + transformed[candidate.end :]
    return transformed


def render_replacement(frame: np.ndarray, bbox: Tuple[int, int, int, int], text: str) -> None:
    x, y, width, height = bbox
    padding = 4
    left = max(0, x - padding)
    top = max(0, y - padding)
    right = min(frame.shape[1] - 1, x + width + padding)
    bottom = min(frame.shape[0] - 1, y + height + padding)
    cv2.rectangle(frame, (left, top), (right, bottom), (18, 24, 32), thickness=-1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max(0.4, min(0.9, height / 25.0))
    thickness = max(1, int(round(scale * 2)))
    text_width = cv2.getTextSize(text, font, scale, thickness)[0][0]
    if text_width > right - left and text_width > 0:
        scale *= (right - left) / text_width
        scale = max(0.3, scale)
        thickness = max(1, int(round(scale * 2)))
    baseline = min(bottom - 2, top + max(height, 14))
    cv2.putText(frame, text, (left + 2, baseline), font, scale, (80, 220, 160), thickness, cv2.LINE_AA)

