import shutil

import cv2
import numpy as np
import pytest

from privacylens.encode import convert_to_h264


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")
def test_mp4v_output_is_reencoded_as_h264(tmp_path):
    path = tmp_path / "clip.mp4"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 2.0, (64, 48))
    for value in (0, 128, 255):
        writer.write(np.full((48, 64, 3), value, dtype=np.uint8))
    writer.release()

    assert convert_to_h264(path)

    capture = cv2.VideoCapture(str(path))
    fourcc = int(capture.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, "little").decode().lower()
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    assert fourcc in {"avc1", "h264"}
    assert frames == 3
    assert not list(tmp_path.glob("*h264-tmp*"))


def test_missing_ffmpeg_leaves_file_untouched(tmp_path, monkeypatch):
    path = tmp_path / "clip.mp4"
    path.write_bytes(b"original")
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert convert_to_h264(path) is False
    assert path.read_bytes() == b"original"
