# PrivacyLens Handoff

This document helps the next team member reproduce and continue the Stage I
prototype. Read `AGENTS.md`, `regulations.md`, `GOAL.md`, `spec.md`, and
`TASKS.md` before changing the repository.

## Current scope

- Competition: ASUS UGen AI League, Stage I
- Selected track: Battlefield Lightning
- Target hardware: ASUS UGen300 / Hailo-10H
- Stage I runtime: offline processing of recorded video on a development PC
- Core idea: context-aware sensitive-information decisions followed by semantic
  replacement

UGen300/Hailo-10H deployment has not been implemented or verified. Do not
present development-PC measurements as accelerator results.

## Implemented

- OpenCV video reading, frame processing, replacement rendering, and MP4 output
- Local RapidOCR inference through ONNX Runtime
- Rule-based email, IPv4, API-key-like, password, token, and policy-term candidates
- User privacy context in `config/context.yaml`
- Mandatory deterministic policy rules that a model cannot override
- Optional local Ollama language-model decisions for ambiguous candidates
- Rule-based fallback when the local model is unavailable or returns invalid data
- Synthetic demo generation, comparison video, and privacy-safe JSON audit log
- Unit tests and a 24-case synthetic context-classifier development check

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest
python run_demo.py
```

Expected generated files:

```text
outputs/demo_input.mp4
outputs/demo_protected.mp4
outputs/demo_comparison.mp4
outputs/detections.json
```

Without Ollama, `run_demo.py` prints a warning and uses the transparent
rule-based fallback. To require the local model path:

```bash
ollama pull qwen3:4b-instruct
python run_demo.py --classifier llm
python scripts/eval_context.py
```

## Verification checklist

1. Run the unit tests.
2. Run the end-to-end demo from the README.
3. Confirm scene 1 keeps the teaching placeholder.
4. Confirm scenes 2 and 3 replace the synthetic secret values.
5. Confirm `outputs/detections.json` contains hashes, not raw sensitive values.
6. If Ollama is installed, confirm events with `"decided_by": "llm"` exist.
7. Report the environment and actual measurements; never copy expected numbers
   as if they were measured on a different machine.

## Remaining work

- Verify the Ollama/Qwen path on another clean machine.
- Evaluate the classifier on a larger independent set.
- Select and validate a model supported by UGen300/Hailo-10H for Stage II.
- Finish the English proposal/slides and approximately three-minute demo video.
- Add the final GitHub and unlisted demo-video links to the submission.

Use only synthetic data. Do not test with real credentials or private material.
