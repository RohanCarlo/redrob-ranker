# Redrob Hackathon — Intelligent Candidate Ranking

**Team:** carlo | **Contact:** rohan2072001@gmail.com

## What this does

Single-file, zero-dependency ranker that reads `candidates.jsonl` (100,000 profiles) and outputs a ranked top-100 CSV — in ~7 seconds on a CPU.

## Reproduce the submission

```bash
# Requirements: Python 3.7+, no pip installs needed
python3 ranker.py
# Writes submission.csv
```

Then validate:

```bash
python3 validate_submission.py submission.csv
# → "Submission is valid."
```

## How it works

Three-step pipeline — all pure Python stdlib:

1. **Retrieve** — O(N) streaming pass through `candidates.jsonl`; min-heap (size 400) tracks top candidates live
2. **Score** — Composite formula: `MH_GATE × disqual_mult × (0.42·skills + 0.28·exp + 0.18·signals + 0.12·edu)`
3. **Rank** — Sort top-400, take top-100, generate grounded reasoning per candidate

Key features:
- 4 must-have gates (embeddings, vector DB, eval frameworks, Python) — missing any collapses score
- 19 honeypot profiles detected and filtered via tenure vs. start-date arithmetic
- Grounded 1–2 sentence reasoning for every candidate, citing actual profile facts
- Fully deterministic — same input always produces the same output

## Compute constraints satisfied

| Constraint | Result |
|---|---|
| Runtime | ~7 seconds (limit: 5 min) |
| Memory | Streaming — 487 MB never fully loaded into RAM |
| GPU | None — pure CPU |
| Network | Zero external calls |
| pip installs | None |

## Files

| File | Purpose |
|---|---|
| `ranker.py` | Complete ranking solution (~420 lines, pure Python stdlib) |
| `validate_submission.py` | Organiser-provided validator (unchanged) |
| `submission.csv` | Ranked top-100 output |
| `fill_presentation.py` | Script that generated the submission deck |
| `Redrob_Submission_Rohan.pptx` | Submission presentation |
| `Redrob_Solution_Document.docx` | Detailed solution write-up |
| `question.md` | Challenge problem statement |
