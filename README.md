# PrivacyLens

PrivacyLens is a Stage I offline prototype for privacy processing of recorded
videos, built for the ASUS UGen AI League. It reads the
text on screen with local OCR, finds candidate secrets with rules, lets a local
language model decide from the user's privacy context whether ambiguous values
are sensitive, and replaces sensitive values with semantic placeholders:

> Hide the value, preserve the context.

> **Status: working Stage I MVP, CPU-only.** All inference runs locally; no
> cloud API is used. Deployment on the target competition hardware (ASUS
> UGen300 / Hailo-10H, Battlefield Lightning) is Stage II work, and no accelerator
> performance is claimed.

## Architecture

```text
 recorded MP4
      |
      v
 frame extraction (OpenCV)
      |
      v
 local OCR: RapidOCR (PP-OCRv4 ONNX models on ONNX Runtime)      [neural inference]
      |
      v  text lines + bounding boxes
 rule-based candidate detection (regex)                           [rules]
 email, IPv4, API key, password, token, policy terms
      |
      v
 privacy decision for each candidate
   1. deterministic policy (config/context.yaml)                  [rules]
      allowlisted placeholders, allowlisted networks,
      mandatory types (API_KEY, EMAIL, PASSWORD, TOKEN), policy terms
   2. everything else -> local language model                     [neural inference]
      prompt = video purpose + audience + privacy guidance
               + all text on the same frame + the candidate
      output = JSON {action: KEEP | REPLACE, reason}
   3. model missing or invalid output -> keyword heuristic        [rules, fallback]
      |
      v
 semantic rendering (<EMAIL>, <IP_ADDRESS>, ...) with OpenCV
      |
      v
 protected MP4  +  JSON audit log (decision, reason, decided_by; hashes, not raw values)
```

| Component | Kind | Code |
| --- | --- | --- |
| Video read/write, rendering | Deterministic (OpenCV) | `pipeline.py`, `renderer.py` |
| OCR | Neural inference (pretrained ONNX models) | `ocr.py` |
| Candidate detection | Rules (regex, term list) | `detectors.py` |
| Mandatory policy decisions | Rules | `context.py` (`policy_decision`) |
| Context-dependent decisions | Local language model via Ollama API | `llm.py` |
| Fallback decisions | Keyword heuristic, not AI | `context.py` (`keyword_decision`) |

Mandatory secret types are never sent to the model for a decision: a model
cannot un-hide an API key. Every event in `outputs/detections.json` records
whether it was decided by `rule`, `llm`, or `rule-fallback`.

The client only accepts a loopback endpoint (`localhost`, `127.0.0.1`, `::1`), so
OCR text never leaves the machine.

## Models

| Model | Purpose | Origin | License |
| --- | --- | --- | --- |
| `ch_PP-OCRv4_det_infer.onnx` | Text detection | PaddleOCR PP-OCRv4, ONNX conversion shipped in `rapidocr-onnxruntime` 1.4.4 | Apache-2.0 |
| `ch_PP-OCRv4_rec_infer.onnx` | Text recognition | same as above | Apache-2.0 |
| `ch_ppocr_mobile_v2.0_cls_infer.onnx` | Text-direction classification | PaddleOCR v2.0, shipped in `rapidocr-onnxruntime` 1.4.4 | Apache-2.0 |
| `qwen3:4b-instruct` (Ollama, Q4_K_M, ~2.5 GB) | Context-dependent KEEP/REPLACE | Qwen3-4B-Instruct (Alibaba Qwen team) | Apache-2.0 |

No model was trained or fine-tuned by the team. Model files are downloaded by
pip and Ollama; this repository does not redistribute them.

