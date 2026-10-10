# Handoff: verify PrivacyLens on a fresh machine

> 給隊友：這份是給你的 AI agent 看的驗證說明。請讓 agent 讀完並照做；
> 驗證完成後，它會刪掉這個檔案。

Written on 2026-10-10 by Claude (AI coding assistant) for the PrivacyLens team.
This note is temporary. **Delete it after verification** (see the last section).

## Context

PrivacyLens is our ASUS UGen AI League Stage I entry (deadline 2026-10-14
17:00 Asia/Taipei). Read `AGENTS.md`, `regulations.md`, `GOAL.md`, `spec.md`,
and `TASKS.md` first, as `AGENTS.md` requires.

Everything was developed and tested on a single machine only: Ubuntu 20.04,
Python 3.8.10, Ollama 0.40.2, CPU-only inference. Your job is to confirm that
the repository works for someone else, following **only** the README.

Recent changes to be aware of:

- A local language-model classifier (`src/privacylens/llm.py`) now decides
  context-dependent cases (currently IPv4 addresses) through the Ollama API.
  The default model is `qwen3:4b-instruct`. Without Ollama, the demo falls back
  to the keyword heuristic and prints a warning.
- Mandatory secret types (API key, email, password, token) are still replaced by
  rules and never sent to the model.
- `scripts/eval_context.py` checks the classifier on 24 hand-written cases.
- The competition track is **Battlefield Thunderstorm** (ASUS UGen Intel Arc
  Pro B70 32GB). Running on that hardware is Stage II and has not been verified;
  this verification is about the Stage I CPU path only.

## Verification steps

Use a fresh clone and a new virtual environment. Do not reuse anything from
another checkout.

1. Clone the repository and follow the README's **Requirements** section
   exactly: venv, `pip install -r requirements.txt`, install Ollama,
   `ollama pull qwen3:4b-instruct`. Note every step that fails or is missing
   from the README.
2. Run `pytest`. Expected: 22 passed, with no Ollama needed.
3. Run `python run_demo.py`. Expected:
   - The first line reads `Classifier: local language model qwen3:4b-instruct ...`.
     If it prints a WARNING about the model being unavailable, the LLM path is
     not working. Report it.
   - The summary shows `frames: 42` and `llm_decisions` greater than 0.
     Other counts may differ slightly on other platforms.
4. Open `outputs/detections.json`:
   - Events with `"decided_by": "llm"`: frames in scene 1 (frame < 14) should
     be IP_ADDRESS -> `KEEP`, and frames in scene 3 (frame >= 28) should be
     IP_ADDRESS -> `REPLACE`. This is demo Case B: the same value, decided
     differently by context.
   - The log must contain `candidate_sha256` hashes, never raw values such as
     `sk-demo-secret-123456` or `demo-password-123`.
5. Watch `outputs/demo_comparison.mp4` (VLC works; browsers do not play `mp4v`):
   - Scene 1: `API_KEY=<YOUR_API_KEY>` and `SERVER_IP=192.168.10.24` stay
     visible. This is intended.
   - Scenes 2 and 3: no raw value may be visible on any frame. Look for
     `sk-demo-...`, `demo@example.com`, `192.168.10.24`, `demo-password-123`,
     `demo-token-987654`, and `Project Apollo`. Each must appear as a
     placeholder such as `<API_KEY>`, `<EMAIL>`, or `<IP_ADDRESS>`.
6. Run `python scripts/eval_context.py`. Reference result on our machine:
   `[dev] 10/12, 0 leaks` and `[holdout] 12/12, 0 leaks`. Small differences on
   other hardware are possible; report them rather than treating them as failures.
7. Record your environment: OS, CPU, RAM, Python version, Ollama version, and
   wall-clock time of `python run_demo.py`. A laptop result is especially
   useful; we have none yet.

## Rules while verifying

- Do not change code, prompts, or test cases to make results match. Report
  differences to the team instead.
- Do not publish any benchmark number that was not actually measured, and never
  copy the reference numbers above as if they were measured on your machine.
- Use only the synthetic demo data. Never test with real credentials.

## When verification is done

1. Report to the team: which steps passed, which failed (with error output),
   and the environment details from step 7.
2. If a README step was missing or wrong, propose a fix to the team.
3. Delete this handoff note:
   - remove the file `HANDOFF.md`;
   - remove the line that mentions `HANDOFF.md` at the top of `AGENTS.md`;
   - commit with a message such as `Remove handoff note after verification`.
