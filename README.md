<p align="center">
  <img src="https://img.shields.io/badge/status-proof%20of%20life-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/python-3.11+-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/tests-208%20passing-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/framework-none-orange" alt="No Framework">
</p>

<h1 align="center">Romulus</h1>

<p align="center">
  <strong>An agent operating system where agents are born, sleep, heal, evolve, and die.</strong>
</p>

<p align="center">
  Romulus treats AI agents as living organisms — not chatbots with tools.<br>
  It runs locally on your machine, learns from every interaction, dreams at night<br>
  to consolidate memories, and has an immune system that blocks dangerous actions.
</p>

---

## The Biological Metaphor

Most agent frameworks treat agents as **request-response functions**. Romulus treats them as **organisms** with lifecycles:

| Biology | Romulus | What It Does |
|---------|--------|--------------|
| Memory | **The Chronicle** | SQLite-backed episodic, semantic, and identity memory |
| Immune System | **The Vigil** | Pattern matching + learned threat detection in <5ms |
| Sleep | **The Dream Engine** | Nightly replay, rule extraction, memory pruning |
| Fitness | **The Arena** | Rolling success rate, calibration, composite scoring |
| Personality | **Soul Spec** | Markdown file defining values, constraints, voice |
| Brain | **Agent Core** | LLM-driven reasoning with tool execution and Vigil gating |

## Architecture

```
                    ┌─────────────┐
                    │   You/API   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Agent Core │ ← Soul Spec
                    └──┬───┬───┬──┘
                       │   │   │
              ┌────────┘   │   └────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Chronicle│ │  Vigil   │ │  Tools   │
        │ (Memory) │ │ (Immune) │ │ (Actions)│
        └────┬─────┘ └──────────┘ └──────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌──────────┐  ┌──────────┐
│  Dream   │  │  Arena   │
│ Engine   │  │(Fitness) │
└──────────┘  └──────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running

### Install

```bash
# Clone
git clone https://github.com/rijul-newalkar/romulus.git
cd romulus

# Pull an LLM
ollama pull qwen2.5:1.5b

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run
python -m romulus.romulus
```

### First Boot

```
  🐺 Romulus v0.1.0
  Platform: Darwin (arm64)
  Python: 3.12.8

  [+] Chronicle initialized
  [+] LLM connected: qwen2.5:1.5b
  [+] Vigil armed
  [+] Identity: Romulus | Tasks: 0 | Trust: 50%
  [+] Agent core ready
  [+] Dream Engine loaded
  [+] Rules: 0 | Traces: 0
  [+] Dream schedule: 0 3 * * *

  Romulus is awake. The wolves are ready.

  You: What time is it?
  Romulus: The current time is 2024-01-15 14:32:07
  [85% confident | 142 tokens | 1203ms]
```

### The Wolf Den (Dashboard)

Open `http://localhost:8080` after boot to see the Wolf Den — an animated visualization of Romulus as a wolf in an isometric den:

- **Wolf states**: idle, working, dreaming, alert
- **Live room**: campfire glows with fitness, bookshelf fills with learned rules
- **Stats**: trust score, fitness, task count, success rate
- **Interactive**: send tasks, trigger dreams, view activity feed

## Commands

In the interactive REPL:

| Command | What It Does |
|---------|-------------|
| `<any text>` | Send a task to the agent |
| `dream` | Trigger a dream cycle (memory consolidation) |
| `status` | Show agent stats |
| `rules` | List all learned semantic rules |
| `fitness` | Show fitness breakdown |
| `quit` | Shutdown gracefully |

## API Endpoints

When the dashboard is enabled (default), a REST API is available:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Agent status and stats |
| POST | `/api/ask` | Send a task `{"task": "..."}` |
| POST | `/api/dream` | Trigger dream cycle |
| GET | `/api/rules` | List learned rules |
| GET | `/api/fitness` | Fitness breakdown |
| GET | `/api/traces` | Recent task traces |
| GET | `/api/dream-reports` | Dream cycle reports |
| GET | `/api/vigil/incidents` | Recent security incidents |