Why Qwen3-4B-Instruct: among the models we tried it kept no sensitive value
and made the fewest errors on cases that were not used to choose the prompt
(see [Context classifier check](#context-classifier-check)), and its license is
Apache-2.0. Any Ollama model can be selected with `--llm-model`.

Hardware note: Qwen3-4B is **not** on the checked Hailo-10H GenAI model
list, whose largest Qwen text model is Qwen3-1.7B; the listed 1-2B models scored
lower in the reported development check. Deployment remains unverified.

## Requirements

- Python **3.8 – 3.12**. `rapidocr-onnxruntime` requires Python < 3.13, and
  `numpy<2.0` has no wheels for 3.13+.
- On Debian/Ubuntu, the venv module is a separate package:
  `sudo apt install python3-venv`
- [Ollama](https://ollama.com/download) for the language-model classifier
  (optional: without it the demo runs with the rule-based fallback and says so).
- About 3 GB of disk for the models. No GPU, API key, or network access is
  needed at run time (network is needed once, to download the models).

Tested environment: Linux x86_64 (Ubuntu 20.04), Python 3.8.10, Ollama 0.40.2
with GPUs disabled (CPU-only inference). Laptop hardware and other operating
systems have not yet been verified by the team.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

# language model (install Ollama first, then:)
ollama pull qwen3:4b-instruct
```

## Run the complete demo

```bash
python run_demo.py
```

The first line of output states which classifier is in use. Use
`--classifier llm` to fail instead of falling back when the model is missing,
or `--classifier rules` to run without a model.

This produces:

```text
outputs/demo_input.mp4       synthetic 21-second recorded video
outputs/demo_protected.mp4   pipeline output
outputs/demo_comparison.mp4  actual before/after view
outputs/detections.json      structured decisions, reasons, and decided_by
```

The audit log records entity types, actions, reasons, coordinates, and a
one-way hash of each candidate. It does not copy raw detected values.

The videos use the `mp4v` (MPEG-4 Part 2) codec, which VLC and most desktop
players handle but web browsers do not. To embed or preview in a browser:

```bash
ffmpeg -i outputs/demo_comparison.mp4 -c:v libx264 -pix_fmt yuv420p demo_comparison_h264.mp4
```

To process a different recorded video using the same policy:

```bash
python run_demo.py --input path/to/video.mp4
```

## Demo cases

All values are synthetic and generated by `src/privacylens/demo.py`.

| Case | Scene | Input | Output | Decided by |
| --- | --- | --- | --- | --- |
| A: obvious secrets | 2, 3 | `API_KEY=sk-demo-secret-123456`, `EMAIL=demo@example.com`, `PASSWORD=...`, `TOKEN=...` | `API_KEY=<API_KEY>`, `EMAIL=<EMAIL>`, `PASSWORD=<PASSWORD>`, `TOKEN=<TOKEN>` | rule (mandatory types) |
| B: context matters | 1 vs 3 | `SERVER_IP=192.168.10.24` in both scenes | Scene 1 (documentation): **KEEP**; scene 3 (internal configuration): `<IP_ADDRESS>` | **language model**, from the on-screen context |
| B': teaching placeholder | 1 | `API_KEY=<YOUR_API_KEY>` | **KEEP** | rule (allowlist, tolerant of OCR misreads) |
| C: meaning preserved | all | `SERVER_IP=192.168.10.24` | `SERVER_IP=<IP_ADDRESS>` | only the value is replaced; labels stay readable |

Example reasons returned by `qwen3:4b-instruct` in our run:
- scene 1: "The value is part of a documentation example with clear instructions
  for readers to substitute their own values, and is labeled as synthetic test data."
- scene 3: "The IP address belongs to an internal configuration and is part of a
  sensitive system setup, even if synthetic, as it could represent a real system
  structure in context."

The original development run reported about 10 s end to end in the tested
environment (CPU only).

## Privacy context

`config/context.yaml` tells the classifier why the video is being shared, who
will see it, and, in `guidance`, what counts as sensitive for this video in plain
language. These are passed to the language model together with the frame's
text. The same file lists mandatory types, allowlisted placeholders and
networks, project-specific sensitive terms, and the keywords used by the
fallback heuristic.

## Context classifier check

`scripts/eval_context.py` runs the classifier on 24 hand-written synthetic IP
cases, each set with 6 KEEP and 6 REPLACE:

- **dev** (12 cases): used while choosing the prompt and model.
- **holdout** (12 cases): written after the prompt was fixed and before
  Qwen3-4B was tried; the prompt was not changed for them. Most avoid obvious keywords such as
  "production" or "internal".

Reported from the 2026-10-10 development run in the tested environment above
(CPU only). The rule-based rows were reproduced during repository verification;
the Ollama model rows were not rerun on the verification machine:

| Classifier | dev | holdout | Sensitive values kept (leaks) | Time per case |
| --- | --- | --- | --- | --- |
| `qwen3:4b-instruct` (default) | 10/12 | 12/12 | 0 | 2.2 s |
| `llama3.2:3b` | 11/12 | 11/12 | 1 (holdout) | 1.2 s |
| Keyword heuristic (fallback) | 9/12 | 8/12 | 0 | < 0.01 s |
| `qwen3:1.7b` | 9/12 | not run | 3 (dev) | 8.2 s |
| `qwen2.5:1.5b-instruct` | 6/12 (always REPLACE) | not run | 0 | 1.1 s |
| `llama3.2:1b` | 6/12 (always REPLACE) | not run | 0 | 0.8 s |

`qwen3:1.7b`, `qwen2.5:1.5b-instruct`, and `llama3.2:1b` correspond to models on
Hailo's Hailo-10H list; the others do not. `qwen3:1.7b` ran with Ollama's
default thinking mode. Both errors of the default model were extra
replacements (a sample address hidden), not leaks.

```bash
python scripts/eval_context.py                      # default model, both sets
python scripts/eval_context.py --set holdout        # holdout only
python scripts/eval_context.py --classifier rules   # keyword heuristic
python scripts/eval_context.py --llm-model llama3.2:3b
```

These are development checks, **not** accuracy estimates: the cases are few
and written by the team.

## Tests

```bash
pytest
```

The tests cover every implemented detector, context-dependent decisions,
OCR-tolerant placeholder matching, semantic text replacement, and the
language-model classifier (with a fake model: prompt contents, policy override,
fallback on invalid or missing output, local-only endpoint). They do not need
Ollama.

## Known limitations

- Only IPv4 candidates currently reach the language model. The model does not
  yet discover new kinds of sensitive text (customer names, internal hostnames)
  on its own; candidates come from rules.
- The language model can be wrong, and a small evaluation set cannot show how
  often. A wrong KEEP exposes the value. Manual review of the output remains
  necessary.
- OCR errors can cause missed detections. For example, if OCR reads the label
  `API_KEY=` as `APILKEY=`, the label-based rule does not fire.
- Processing is per frame with no temporal tracking; decisions could flicker on
  real screen recordings. On a jittered 210-frame copy of the demo, every frame
  got the same decision per scene, but that video is still synthetic.
- Replacement appearance is intentionally simple and may not match the source UI.
- Audio is not copied into the output.
- Deployment on UGen300/Hailo-10H has not been implemented or verified.

## Stage II plan (not implemented)

The selected track is Battlefield Lightning. The Ollama-API client is a
candidate integration point for ASUS UGen300 / Hailo-10H through Hailo's
Ollama-compatible `hailo-ollama` server; this has not been verified. The default
Stage I model is not on the checked Hailo list, so Stage II must select and
evaluate a supported model or verify a compliant deployment path. Future work
also includes model-proposed candidates, temporal tracking, and a larger
labelled evaluation set.

## References

- RapidOCR: https://github.com/RapidAI/RapidOCR
- PaddleOCR (PP-OCR models): https://github.com/PaddlePaddle/PaddleOCR
- ONNX Runtime: https://github.com/microsoft/onnxruntime
- OpenCV: https://opencv.org/
- Ollama: https://github.com/ollama/ollama
- Qwen3: https://github.com/QwenLM/Qwen3
- Llama 3.2 (compared only): https://www.llama.com/
- Hailo-10H GenAI models: https://hailo.ai/products/hailo-software/model-explorer/generative-ai/devices/hailo-10h/
- Hailo Model Zoo GenAI model list: https://github.com/hailo-ai/hailo_model_zoo_genai/blob/main/docs/MODELS.rst
- hailo-ollama: https://community.hailo.ai/t/hailo-ollama-support-for-model-explorer-genai-models/19275

## License

This project is released under the MIT License (see `LICENSE`). Third-party
components keep their own licenses; see `THIRD_PARTY.md`.
