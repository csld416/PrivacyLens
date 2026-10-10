# Stage I MVP

## P0 — Must Complete

- [x] Read video using OpenCV
- [x] Extract frames
- [x] Run OCR
- [x] Detect email
- [x] Detect IPv4
- [x] Detect API-key-like strings
- [x] Detect password/token-like strings
- [x] Replace detected text with semantic placeholders
- [x] Reconstruct output video
- [x] Create synthetic demo video
- [x] Document one-command end-to-end demo

## P1 — AI Context Detection

- [x] Define sensitivity classifier interface
- [x] Implement KEEP / REPLACE decision
- [x] Create context-dependent test cases
- [x] Demo the same value with different decisions in different contexts
- [x] Local language-model classifier (Ollama) with rule fallback
- [x] Development check of classifier (`scripts/eval_context.py`, 12 dev + 12 holdout cases)
- [x] Default model chosen: `qwen3:4b-instruct` (0 leaks on 24 cases, Apache-2.0)
- [ ] Evaluate classifier on a larger, independent set
- [x] Choose competition track: Battlefield Thunderstorm (Intel Arc Pro B70 32GB)
- [ ] Stage II: verify the model and runtime on Intel Arc Pro B70 / SDV environment

## P2 — Nice to Have

- [ ] Temporal tracking
- [ ] Improve replacement appearance
- [ ] Optimize processing speed

## Explicitly Deferred

- Real-time
- Zoom
- Virtual camera
- Generative inpainting
