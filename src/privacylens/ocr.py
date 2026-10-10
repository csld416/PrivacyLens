"""Local RapidOCR adapter backed by ONNX Runtime."""

from typing import List, Protocol

import numpy as np
from rapidocr_onnxruntime import RapidOCR

from .models import OCRWord


class OCREngine(Protocol):
    def read(self, frame: np.ndarray) -> List[OCRWord]:
        ...


class LocalOCR:
    def __init__(self, minimum_confidence: float = 0.35):
        self.minimum_confidence = minimum_confidence
        self.engine = RapidOCR()

    def read(self, frame: np.ndarray) -> List[OCRWord]:
        result, _ = self.engine(frame)
        words = []
        for points, raw_text, raw_confidence in result or []:
            text = str(raw_text).strip()
            confidence = float(raw_confidence)
            if not text or confidence < self.minimum_confidence:
                continue
            xs = [int(point[0]) for point in points]
            ys = [int(point[1]) for point in points]
            left, top = min(xs), min(ys)
            right, bottom = max(xs), max(ys)
            words.append(
                OCRWord(
                    text=text,
                    bbox=(left, top, right - left, bottom - top),
                    confidence=confidence,
                )
            )
        return words

