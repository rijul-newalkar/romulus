# Contributing to Romulus

Thanks for your interest in Romulus. This guide covers how to contribute.

## Getting Started

```bash
git clone https://github.com/rijul-newalkar/romulus.git
cd romulus
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

You'll also need [Ollama](https://ollama.com) running with a model pulled:

```bash
ollama pull qwen2.5:1.5b
```

## Development Workflow

1. **Fork and branch** from `master`
2. **Write code** — follow existing patterns
3. **Write tests** — every feature needs tests
4. **Run the suite** — `pytest tests/ -v -k "not integration"`
5. **Lint** — `ruff check romulus/ tests/`
6. **Open a PR** with a clear description

## Code Style

- **Ruff** for linting and formatting (config in `pyproject.toml`)
- Line length: 120 characters
- Target: Python 3.12
- Type hints on all function signatures
- Pydantic models for all data structures
- Async/await throughout — no blocking I/O in the event loop

## Architecture Rules

These are non-negotiable:

1. **No external frameworks** — Romulus IS the framework. No LangChain, no LlamaIndex, no agent SDKs. Raw LLM calls via httpx.

2. **Local only** — No cloud APIs, no telemetry, no external data transmission. Everything runs on the user's machine.

3. **Vigil gates everything** — Every action the agent proposes must pass through the Vigil before execution. No shortcuts, no bypasses.

4. **Chronicle logs everything** — Every task, result, and incident gets logged. The Dream Engine depends on complete records.

5. **Security by default** — Secrets in OS keychain (never plaintext). Innate rules block known threats. Adaptive layer learns from incidents.

## What to Work On

### Good First Issues

- Add new innate rules to `vigil/innate_rules.yaml` for emerging threat patterns
- Add new tools in `agent/tools.py` (file listing, weather, etc.)
- Improve LLM JSON parsing robustness in `agent/core.py`
- Add more test cases to `tests/test_vigil.py`

### Phase 2 Features

- ChromaDB vector search integration for semantic memory
- Counterfactual dream simulation
- Confidence recalibration in dreams
- Adversarial self-testing during dream cycles

### Phase 3 Features

- Telegram bot interface
- Email triage via IMAP/SMTP
- CalDAV calendar integration
- Raspberry Pi deployment scripts

## Testing

```bash
# Unit tests only (no Ollama needed)
pytest tests/ -v -k "not integration"

# Integration tests (Ollama must be running)
pytest tests/ -v -m integration

# With coverage
pytest tests/ --cov=romulus --cov-report=term-missing
```

All PRs must pass the existing test suite. New features must include tests.

## Project Structure

```
romulus/
├── models/      # Pydantic data models (shared language)
├── llm/         # Ollama client + prompt templates
├── chronicle/   # Memory system (SQLite)
├── vigil/       # Immune system (threat detection)
├── arena/       # Fitness monitoring
├── agent/       # Core reasoning loop + tools
├── dream/       # Nightly learning cycle
└── tests/       # 208+ tests
```

## Commit Messages

- Use present tense: "Add feature" not "Added feature"
- First line under 72 characters
- Reference issues: "Fix #12: handle empty LLM responses"

## Questions?

Open an issue or start a discussion. We don't bite — we were raised by wolves.
