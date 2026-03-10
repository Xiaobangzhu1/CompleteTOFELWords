# FillBlanks

A CLI tool that generates TOEFL-style fill-in-the-blank exercises from an English passage.

> **🧪 Vibe-Coding Toy Project**
> This project was built entirely through vibe-coding — conversational AI-assisted development from scratch. It is a learning toy, not a production-grade tool. See [Known Limitations](#known-limitations) below.

---

## 中文说明

FillBlanks 是一个命令行小工具，可以把一段英文文章自动生成 TOEFL 风格的选词填空练习题。

这是一个 **vibe-coding 小玩具**：整个项目从需求、架构到代码实现，全程由 AI 对话驱动完成。它的初衷是探索"用自然语言写代码"的可能性，而非做一个完善的产品。

### 已知不足

1. **AI 供应商单一**：目前仅支持 DeepSeek，不支持 OpenAI、Claude 等其他 API。
2. **无重试/限速机制**：API 调用失败后只有回退到本地文件，没有自动重试或速率控制。
3. **无 GUI / Web 界面**：纯命令行，对非技术用户不友好。
4. **仅支持英文**：不支持中文或其他语言的填空练习。
5. **选词策略较简单**：基于词频和词表的规则筛选，没有引入 NLP 语义理解。
6. **无 token 成本控制**：AI 模式下不限制 token 消耗，大量调用可能产生费用。
7. **测试覆盖有限**：虽有 23 个单元测试，但边界场景和集成测试仍可完善。
8. **无国际化支持**：界面提示和文档混合中英文，未做系统性的 i18n。

---

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

## Known Limitations

1. **Single AI provider** — Only DeepSeek is supported; no OpenAI/Claude/etc.
2. **No retry / rate-limiting** — API failures fall back to local file input; no automatic retry or throttling.
3. **CLI only** — No GUI or web interface.
4. **English only** — Cannot generate exercises for other languages.
5. **Simple selection heuristics** — Frequency + corpus rule-based; no semantic NLP.
6. **No token cost control** — AI mode does not cap token usage.
7. **Limited test coverage** — 23 unit tests; edge cases and integration tests could be expanded.
8. **No i18n** — Prompts and docs mix Chinese and English without systematic localization.

## Docs
- `PRD.md`
- `IMPLEMENTATION_PLAN.md`
- `ARCHITECTURE.md`
- `ARCHITECTURE.zh-CN.md`
- `QUICKSTART.md`
