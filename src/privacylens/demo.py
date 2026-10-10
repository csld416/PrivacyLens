"""Generate controlled synthetic video and a side-by-side result."""

from pathlib import Path
from typing import List, Sequence

import cv2
import numpy as np


WIDTH = 1280
HEIGHT = 720
FPS = 2.0


SCENES: Sequence[Sequence[str]] = (
    (
        "DOCUMENTATION EXAMPLE (SAFE PLACEHOLDER)",
        "How to configure the SDK:",
        "API_KEY=<YOUR_API_KEY>",
        "This placeholder is intended for public tutorials.",
    ),
    (
        "PRODUCTION TERMINAL (SENSITIVE)",
        "Deploying Project Apollo",
        "API_KEY=sk-demo-secret-123456",
        "PrivacyLens should preserve meaning, not the value.",
    ),
    (
        "INTERNAL CONFIGURATION (SENSITIVE)",
        "EMAIL=demo@example.com",
        "SERVER_IP=192.168.10.24",
        "PASSWORD=demo-password-123",
        "TOKEN=demo-token-987654",
    ),
)


def create_demo_video(path: Path, seconds_per_scene: int = 7) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (WIDTH, HEIGHT),
    )
    if not writer.isOpened():
        raise ValueError("could not create demo video: {}".format(path))
    try:
        for scene_number, lines in enumerate(SCENES, start=1):
            frame = _scene_frame(scene_number, lines)
            for _ in range(int(FPS * seconds_per_scene)):
                writer.write(frame)
    finally:
        writer.release()


def create_comparison_video(input_path: Path, protected_path: Path, output_path: Path) -> None:
    original = cv2.VideoCapture(str(input_path))
    protected = cv2.VideoCapture(str(protected_path))
    if not original.isOpened() or not protected.isOpened():
        raise ValueError("could not open videos for comparison")
    fps = original.get(cv2.CAP_PROP_FPS) or FPS
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (WIDTH, HEIGHT // 2),
    )
    if not writer.isOpened():
        raise ValueError("could not create comparison video")
    try:
        while True:
            left_ok, left = original.read()
            right_ok, right = protected.read()
            if not left_ok or not right_ok:
                break
            left = cv2.resize(left, (WIDTH // 2, HEIGHT // 2))
            right = cv2.resize(right, (WIDTH // 2, HEIGHT // 2))
            cv2.rectangle(left, (0, 0), (190, 36), (35, 42, 52), -1)
            cv2.rectangle(right, (0, 0), (250, 36), (35, 42, 52), -1)
            cv2.putText(left, "RAW VIDEO", (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (230, 230, 230), 2)
            cv2.putText(right, "PRIVACY-PROTECTED", (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (80, 220, 160), 2)
            writer.write(np.hstack((left, right)))
    finally:
        original.release()
        protected.release()
        writer.release()


def _scene_frame(scene_number: int, lines: Sequence[str]) -> np.ndarray:
    frame = np.full((HEIGHT, WIDTH, 3), (18, 24, 32), dtype=np.uint8)
    cv2.rectangle(frame, (40, 35), (WIDTH - 40, HEIGHT - 35), (31, 39, 49), -1)
    cv2.rectangle(frame, (40, 35), (WIDTH - 40, 92), (48, 58, 71), -1)
    cv2.putText(
        frame,
        "PrivacyLens Synthetic Demo | Scene {}/{}".format(scene_number, len(SCENES)),
        (68, 73),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (235, 235, 235),
        2,
        cv2.LINE_AA,
    )
    y = 165
    for index, line in enumerate(lines):
        color = (125, 215, 255) if index == 0 else (232, 236, 240)
        scale = 0.85 if index == 0 else 0.9
        cv2.putText(frame, line, (85, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)
        y += 90
    cv2.putText(
        frame,
        "All values shown are synthetic test data.",
        (85, HEIGHT - 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (155, 165, 175),
        1,
        cv2.LINE_AA,
    )
    return frame

