# QUICKSTART

## 1. Prerequisites
1. Python 3.10+
2. A TOEFL vocabulary list file (default: `TOFELVob.txt`)
3. An English input passage file (example: `input.txt`)

## 2. Install Dependencies
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## 3. Configure Default Runtime (Optional)
Edit `config.txt`:
```text
input=input.txt
corpus=TOFELVob.txt
output=
blanks=10
seed=
```
Priority order is: CLI args > `config.txt` > built-in defaults.

Copy `.env.example` to `.env` and fill API key when using AI mode:
```bash
cp .env.example .env
```

## 4. Run the Program
1. Minimal (use config fallback):
```bash
python main.py
```

2. Fully explicit:
```bash
python main.py --input input.txt --corpus TOFELVob.txt --blanks 10 --output demo
```

3. Interactive mode:
```bash
python main.py --interactive
```

## 5. Output Files
1. Input snapshot: `input_YYYYMMDD.txt` (or `<prefix>_input_YYYYMMDD.txt`)
2. Question file: `blanks_YYYYMMDD.txt` (or `<prefix>_blanks_YYYYMMDD.txt`)
3. Answer file: `answers_YYYYMMDD.txt` (or `<prefix>_answers_YYYYMMDD.txt`)
4. If output prefix starts with `_`, leading underscores are removed automatically.
5. If `--output` ends with `/`, it is treated as an output directory.

## 6. Quick Validation
```bash
python -m pytest -q
```
Expected: all tests pass.

## 7. Common Issues
1. Missing `input`/`corpus`
- Fix: pass CLI args or set values in `config.txt`.

2. `--blanks` invalid
- Fix: use integer `>= 1`.

3. Empty candidate pool
- Fix: ensure input text has words present in corpus whitelist.

4. Long single-line output is hard to read
- Note: generated `input/blanks` are wrapped at 80 columns by default.
