# PrivacyLens

PrivacyLens is a Stage I offline prototype for privacy processing of recorded
videos. It uses local OCR, deterministic secret detection, a configurable
context policy, and semantic placeholders to hide sensitive values while
preserving meaning.

> Status: working MVP. The current context classifier is a transparent heuristic,
> not an LLM. Local-model integration and UGen300/Hailo-10H deployment remain
> future work and no accelerator performance is claimed.

## What the demo proves

- Reads and reconstructs a recorded MP4 with OpenCV.
- Runs RapidOCR locally through ONNX Runtime.
- Detects email, IPv4, API-key-like, password, and token values with rules.
- Loads the sharing purpose and privacy policy from `config/context.yaml`.
- Makes structured `KEEP` or `REPLACE` decisions.
- Keeps the teaching placeholder `<YOUR_API_KEY>` while replacing a secret-like
  value with `<API_KEY>`.
- Creates the input, protected output, comparison video, and JSON audit log from
  controlled synthetic data.

## Requirements

- Python 3.8 or later
- A local environment capable of writing MP4 through OpenCV

Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the complete demo

```bash
python run_demo.py
```

This produces:

```text
outputs/demo_input.mp4       synthetic 21-second recorded video
outputs/demo_protected.mp4   pipeline output
outputs/demo_comparison.mp4  actual before/after view
outputs/detections.json      structured decisions and reasons
```

The audit log records entity types, actions, reasons, coordinates, and a
one-way hash of each candidate. It does not copy raw detected values.

To process a different recorded video using the same policy:

```bash
python run_demo.py --input path/to/video.mp4
```

## Privacy context

`config/context.yaml` tells the classifier why the video is being shared, who
will see it, which entity types must be replaced, which teaching placeholders
are safe, and which project-specific terms are sensitive. Raw frames and OCR
text never leave the local process.

Decision flow:

```text
Recorded video -> local OCR -> rule candidates -> context policy
               -> KEEP/REPLACE -> semantic rendering -> protected MP4
```

Mandatory secret types override general safe-context keywords. Explicit safe
teaching placeholders and allowlisted networks can still be kept.

## Tests

```bash
pytest
```

The tests cover every implemented detector, context-dependent decisions, and
semantic text replacement.

## Known limitations

- OCR errors can cause missed detections; manual review remains necessary.
- Replacement appearance is intentionally simple and may not match the source UI.
- The heuristic classifier demonstrates the context-policy interface but is not
  neural inference or AI reasoning.
- Audio is not copied into the MVP output.
- UGen300/Hailo-10H deployment has not been implemented or verified.

See `THIRD_PARTY.md` for dependency licenses. The repository's own license is
not yet selected; the team must choose one before public release.
