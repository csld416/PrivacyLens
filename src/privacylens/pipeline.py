"""End-to-end offline recorded-video processing pipeline."""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

from .config import PrivacyContext
from .context import SensitivityClassifier
from .detectors import detect_candidates
from .models import Candidate, OCRWord, PrivacyDecision
from .ocr import OCREngine
from .renderer import render_replacement, replace_text


class VideoPipeline:
    def __init__(self, ocr: OCREngine, classifier: SensitivityClassifier, context: PrivacyContext):
        self.ocr = ocr
        self.classifier = classifier
        self.context = context

    def process(self, input_path: Path, output_path: Path, log_path: Path) -> Dict[str, int]:
        capture = cv2.VideoCapture(str(input_path))
        if not capture.isOpened():
            raise ValueError("could not open input video: {}".format(input_path))

        fps = capture.get(cv2.CAP_PROP_FPS) or 2.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            capture.release()
            raise ValueError("could not create output video: {}".format(output_path))

        cache: Dict[str, Tuple[np.ndarray, List[dict]]] = {}
        events: List[dict] = []
        frame_index = 0
        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    break
                fingerprint = self._visual_fingerprint(frame)
                if fingerprint in cache:
                    processed, _ = cache[fingerprint]
                    writer.write(processed)
                else:
                    processed, frame_events = self._process_frame(frame, frame_index)
                    cache[fingerprint] = (processed.copy(), frame_events)
                    events.extend(frame_events)
                    writer.write(processed)
                frame_index += 1
        finally:
            capture.release()
            writer.release()

        report = {
            "input": str(input_path),
            "output": str(output_path),
            "frames": frame_index,
            "unique_frames_analyzed": len(cache),
            "replace_decisions": sum(event["action"] == "REPLACE" for event in events),
            "keep_decisions": sum(event["action"] == "KEEP" for event in events),
            "events": events,
        }
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        return {
            "frames": frame_index,
            "unique_frames_analyzed": len(cache),
            "replace_decisions": report["replace_decisions"],
            "keep_decisions": report["keep_decisions"],
        }

    @staticmethod
    def _visual_fingerprint(frame: np.ndarray) -> bytes:
        """Create a compression-tolerant signature for static video scenes."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (33, 18), interpolation=cv2.INTER_AREA)
        return np.packbits(small[:, 1:] > small[:, :-1]).tobytes()

    def _process_frame(self, frame: np.ndarray, frame_index: int) -> Tuple[np.ndarray, List[dict]]:
        output = frame.copy()
        words = self.ocr.read(frame)
        surrounding_text = " ".join(word.text for word in words)
        events = []
        for word in words:
            decisions: List[Tuple[Candidate, PrivacyDecision]] = []
            for candidate in detect_candidates(word, self.context.sensitive_terms):
                decision = self.classifier.classify(candidate, surrounding_text)
                decisions.append((candidate, decision))
                events.append(
                    {
                        "frame": frame_index,
                        "candidate_sha256": hashlib.sha256(candidate.text.encode("utf-8")).hexdigest(),
                        "entity_type": decision.entity_type,
                        "action": decision.action,
                        "replacement": decision.replacement,
                        "reason": decision.reason,
                        "bbox": list(word.bbox),
                    }
                )
            if any(decision.action == "REPLACE" for _, decision in decisions):
                render_replacement(output, word.bbox, replace_text(word.text, decisions))
        return output, events

