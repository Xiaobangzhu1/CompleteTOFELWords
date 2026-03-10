# FillBlanks

A CLI tool that generates TOEFL-style fill-in-the-blank exercises from an English passage.

## Features
- File input and DeepSeek AI input (with fallback to local file path).
- Rule-based candidate filtering with staged relax strategy.
- Fixed selection order: pick 3 high-frequency words first, then fill the remaining blanks.
- Blank rendering keeps prefix ratio in `[0.4, 0.6]`.
- Output naming with date suffix `YYYYMMDD` to avoid overwrite.
- Automatic filename normalization: leading underscores in output prefix are removed.
- Wrapped text output at 80 columns for readability.
- `seed` is optional. Leave it empty for varied outputs.

## Quick Start
1. Create environment and install dependencies:
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
2. Configure optional defaults in `config.txt`.
3. Copy environment template and fill your key:
```bash
cp .env.example .env
```
Then edit `.env` and set `DEEPSEEK_API_KEY=...`.
4. Run:
```bash
python main.py
```
Or explicit:
```bash
python main.py --input input.txt --corpus TOFELVob.txt --blanks 10 --output demo
```

## Output Files
For date `20260310`, outputs are:
- `input_20260310.txt` (or `<prefix>_input_20260310.txt`)
- `blanks_20260310.txt` (or `<prefix>_blanks_20260310.txt`)
- `answers_20260310.txt` (or `<prefix>_answers_20260310.txt`)

If prefix starts with underscore, it is normalized. Example:
- `--output ioputs/_` -> `ioputs/input_20260310.txt`, `ioputs/blanks_20260310.txt`, `ioputs/answers_20260310.txt`

If output ends with `/`, it is treated as a directory. Example:
- `--output ioputs/` -> `ioputs/input_20260310.txt`, `ioputs/blanks_20260310.txt`, `ioputs/answers_20260310.txt`

## Docs
- `PRD.md`
- `IMPLEMENTATION_PLAN.md`
- `ARCHITECTURE.md`
- `ARCHITECTURE.zh-CN.md`
- `QUICKSTART.md`
