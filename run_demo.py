#!/usr/bin/env python3
"""Run the complete synthetic PrivacyLens demonstration."""

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from privacylens.config import load_context  # noqa: E402
from privacylens.context import HeuristicContextClassifier  # noqa: E402
from privacylens.demo import create_comparison_video, create_demo_video  # noqa: E402
from privacylens.encode import convert_to_h264  # noqa: E402
from privacylens.llm import DEFAULT_MODEL, DEFAULT_URL, LLMContextClassifier, OllamaClient  # noqa: E402
from privacylens.ocr import LocalOCR  # noqa: E402
from privacylens.pipeline import VideoPipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the offline PrivacyLens demo")
    parser.add_argument("--input", type=Path, help="process an existing recorded video")
    parser.add_argument("--context", type=Path, default=ROOT / "config" / "context.yaml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument(
        "--classifier",
        choices=("auto", "llm", "rules"),
        default="auto",
        help="auto: use the local language model if available, otherwise rules",
    )
    parser.add_argument("--llm-url", default=DEFAULT_URL, help="local Ollama-compatible server")
    parser.add_argument("--llm-model", default=DEFAULT_MODEL)
    return parser.parse_args()


def build_classifier(args: argparse.Namespace, context):
    if args.classifier == "rules":
        print("Classifier: rule-based heuristic (--classifier rules)")
        return HeuristicContextClassifier(context)

    client = OllamaClient(args.llm_url, args.llm_model)
    if client.available():
        print("Classifier: local language model {} at {}".format(args.llm_model, args.llm_url))
        return LLMContextClassifier(context, client.chat)
    if args.classifier == "llm":
        raise SystemExit(
            "Language model {} is not available at {}. Start Ollama and run: ollama pull {}".format(
                args.llm_model, args.llm_url, args.llm_model
            )
        )
    print("WARNING: language model {} not available at {}; using the rule-based heuristic.".format(
        args.llm_model, args.llm_url
    ))
    return HeuristicContextClassifier(context)


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_path = args.input or args.output_dir / "demo_input.mp4"
    if args.input is None:
        print("1/5 Creating synthetic input video...")
        create_demo_video(input_path)

    protected_path = args.output_dir / "demo_protected.mp4"
    log_path = args.output_dir / "detections.json"
    context = load_context(args.context)
    pipeline = VideoPipeline(LocalOCR(), build_classifier(args, context), context)

    print("2/5 Running local OCR and privacy processing...")
    summary = pipeline.process(input_path, protected_path, log_path)
    if args.input is None:
        print("3/5 Creating actual before/after comparison...")
        create_comparison_video(input_path, protected_path, args.output_dir / "demo_comparison.mp4")
    else:
        print("3/5 Skipping comparison for custom input.")

    # Only re-encode files this script wrote; never touch a user-supplied input.
    written = [protected_path]
    if args.input is None:
        written = [input_path, protected_path, args.output_dir / "demo_comparison.mp4"]
    print("4/5 Re-encoding videos as H.264 for QuickTime and browsers...")
    if all(convert_to_h264(path) for path in written):
        print("  Videos are H.264.")
    else:
        print("  NOTE: ffmpeg with libx264 not found or failed; videos stay in mp4v format.")
        print("  Play them with VLC, or install ffmpeg (brew install ffmpeg / apt install ffmpeg).")

    print("5/5 Done")
    print("  Input: {}".format(input_path))
    print("  Protected: {}".format(protected_path))
    print("  Detection log: {}".format(log_path))
    if args.input is None:
        print("  Comparison: {}".format(args.output_dir / "demo_comparison.mp4"))
    print("  Summary: {}".format(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

