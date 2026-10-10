# PrivacyLens — Stage I Goal

Build a reproducible offline prototype that processes a recorded video, detects
sensitive text, and replaces sensitive values with semantic placeholders while
preserving the video's meaning.

## Deliverables

1. A repository containing the working prototype and run instructions.
2. A short demo video showing real before-and-after output from the prototype.
3. An English slide deck based only on implemented features and verified results.

The repository is the source of truth for the video and slides and must be
completed first.

## MVP

The prototype must:

- read a recorded video;
- extract frames and run local OCR;
- detect synthetic email addresses, IPv4 addresses, API-key-like strings, and
  passwords or tokens;
- make a `KEEP` or `REPLACE` decision using the surrounding context;
- replace sensitive values with typed placeholders such as `<EMAIL>` and
  `<API_KEY>`;
- reconstruct and export the processed video; and
- run end to end on controlled synthetic demo data.

## Acceptance Criteria

- A documented command runs the end-to-end demo.
- The output video is produced by the repository, not manually fabricated.
- At least one example demonstrates that context changes a `KEEP`/`REPLACE`
  decision.
- Demo inputs contain no real credentials or unrelated personal information.
- Claims in the repository, video, and slides match the implemented system.

## Non-Goals for Stage I

- real-time processing;
- live screen capture or screen sharing;
- Zoom, Google Meet, or virtual-camera integration;
- cloud APIs;
- generative inpainting; and
- Intel Arc Pro B70 performance claims without verified deployment.

Detailed product scope is defined in `spec.md`. Competition and submission
constraints in `regulations.md` take precedence over all other project files.
