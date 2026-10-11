"""Re-encode OpenCV output as H.264 so QuickTime and web browsers can play it.

OpenCV's pip wheels write MPEG-4 Part 2 (`mp4v`), which VLC plays but QuickTime
on macOS and most browsers show as a green or blank picture. The external
`ffmpeg` program is optional; without it the files stay in `mp4v`.
"""

import shutil
import subprocess
from pathlib import Path


def convert_to_h264(path: Path) -> bool:
    """Replace `path` with an H.264 copy. Return False if ffmpeg is unavailable or fails."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        return False
    temporary = path.with_name(path.stem + ".h264-tmp.mp4")
    result = subprocess.run(
        [
            ffmpeg, "-y", "-v", "error", "-i", str(path),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(temporary),
        ],
        check=False,
    )
    if result.returncode != 0 or not temporary.exists():
        temporary.unlink(missing_ok=True)
        return False
    temporary.replace(path)
    return True
