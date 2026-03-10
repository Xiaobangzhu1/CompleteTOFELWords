# ARCHITECTURE

## 1. System Overview
This project is a CLI-oriented TOEFL cloze generator. The runtime pipeline is:
1. Input acquisition and configuration merge.
2. Text segmentation and token extraction.
3. Candidate filtering with staged fallback rules.
4. Selection strategy execution (currently uniform random sampling).
5. Blank rendering and answer serialization.

## 2. Module Responsibilities
1. `main.py` - Application bootstrap.
   - Delegates process lifecycle to CLI entrypoint.

2. `completetofelwords/cli.py` - Command Orchestration Layer.
   - Parses CLI arguments.
   - Merges runtime config (`CLI > config.txt > defaults`).
   - Supports interactive mode and validation.
   - Executes end-to-end flow and handles user-facing errors.

3. `completetofelwords/pipeline.py` - Selection Pipeline Coordinator.
   - Coordinates sentence splitting, tokenization, and strategy invocation.
   - Exposes `select_tokens(...)` as a stable integration boundary.

4. `completetofelwords/selection_strategy.py` - Selection Strategy Engine.
   - Defines strategy protocol (`SelectionStrategy`).
   - Implements `DefaultSelectionStrategy`.
   - Applies candidate constraints and staged fallback sequence.
   - Current policy: uniform sampling among candidates within stage.

5. `completetofelwords/sentence_splitter.py` - Sentence Boundary Detector.
   - Splits raw text by `. ! ?` and preserves character spans.

6. `completetofelwords/tokenizer.py` - Token Extraction and Span Mapper.
   - Extracts lexical tokens and maps each token to sentence and text offsets.

7. `completetofelwords/lemmatizer.py` - Lexeme Normalization Service.
   - Normalizes word forms for duplicate-lemma constraints.
   - Current implementation uses `PorterStemmer` fallback behavior.

8. `completetofelwords/blank_renderer.py` - Cloze Rendering Engine.
   - Converts selected tokens into placeholders.
   - Preserves positional replacement correctness via reverse-offset rendering.

9. `completetofelwords/io_utils.py` - I/O and Configuration Utilities.
   - Reads input/corpus files.
   - Parses key-value `config.txt`.
   - Resolves output paths and writes result files.

10. `completetofelwords/frequency_ranker.py` - Frequency Utility Module.
   - Provides word frequency helpers.
   - Used by current default strategy to lock 3 high-frequency selections first.

## 3. Data Contracts
1. `Token` (`tokenizer.py`)
   - Raw token with normalized text, sentence index, and character span.

2. `SelectedToken` (`selection_strategy.py`)
   - Strategy-selected token enriched with normalized lemma.

3. `PipelineResult` (`pipeline.py`)
   - Final selected tokens plus warning messages.

## 4. Extension Points
1. Custom selection strategy
   - Implement `SelectionStrategy.select(...)`.
   - Inject via `select_tokens(..., strategy=...)`.

2. Advanced NLP upgrades
   - Replace/extend sentence splitter, tokenizer, or lemmatizer while preserving contracts.

3. Difficulty policies
   - Add new strategy classes (e.g., tiered frequency buckets) without modifying pipeline coordinator.

## 5. Runtime Output Rules
1. Output names include date suffix `YYYYMMDD` for `input/blanks/answers`.
2. If output prefix starts with `_`, leading underscores are removed.
3. `input` and `blanks` content are wrapped at 80 columns for readability.
4. Blank render prefix ratio is `[0.2, 0.6]`.

## 6. Test Surface
1. `tests/test_pipeline.py` - Pipeline rule behavior and fallback warnings.
2. `tests/test_selection_strategy.py` - Strategy injection and frequency-priority behavior.
3. `tests/test_config_fallback.py` - Config fallback and override precedence.
4. `tests/test_cli_paths.py` - Output path naming and wrap behavior.
5. `tests/test_blank_renderer.py` - Prefix ratio bounds.
