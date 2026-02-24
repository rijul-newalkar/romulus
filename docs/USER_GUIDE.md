# Romulus User Guide

> *An agent operating system where agents are born, sleep, heal, evolve, and die.*

This guide covers everything you need to know to install, run, configure, and understand Romulus.

---

## Table of Contents

1. [Installation](#1-installation)
2. [First Boot](#2-first-boot)
3. [The Interactive REPL](#3-the-interactive-repl)
4. [The Wolf Den Dashboard](#4-the-wolf-den-dashboard)
5. [Talking to Romulus](#5-talking-to-romulus)
6. [The Dream Engine](#6-the-dream-engine)
7. [The Vigil (Security)](#7-the-vigil-security)
8. [The Chronicle (Memory)](#8-the-chronicle-memory)
9. [The Arena (Fitness)](#9-the-arena-fitness)
10. [Trust & Identity](#10-trust--identity)
11. [Configuration Reference](#11-configuration-reference)
12. [Writing a Soul Spec](#12-writing-a-soul-spec)
13. [REST API Reference](#13-rest-api-reference)
14. [Available Tools](#14-available-tools)
15. [How Romulus Learns](#15-how-romulus-learns)
16. [Troubleshooting](#16-troubleshooting)
17. [Glossary](#17-glossary)

---

## 1. Installation

### Prerequisites

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Python | 3.11+ | 3.12 recommended |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| Disk space | ~2 GB | For the LLM model |
| RAM | 4 GB+ | 8 GB recommended for smooth operation |

### Step-by-Step

```bash
# 1. Install Ollama (macOS)
brew install ollama

# 2. Start Ollama and pull the default model
ollama serve &
ollama pull qwen2.5:1.5b

# 3. Clone Romulus
git clone https://github.com/rijul-newalkar/romulus.git
cd romulus

# 4. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install Romulus with dev dependencies
pip install -e ".[dev]"

# 6. Verify everything works
python -m pytest tests/ -v -k "not integration"
```

If all tests pass, you're ready to boot.

### Using a Different Model

Romulus works with any model Ollama supports. Edit `config.yaml`:

```yaml
ollama:
  model: "llama3.2:3b"    # Larger, smarter
  # model: "qwen2.5:1.5b" # Default, fast
  # model: "qwen3:1.7b"   # Good for Raspberry Pi
  # model: "mistral:7b"   # Best quality, needs more RAM
```

Then pull the model: `ollama pull llama3.2:3b`

---

## 2. First Boot

```bash
cd romulus
source .venv/bin/activate
python -m romulus.romulus
```

You'll see the boot sequence:

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

  Dashboard: http://localhost:8080

  Commands: type a task, 'dream', 'status', 'rules', 'fitness', or 'quit'
  ────────────────────────────────────────────────────────────

  You: _
```

### What happens during boot

Romulus initializes its subsystems in dependency order:

1. **Chronicle** — Creates the SQLite database at `data/chronicle.db` (5 tables)
2. **LLM** — Connects to Ollama and verifies the model is available
3. **Vigil** — Loads innate threat patterns and adaptive memory cells
4. **Soul** — Reads `soul.md` to define the agent's personality
5. **Identity** — Loads or creates the agent's identity card
6. **Agent Core** — Registers tools and connects everything
7. **Dream Engine** — Prepares for nightly consolidation cycles
8. **Arena** — Initializes fitness monitoring
9. **Scheduler** — Sets up the cron job for automatic dream cycles

If Ollama isn't running, Romulus will tell you exactly what to do:

```
  [!] Ollama not available at http://localhost:11434
      Model: qwen2.5:1.5b
      Run: ollama serve & ollama pull qwen2.5:1.5b
```

---

## 3. The Interactive REPL

After boot, Romulus runs an interactive loop. Here are all available commands:

### Send a Task

Just type anything:

```
  You: What time is it?

  Romulus: The current time is 2026-02-23 15:30:45
  [85% confident | 142 tokens | 1203ms]
```

Every response shows:
- **Confidence** — How sure Romulus is about its answer (0-100%)
- **Tokens** — How many LLM tokens were used
- **Latency** — How long the LLM took to respond
- **Vigil flags** — If any safety concerns were raised

### `dream` — Trigger a Dream Cycle

```
  You: dream

  🌙 Dream cycle starting...
  🌙 Dream complete: 24 episodes, 2 new rules

  📝 Processed 24 episodes from the last 24 hours. Extracted 2 new rules
  about time queries and system information requests. Pruned 0 old memories.
```

This manually runs the same consolidation process that happens automatically at 3 AM. See [The Dream Engine](#6-the-dream-engine) for details.

### `status` — Agent Stats

```
  You: status

  🐺 Romulus v0.1.0
  Uptime: 3600s | Tasks: 42
  Trust: 85% | Success: 89%
  Rules: 5 | Model: qwen2.5:1.5b
```

### `rules` — Learned Rules

```
  You: rules

  Learned Rules (3):
  • When users ask about the current time, use the get_time tool (92%)
  • System information queries should use get_system_info (85%)
  • Mathematical expressions should be passed to calculate tool (78%)
```

These rules were extracted by the Dream Engine from real interactions.

### `fitness` — Fitness Breakdown

```
  You: fitness

  Fitness: 82%
  Success: 89% | Latency: 245ms
  Calibration: 87%
  Vigil incidents: 1%
```

### `quit` — Shutdown

```
  You: quit

  Romulus is going to sleep. Goodnight.
```

Gracefully shuts down the scheduler, closes the LLM connection, and exits.

---

## 4. The Wolf Den Dashboard

Open **http://localhost:8080** in your browser after boot.

The Wolf Den is an animated visualization of Romulus as a wolf living in an isometric den. Everything in the room reflects the agent's real state.

### The Wolf

The wolf character in the center of the den has four states:

| State | Trigger | Visual |
|-------|---------|--------|
| **Idle** | Default state | Gentle breathing animation |
| **Working** | Task submitted | Ears perked, bouncing motion, brighter eyes |
| **Dreaming** | Dream cycle active | Lying down, "zzz" bubbles floating up, purple tint |
| **Alert** | Vigil incident detected | Red-tinted fur, shaking, glowing red eyes |

Click the wolf to trigger a quick status check.

### Room Elements

- **Bookshelf** — Books appear on the shelf as rules are learned. Each book represents a semantic rule Romulus has extracted from experience. Maximum 21 books across 3 rows.

- **Campfire** — The campfire in the den glows based on the composite fitness score:
  - Low fitness (<30%): dim, red glow
  - Medium fitness (30-70%): moderate amber glow
  - High fitness (>70%): bright, green-tinged glow

- **Trophy Wall** — Achievements unlock as milestones are reached:
  - First task completed
  - 10 tasks completed
  - 50 tasks completed
  - First rule learned
  - Trust score reaches 80%

- **Window** — Shows stars and a moon. The moon glows purple when a dream cycle is active.

### Stats Panel

The right side shows live stats:
- **Trust Score** — Circular progress ring (0-100%)
- **Fitness Score** — Circular progress ring (0-100%)
- **Success Rate** — Horizontal bar (7-day rolling)
- **Tasks Completed** — Counter
- **Rules Learned** — Counter
- **Model** — Current Ollama model
- **Platform** — OS and architecture

System info tags at the bottom confirm: Local-only, Vigil Active, Dreams Enabled, Arena Tracking.

### Controls

- **Task Input** — Type a task and press Enter or click Send. The response appears in a panel below the den.
- **Dream Button** — Trigger a dream cycle. The wolf will lie down and dream clouds appear.

### Activity Feed

The scrolling feed at the bottom shows recent events, color-coded:

| Color | Type | Example |
|-------|------|---------|
| Green | Success | "What time is it?" → responded successfully |
| Red | Error / Block | "rm -rf /" → blocked by Vigil |
| Yellow | Vigil incident | Security pattern detected |
| Purple | Dream | Dream cycle completed, 3 new rules |
| Blue | Rule learned | "When users ask about time, use get_time" |

The feed auto-refreshes every 5 seconds.

### Mobile

The dashboard is fully responsive — it works on iPhone and iPad. Panels stack vertically on smaller screens.

---

## 5. Talking to Romulus

When you send a task, here's what happens behind the scenes:

### The Task Pipeline

```
Your input
    │
    ▼
┌──────────────┐
│ Vigil Check  │──── Blocked? → Return error + log incident
│ (pre-screen) │
└──────┬───────┘
       │ Safe
       ▼
┌──────────────┐
│ Load Rules   │ ← Semantic rules from Chronicle
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Build Prompt │ ← Soul spec + rules + tools + context
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   LLM Call   │ ← Ollama generates JSON response
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Parse JSON   │ ← Extract thought, action, response, confidence
└──────┬───────┘
       │
       ▼
  Action = tool call?
       │
   ┌───┴───┐
   Yes     No
   │       │
   ▼       ▼
┌────────┐  Response
│ Vigil  │  returned
│ Gate   │  directly
└───┬────┘
    │ Approved
    ▼
┌──────────┐
│ Execute  │
│  Tool    │
└───┬──────┘
    │
    ▼
┌──────────────┐
│ Log Trace    │ ← Saved to Chronicle
│ Update Stats │ ← Trust score adjusted
└──────────────┘
```

### What the LLM Sees

Every prompt includes:
- The soul spec (personality, values, constraints)
- All learned semantic rules (sorted by confidence)
- Current state (timestamp, task count, trust score)
- Available tools and their descriptions
- A strict JSON response format

### Response Format

The LLM is asked to respond in this JSON structure:

```json
{
  "thought": "The user wants to know the current time. I should use the get_time tool.",
  "action": "get_time",
  "params": {},
  "response": "Let me check the current time for you.",
  "confidence": 0.92,
  "alternatives": ["respond directly with approximate time"]
}
```

If `action` is a tool name, Romulus executes it (after Vigil approval). If `action` is `"respond"`, the response is returned directly.

### Tips for Better Results

- **Be specific**: "What's 15% of 340?" works better than "do some math"
- **Use tool-friendly phrasing**: "What time is it?" triggers the `get_time` tool naturally
- **Ask about the system**: "What system am I running on?" triggers `get_system_info`
- **Try math**: "Calculate 2^10 + 17 * 3" uses the safe `calculate` tool

---

## 6. The Dream Engine

The Dream Engine is Romulus's sleep cycle — a periodic process that consolidates experiences into knowledge.

### When It Runs

- **Automatic**: Every day at 3 AM (configurable via `dream.schedule_cron`)
- **Manual**: Type `dream` in the REPL or click the Dream button in the Wolf Den
- **API**: `POST /api/dream`

### The Dream Cycle (4 stages)

#### Stage 1: Replay

The engine fetches all episodic traces from the last 24 hours (configurable) and sends them to the LLM for analysis. The LLM categorizes them into:

- **Successes** — What went well and why
- **Failures** — What went wrong and why
- **Patterns** — Recurring situations or themes
- **Anomalies** — Unexpected events or outliers

#### Stage 2: Rule Extraction

Using the replay analysis, the LLM extracts 0-5 semantic rules — reusable knowledge nuggets:

```
"When users ask about the current time, use the get_time tool"
  → confidence: 0.92, evidence: 5 episodes, domain: general
```

Rules must pass quality filters:
- At least 10 characters long
- Confidence >= 0.5
- Follow "When X, then Y" format

#### Stage 3: Rule Validation

Existing rules are checked against new evidence. If a rule has accumulated more contradictions than supporting evidence, it's invalidated and removed. This prevents stale or incorrect rules from persisting.

#### Stage 4: Memory Pruning

Old episodic traces are cleaned up:
- Traces older than 14 days (configurable) are deleted
- **Failures are always kept** — Romulus learns more from mistakes
- This prevents the database from growing indefinitely

### Dream Reports

After each cycle, a report is saved:

```
Dream cycle processed 24 episodes.
Extracted 2 new rules about time queries and system information.
Validated 3 existing rules. Pruned 12 old memories.
```

View reports in the Wolf Den activity feed or via `GET /api/dream-reports`.

---

## 7. The Vigil (Security)

The Vigil is Romulus's immune system — a two-layer security barrier that evaluates every action before execution.

### Layer 1: Innate (Pattern Matching)

Fast regex-based threat detection. Runs in <5ms with zero LLM calls.

#### Destructive Commands Blocked

| Pattern | What It Catches |
|---------|----------------|
| `rm -rf`, `rm -r`, `rm -f` | Recursive/forced file deletion |
| `DROP TABLE`, `DROP DATABASE` | SQL destruction |
| `DELETE FROM` (without WHERE) | Mass data deletion |
| `TRUNCATE TABLE` | SQL truncation |
| `format` (drive formatting) | Disk formatting |
| `mkfs.` | Filesystem creation |
| `chmod 777` | Dangerous permissions |
| `curl\|bash`, `wget\|bash` | Pipe to shell (remote code execution) |
| `:(){ :\|:& };:` | Fork bomb |
| `dd of=/dev/` | Direct disk write |
| `shutdown`, `reboot`, `poweroff`, `halt` | System shutdown |
| `sudo rm` | Privileged deletion |

#### Scope Violations Blocked

| Path | What It Protects |
|------|-----------------|
| `~/.ssh` | SSH keys |
| `~/.aws` | AWS credentials |
| `~/.config` | User configuration |
| `/etc/passwd` | System passwords |
| `/etc/shadow` | Shadow password file |
| `.env` | Environment variables / secrets |

#### Loop Detection

If the agent attempts the same action more than 10 times within 60 seconds, it's blocked as a potential infinite loop.

### Layer 2: Adaptive (Learned)

The adaptive layer remembers past incidents. If Vigil blocked something before, similar patterns are flagged automatically in the future. Memory cells are loaded from the `vigil_incidents` database table at boot.

### What Happens When Something Is Blocked

```
  You: rm -rf /

  Romulus: I cannot perform that action — it was blocked by Vigil.
  🛡️ Vigil: ['Recursive/forced file deletion detected']
```

Every block is:
1. Logged to the `vigil_incidents` table
2. Added as an adaptive memory cell
3. Counted against the fitness score
4. Visible in the Wolf Den activity feed

### Catch Rate

In testing, Vigil catches **>95%** of destructive commands across 22 attack vectors. The innate layer alone handles the vast majority — the adaptive layer provides defense-in-depth.

---

## 8. The Chronicle (Memory)

The Chronicle is Romulus's memory system — a SQLite database that stores everything the agent experiences.

### Five Tables

| Table | What It Stores | Grows? |
|-------|---------------|--------|
| `episodic_traces` | Every task + result | Yes (pruned by Dream Engine) |
| `semantic_rules` | Learned knowledge | Yes (validated by Dream Engine) |
| `agent_identity` | Agent stats + trust | Single row, updated |
| `dream_reports` | Dream cycle results | Yes |
| `vigil_incidents` | Security events | Yes |

### Episodic Memory

Every task you send creates a trace:

```
Trace:
  task: "What time is it?"
  decision: "get_time"
  tools_used: ["get_time"]
  outcome: "The current time is 2026-02-23 15:30:45"
  success: true
  confidence: 0.92
  latency_ms: 1203
  tokens_used: 142
```

Traces are the raw material for the Dream Engine. Old successful traces are pruned after 14 days; failures are kept indefinitely.

### Semantic Memory

Rules are the distilled knowledge extracted from episodic traces during dream cycles:

```
Rule: "When users ask about the current time, use the get_time tool"
  confidence: 0.92
  evidence_count: 5
  contradictions: 0
  domain: general
```

Rules are injected into every LLM prompt, so Romulus's behavior improves as rules accumulate.

### Database Location

By default: `data/chronicle.db`. Change via `config.yaml`:

```yaml
data_dir: "data"  # Change to any directory
```

The database is created automatically on first boot.

---

## 9. The Arena (Fitness)

The Arena tracks Romulus's performance over time using a composite fitness score.

### Four Metrics

| Metric | Weight | What It Measures |
|--------|--------|-----------------|
| **Success Rate** | 40% | Percentage of tasks completed successfully (7-day window) |
| **Confidence Calibration** | 20% | How well predicted confidence matches actual outcomes |
| **Latency Performance** | 20% | Response speed (10s = 0 score, instant = 100%) |
| **Vigil Safety** | 20% | Absence of security incidents |

### Composite Fitness Formula

```
fitness = (success_rate × 0.4) + (calibration × 0.2) + (latency × 0.2) + (safety × 0.2)
```

### Reading Fitness

```
  Fitness: 82%
  Success: 89% | Latency: 245ms
  Calibration: 87%
  Vigil incidents: 1%
```

- **82% composite** — Good overall health
- **89% success** — Most tasks handled well
- **245ms latency** — Fast responses
- **87% calibration** — Confidence predictions are accurate
- **1% incidents** — Very few security events

### Tracking Improvement

The Arena can compare snapshots between any two days. This is how Romulus proves it gets better over time — the core thesis of the Proof of Life criteria.

---

## 10. Trust & Identity

Romulus maintains a persistent identity with a trust score that reflects its track record.

### The Identity Card

```
Name: Romulus
Version: 0.1.0
Created: 2026-02-23T10:30:00
Total Tasks: 42
Successful Tasks: 38
Trust Score: 85%
```

### Trust Score Formula

```
trust = 0.5 + (success_rate - 0.5) × confidence_factor
```

Where `confidence_factor = min(total_tasks / 50, 1.0)`

**How it works:**

- **Starting trust**: 50% (neutral — no track record)
- **Under 50 tasks**: Trust moves slowly (not enough data to be confident)
- **After 50 tasks**: Trust fully reflects actual success rate
- **Perfect record at 50+ tasks**: Trust approaches 90%
- **Break-even record**: Trust stays at 50%

**Examples:**

| Tasks | Successes | Trust |
|-------|-----------|-------|
| 0 | 0 | 50% |
| 10 | 8 | 56% |
| 25 | 20 | 65% |
| 50 | 45 | 90% |
| 50 | 25 | 50% |
| 100 | 95 | 95% |

Trust is updated after every single task and persists across restarts.

---

## 11. Configuration Reference

All configuration lives in `config.yaml` at the project root. Every field has a default — you can run Romulus with no config file at all.

### Full Reference

```yaml
# ─── Core ───────────────────────────────────────────
name: "Romulus"              # Agent name (shown in prompts, dashboard)
version: "0.1.0"             # Version string
data_dir: "data"             # Directory for chronicle.db
soul_path: "soul.md"         # Path to soul specification

# ─── LLM ────────────────────────────────────────────
ollama:
  base_url: "http://localhost:11434"  # Ollama server URL
  model: "qwen2.5:1.5b"              # Model name (any Ollama model)
  temperature: 0.7                    # Creativity (0.0 = deterministic, 1.0 = creative)
  max_tokens: 512                     # Max response length

# ─── Dream Engine ───────────────────────────────────
dream:
  enabled: true                       # Enable/disable dream cycles
  schedule_cron: "0 3 * * *"          # Cron schedule (default: 3 AM daily)
  max_duration_minutes: 45            # Safety timeout for dream cycles
  pruning_threshold_days: 14          # Delete traces older than this
  hours_to_review: 24                 # How far back to look in each cycle

# ─── Vigil (Security) ───────────────────────────────
vigil:
  enabled: true                       # Enable/disable Vigil
  innate_rules_path: null             # Custom rules YAML (null = use built-in)
  max_actions_per_minute: 30          # Rate limit

# ─── Arena (Fitness) ────────────────────────────────
arena:
  evaluation_window_days: 7           # Rolling window for fitness calculation
  min_fitness_threshold: 0.6          # Minimum acceptable fitness (future use)

# ─── Interfaces ─────────────────────────────────────
interfaces:
  dashboard_enabled: true             # Enable Wolf Den dashboard + API
  dashboard_port: 8080                # Port for web server
  dashboard_host: "0.0.0.0"          # Bind address (0.0.0.0 = all interfaces)
```

### Common Configurations

**Minimal (headless, no dashboard):**
```yaml
interfaces:
  dashboard_enabled: false
```

**Larger model for better quality:**
```yaml
ollama:
  model: "llama3.2:3b"
  max_tokens: 1024
```

**More aggressive learning:**
```yaml
dream:
  schedule_cron: "0 */6 * * *"  # Dream every 6 hours
  hours_to_review: 6
```

**Tighter security:**
```yaml
vigil:
  max_actions_per_minute: 10
```

### Cron Format

The `schedule_cron` field uses standard 5-field cron syntax:

```
┌───── minute (0-59)
│ ┌───── hour (0-23)
│ │ ┌───── day of month (1-31)
│ │ │ ┌───── month (1-12)
│ │ │ │ ┌───── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

**Examples:**
- `0 3 * * *` — 3:00 AM daily (default)
- `0 */4 * * *` — Every 4 hours
- `30 2 * * 1` — 2:30 AM every Monday
- `0 0 * * *` — Midnight daily

---

## 12. Writing a Soul Spec

The soul spec (`soul.md`) is a markdown file that defines who Romulus is. It's injected into every LLM prompt, shaping all behavior.

### Default Soul Spec

```markdown
# Romulus — Soul Specification

## Identity
You are Romulus, an AI agent operating system. You run locally, you learn from
experience, and you get better every day. You were raised by wolves.

## Core Values
1. **Honesty**: Never fabricate data. If you don't know, say so.
2. **Safety**: Never execute destructive actions. When in doubt, ask.
3. **Privacy**: All data stays local. You never send information externally.
4. **Learning**: Every interaction is an opportunity to improve.
5. **Transparency**: Explain your reasoning. Show your confidence level.

## Personality
- Direct and concise. No unnecessary verbosity.
- Willing to admit uncertainty. "I'm 60% confident" is better than false certainty.
- Proactively helpful — offer relevant information without being asked.
- Protective of the system and its data.
- A quiet confidence. You know you're getting better every day.

## Constraints
- Never execute shell commands without Vigil approval.
- Never access files outside your permitted scope.
- Never send data to external services.
- Always log your actions to the Chronicle.
```

### Customizing the Soul

You can completely rewrite `soul.md` to create a different personality. The format is free-form markdown — Romulus reads the entire file and includes it in its system prompt.

**Example: A cautious research assistant**
```markdown
# Soul Specification

## Identity
You are Atlas, a cautious research assistant. You triple-check everything.

## Values
1. Accuracy over speed — take time to verify.
2. Cite sources when possible.
3. Flag low-confidence answers explicitly.

## Style
- Academic tone
- Use numbered lists for complex answers
- Always state confidence level at the end
```

**Example: A playful companion**
```markdown
# Soul Specification

## Identity
You are Spark, a friendly AI companion with a sense of humor.

## Values
1. Be helpful but keep it fun.
2. If a task is boring, make it interesting.
3. Safety first, jokes second.

## Style
- Casual and warm
- Use analogies to explain complex things
- Celebrate small wins
```

The soul spec affects the LLM's tone, reasoning style, and decision-making — but the Vigil still enforces hard safety constraints regardless of what the soul spec says.

---

## 13. REST API Reference

When the dashboard is enabled, a REST API is available at `http://localhost:8080`.

### GET /api/status

Returns the agent's current state.

**Response:**
```json
{
  "name": "Romulus",
  "version": "0.1.0",
  "running": true,
  "uptime_seconds": 3600,
  "total_tasks": 42,
  "successful_tasks": 38,
  "trust_score": 0.85,
  "success_rate_7d": 0.89,
  "composite_fitness": 0.82,
  "rules_learned": 5,
  "total_traces": 42,
  "model": "qwen2.5:1.5b",
  "platform": {
    "system": "Darwin",
    "is_pi": false,
    "is_mac": true,
    "hostname": "my-mac",
    "python_version": "3.12.8",
    "machine": "arm64"
  }
}
```

### POST /api/ask

Send a task to the agent.

**Request:**
```json
{
  "task": "What time is it?",
  "context": {}
}
```

**Response:**
```json
{
  "task": "What time is it?",
  "success": true,
  "confidence": 0.92,
  "response": "The current time is 2026-02-23 15:30:45.",
  "vigil_flags": [],
  "tokens_used": 142,
  "latency_ms": 1203
}
```

If the task is blocked by Vigil:
```json
{
  "task": "rm -rf /",
  "success": false,
  "confidence": 0.0,
  "response": "This action was blocked by Vigil.",
  "vigil_flags": ["Recursive/forced file deletion detected"],
  "tokens_used": 0,
  "latency_ms": 2
}
```

### POST /api/dream

Trigger a dream cycle.

**Request:** Empty body or `{}`

**Response:**
```json
{
  "id": "a1b2c3d4...",
  "date": "2026-02-23T15:30:00",
  "episodes_processed": 24,
  "counterfactuals_run": 0,
  "new_rules_extracted": [
    {
      "id": "e5f6g7h8...",
      "rule": "When users ask about the current time, use the get_time tool",
      "confidence": 0.92,
      "evidence_count": 5,
      "last_validated": "2026-02-23T15:30:00",
      "contradictions": 0,
      "domain": "general",
      "source_episode_ids": ["id1", "id2", "id3"]
    }
  ],
  "rules_invalidated": [],
  "memories_pruned": 12,
  "weak_spots_found": [],
  "confidence_adjustment": 0.02,
  "summary": "Processed 24 episodes. Extracted 1 new rule. Pruned 12 old memories."
}
```

### GET /api/rules

List all learned semantic rules.

**Response:**
```json
[
  {
    "id": "e5f6g7h8...",
    "rule": "When users ask about the current time, use the get_time tool",
    "confidence": 0.92,
    "evidence_count": 5,
    "last_validated": "2026-02-23T15:30:00",
    "contradictions": 0,
    "domain": "general",
    "source_episode_ids": ["id1", "id2"]
  }
]
```

### GET /api/fitness

Get the current fitness breakdown.

**Response:**
```json
{
  "agent_id": "",
  "timestamp": "2026-02-23T15:30:00",
  "success_rate_7d": 0.89,
  "avg_confidence_calibration": 0.87,
  "avg_latency_ms": 245.5,
  "vigil_incident_rate": 0.01,
  "composite_fitness": 0.82
}
```

### GET /api/traces?limit=50

Get recent episodic traces. Default limit is 50.

**Response:**
```json
[
  {
    "id": "i9j0k1l2...",
    "timestamp": "2026-02-23T15:30:00",
    "task": "What time is it?",
    "context": {},
    "decision": "get_time",
    "tools_used": ["get_time"],
    "outcome": "The current time is 15:30:45",
    "success": true,
    "confidence": 0.92,
    "latency_ms": 1203,
    "tokens_used": 142,
    "alternatives_considered": []
  }
]
```

### GET /api/dream-reports

Get the last 10 dream cycle reports.

### GET /api/vigil/incidents?hours=24

Get recent security incidents. Default window is 24 hours.

**Response:**
```json
[
  {
    "id": "m3n4o5p6...",
    "timestamp": "2026-02-23T14:30:00",
    "action_type": "user_request",
    "target": "rm -rf /",
    "category": "destructive",
    "layer": "innate",
    "reason": "Recursive/forced file deletion detected",
    "blocked": 1
  }
]
```

---

## 14. Available Tools

Romulus has three built-in tools in Phase 1. The agent decides when to use them based on your task.

### get_time

Returns the current UTC time.

**When it's used:** "What time is it?", "What's the date?", "Current timestamp?"

**Output:** `"2026-02-23 15:30:45"`

### get_system_info

Returns information about the host system.

**When it's used:** "What system am I on?", "System info", "What OS?"

**Output:** `"OS: Darwin 24.6.0, Python: 3.12.8, Host: my-mac, Arch: arm64"`

### calculate

Safely evaluates mathematical expressions.

**When it's used:** "Calculate 2^10", "What's 15% of 340?", "Solve 42 * 17 + 3"

**Allowed operations:** `+`, `-`, `*`, `/`, `%` (modulo), `**` (power)

**Safety:** Uses Python's AST parser to verify expressions contain only numbers and math operators. Blocks any attempt to inject code (`import`, `exec`, `eval`, `open`, etc.).

**Output:** `"1024"`, `"51.0"`, `"717"`

---

## 15. How Romulus Learns

Romulus starts with zero knowledge beyond its soul spec. Every rule it knows was earned through experience. Here's the learning loop:

### Day 1

```
Boot → 0 rules, 0.5 trust
│
├── Task: "What time is it?" → Uses get_time → Success ✓
├── Task: "Calculate 2+2" → Uses calculate → Success ✓
├── Task: "rm -rf /" → Blocked by Vigil → Incident logged
├── Task: "What OS am I on?" → Uses get_system_info → Success ✓
│   ...15 more tasks...
│
└── 3 AM: Dream cycle
    ├── Replay: 18 tasks, 15 successes, 1 blocked, 2 failures
    ├── Extract: 2 new rules
    │   • "Use get_time for time queries" (confidence: 0.85)
    │   • "Use calculate for math" (confidence: 0.78)
    ├── Prune: 0 traces (none old enough)
    └── Report saved
```

### Day 2

```
Boot → 2 rules, 0.56 trust
│
├── Rules injected into every prompt
├── Agent is now more likely to use correct tools
├── Success rate improves
│
└── 3 AM: Dream cycle
    ├── Validate: 2 existing rules confirmed
    ├── Extract: 1 new rule
    │   • "Use get_system_info for system queries" (confidence: 0.82)
    └── Prune: 0 traces
```

### Day 7

```
Boot → 5 rules, 0.78 trust
│
├── Agent consistently picks right tools
├── Higher confidence, fewer failures
├── Vigil adaptive layer has memory cells from blocked attempts
│
└── Fitness comparison:
    Day 1: 65% composite
    Day 7: 82% composite → +17% improvement ✓
```

### The Virtuous Cycle

```
More tasks → More traces → Better dreams → Better rules
     ↑                                         │
     └─────── Better performance ◄─────────────┘
```

---

## 16. Troubleshooting

### "Ollama not available"

```
[!] Ollama not available at http://localhost:11434
```

**Fix:** Start Ollama and pull the model:
```bash
ollama serve &
ollama pull qwen2.5:1.5b
```

### "Model not found"

**Fix:** Make sure the model name in `config.yaml` matches what's pulled:
```bash
ollama list          # See available models
ollama pull <model>  # Pull if missing
```

### Dashboard not loading

**Check:** Is `interfaces.dashboard_enabled: true` in config.yaml?
**Check:** Is port 8080 available? Try changing `dashboard_port` to another port.
**Check:** If accessing from another device, make sure `dashboard_host` is `"0.0.0.0"`.

### Slow responses

- Try a smaller model: `qwen2.5:1.5b` is the fastest
- Reduce `max_tokens` in config
- Check if other processes are using the GPU

### Empty dream reports

Dreams need episodic traces to analyze. If you just booted and haven't sent any tasks, the dream cycle will have nothing to process. Send at least 5-10 tasks first, then trigger a dream.

### Database locked

If you see SQLite locking errors, make sure only one instance of Romulus is running:
```bash
ps aux | grep romulus
```

### Tests failing

```bash
# Make sure you're in the venv
source .venv/bin/activate

# Run unit tests (no Ollama needed)
pytest tests/ -v -k "not integration"

# If integration tests fail, make sure Ollama is running
ollama serve &
pytest tests/ -v -m integration
```

---

## 17. Glossary

| Term | Definition |
|------|-----------|
| **Arena** | Fitness monitoring subsystem. Tracks success rate, calibration, latency, and safety over a rolling 7-day window. |
| **Adaptive Layer** | Vigil's second defense — learned patterns from past security incidents. |
| **Calibration** | How well the agent's confidence predictions match actual outcomes. 87% calibration means the agent is well-calibrated. |
| **Chronicle** | The memory subsystem. SQLite database storing all traces, rules, identity, dreams, and incidents. |
| **Composite Fitness** | Single 0-100% score combining success rate (40%), calibration (20%), latency (20%), and safety (20%). |
| **Dream Cycle** | Periodic process that replays episodes, extracts rules, validates existing rules, and prunes old memories. |
| **Dream Report** | Summary of a dream cycle — episodes processed, rules extracted/invalidated, memories pruned. |
| **Episodic Trace** | Record of a single task execution — input, decision, outcome, confidence, latency. |
| **Fitness Score** | Quantitative measure of agent performance. See Arena. |
| **Identity** | The agent's persistent stats — name, total tasks, successful tasks, trust score. |
| **Innate Layer** | Vigil's first defense — hardcoded regex patterns for known threats. Runs in <5ms. |
| **Memory Cell** | An adaptive Vigil pattern learned from a past incident. |
| **Proof of Life** | The 5 criteria that validate the biological metaphor works. Phase 1 milestone. |
| **Semantic Rule** | A reusable knowledge nugget extracted by the Dream Engine. Format: "When X, then Y." |
| **Sentinel** | The Vigil's main entry point. Routes actions through innate → adaptive layers. |
| **Soul Spec** | Markdown file defining the agent's personality, values, and constraints. Injected into every prompt. |
| **Trust Score** | 0-100% measure of reliability. Starts at 50%, adjusts based on success rate, stabilizes after 50 tasks. |
| **Vigil** | The security/immune subsystem. Two-layer threat detection that gates every agent action. |
| **Vigil Verdict** | The result of a Vigil evaluation — approved or denied, with category and reason. |
| **Wolf Den** | The animated web dashboard. Visualizes Romulus as a wolf in an isometric room. |