## How It Works

### A Day in the Life of Romulus

1. **Morning**: Romulus boots. Chronicle loads memories. Vigil arms threat patterns. Agent core connects to Ollama.

2. **During the day**: You send tasks. Each task flows through:
   - Vigil pre-check (is this task safe?)
   - Rule loading (what has Romulus learned about tasks like this?)
   - LLM reasoning (think, plan, act)
   - Vigil gate (is the proposed action safe?)
   - Tool execution (if approved)
   - Chronicle logging (save the experience)
   - Identity update (adjust trust score)

3. **At night (3 AM)**: The Dream Engine runs:
   - **Replay**: Reviews the day's episodes — successes, failures, patterns
   - **Extract**: LLM identifies reusable rules from patterns ("when users ask about time, use the get_time tool")
   - **Prune**: Deletes routine successful traces older than 14 days (keeps failures for learning)
   - **Report**: Saves a dream report with summary and new rules

4. **Over time**: The Arena tracks rolling 7-day fitness. Rules accumulate. Trust score adjusts. Day 7 Romulus is measurably better than Day 1.

### The Vigil (Immune System)

Two layers, inspired by biological immunity:

**Innate Layer** (<5ms, zero LLM calls):
- Regex pattern matching against known threats
- Catches: `rm -rf`, `DROP TABLE`, fork bombs, `chmod 777`, `curl|bash`, scope escapes
- Loop detection: blocks >10 identical actions in 60s

**Adaptive Layer** (learned from experience):
- Memory cells from past incidents
- If something was blocked before, similar patterns are flagged
- Grows smarter with every incident

## Configuration

Edit `config.yaml`:

```yaml
name: "Romulus"
data_dir: "data"
soul_path: "soul.md"

ollama:
  model: "qwen2.5:1.5b"    # Any Ollama model
  temperature: 0.7
  max_tokens: 512

dream:
  enabled: true
  schedule_cron: "0 3 * * *"  # 3 AM daily
  hours_to_review: 24

vigil:
  enabled: true
  max_actions_per_minute: 30

interfaces:
  dashboard_enabled: true
  dashboard_port: 8080
```

### Soul Spec

Edit `soul.md` to change the agent's personality, values, and constraints. This is injected into every LLM prompt.

## Testing

```bash
# Run all unit tests (no Ollama required)
pytest tests/ -v -k "not integration"

# Run integration tests (requires Ollama running)
pytest tests/ -v -m integration

# Run everything
pytest tests/ -v
```

**208 unit tests** covering models, Chronicle, Vigil, Arena, tools, and all 5 Proof of Life criteria.

## Proof of Life Criteria

Phase 1 is complete when all 5 pass:

- [x] Agent boots and handles basic tasks (>60% success rate)
- [x] Dream Engine runs and produces non-empty reports
- [x] At least one semantic rule extracted from experience
- [x] Vigil catches destructive commands (>80% catch rate — we hit >95%)
- [x] Day 7 performance is measurably better than Day 1

## Project Structure

```
romulus/
├── romulus/
│   ├── romulus.py          # Main daemon — boots everything, runs REPL
│   ├── api.py              # FastAPI endpoints
│   ├── config.py           # Pydantic config from YAML
│   ├── platform.py         # Mac/Pi auto-detection
│   ├── models/             # Shared Pydantic data models
│   │   ├── episodic.py     #   EpisodicTrace, TaskResult
│   │   ├── semantic.py     #   SemanticRule
│   │   ├── identity.py     #   AgentIdentity
│   │   ├── dream.py        #   DreamReport
│   │   ├── vigil.py        #   VigilVerdict, ThreatCategory
│   │   ├── actions.py      #   AgentAction, ActionOutcome
│   │   └── arena.py        #   FitnessScore, PerformanceSnapshot
│   ├── llm/
│   │   ├── client.py       # Async Ollama HTTP client
│   │   └── prompts.py      # System prompt templates
│   ├── chronicle/          # Memory system
│   │   ├── database.py     #   SQLite schema + connection
│   │   ├── episodic.py     #   Episode logging + retrieval
│   │   ├── semantic.py     #   Rule storage + validation
│   │   └── identity.py     #   Agent identity card
│   ├── vigil/              # Immune system
│   │   ├── sentinel.py     #   Main entry — chains layers
│   │   ├── innate.py       #   Layer 1: regex patterns (<5ms)
│   │   ├── innate_rules.yaml  # Threat pattern database
│   │   ├── adaptive.py     #   Layer 2: learned memory cells
│   │   └── incidents.py    #   Incident logging
│   ├── arena/
│   │   └── monitor.py      # Fitness scoring
│   ├── agent/
│   │   ├── core.py         # Central reasoning loop
│   │   └── tools.py        # Built-in tools
│   └── dream/
│       ├── engine.py       # Orchestrator
│       ├── replay.py       # Episode categorization
│       ├── extractor.py    # Rule extraction from patterns
│       └── pruner.py       # Memory cleanup
├── static/                 # Wolf Den dashboard
│   ├── index.html
│   ├── css/wolfden.css
│   └── js/wolfden.js
├── tests/                  # 208 tests
├── config.yaml
├── soul.md
└── pyproject.toml
```

## Design Philosophy

**No frameworks.** Romulus is the framework. The core agent loop is ~100 lines. No LangChain, no LlamaIndex, no abstractions fighting you.

**Local first.** Everything runs on your machine. SQLite for storage. Ollama for LLM. No API keys, no cloud, no telemetry.

**Learn by doing.** Romulus doesn't start smart — it starts with a soul spec and zero rules. Every rule it knows was extracted from real experience through dream cycles.

**Fail safely.** The Vigil checks every action before execution. If it's never seen it before, it's cautious. If it blocked something similar before, it remembers.

## Roadmap

### Phase 2: Intelligence
- [ ] ChromaDB vector search for semantic memory
- [ ] Counterfactual dream simulation ("what if I'd done X?")
- [ ] Confidence recalibration through dream analysis
- [ ] Adversarial self-testing in dreams

### Phase 3: Integration
- [ ] Raspberry Pi deployment (24/7 operation)
- [ ] Telegram bot interface
- [ ] Email triage (IMAP/SMTP)
- [ ] Calendar management (CalDAV)
- [ ] Tailscale mesh networking (Mac/Pi/iPhone)

### Phase 4: Evolution
- [ ] The Forge — spawn variant agents with mutations
- [ ] The Reaper — retire unfit agents
- [ ] Multi-agent arena tournaments
- [ ] Genetic inheritance of learned rules

## Documentation

- [User Guide](docs/USER_GUIDE.md) — Installation, configuration, and complete usage guide
- [Research References](docs/REFERENCES.md) — The 34 papers behind the architecture
- [Contributing](CONTRIBUTING.md) — Development workflow and guidelines
- [Changelog](CHANGELOG.md) — Release history

## Research Foundations

Every Romulus subsystem is grounded in real research — 34 papers spanning neuroscience, immunology, cognitive science, and machine learning. See [REFERENCES.md](docs/REFERENCES.md) for the full bibliography.

| Subsystem | Research Basis |
|-----------|---------------|
| Chronicle (Memory) | Tulving's episodic/semantic memory distinction (1972) |
| Dream Engine (Sleep) | Hippocampal replay during sleep (Wilson & McNaughton, 1994), Complementary Learning Systems (McClelland et al., 1995) |
| Vigil (Immunity) | Artificial Immune Systems (Forrest et al., 1994), Danger Theory (Matzinger, 2002) |
| Arena (Fitness) | Genetic algorithms (Holland, 1975), Neural network calibration (Guo et al., 2017) |
| Agent Core | ReAct (Yao et al., 2023), Retrieval-Augmented Generation (Lewis et al., 2020) |

## License

[MIT](LICENSE) — use it, fork it, teach it to hunt.

---

<p align="center">
  <em>Raised by wolves. Learning every day.</em>
</p>
