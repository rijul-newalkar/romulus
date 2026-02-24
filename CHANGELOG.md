# Changelog

All notable changes to Romulus will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-23

### Added

**Phase 1: Proof of Life** — the complete foundation.

#### Core Systems
- **Chronicle** — SQLite-backed memory with episodic traces, semantic rules, and agent identity
- **Vigil** — Two-layer immune system: innate regex patterns (<5ms) + adaptive memory cells
- **Dream Engine** — Nightly cycle: episode replay, rule extraction, memory pruning
- **Arena** — Composite fitness scoring (success rate, calibration, latency, safety)
- **Agent Core** — LLM-driven task handling with tool execution and Vigil gating

#### Infrastructure
- Async Ollama LLM client via httpx (swappable to any OpenAI-compatible API)
- Pydantic data models for all subsystems
- YAML configuration with sensible defaults
- Platform auto-detection (macOS / Raspberry Pi)
- APScheduler for cron-based dream cycles

#### Interface
- Interactive REPL with commands: ask, dream, status, rules, fitness
- FastAPI REST API (8 endpoints)
- **Wolf Den** — Animated dashboard with isometric room, CSS wolf character, live stats

#### Testing
- 208 unit tests across 6 test files
- 5 integration tests (requires Ollama)
- Proof of Life criteria validation suite

#### Security
- Innate threat detection: 15 destructive patterns, 6 scope violations
- Loop detection (>10 identical actions in 60s)
- Rate limiting (30 actions/minute)
- Safe math evaluation (AST-parsed, no eval/exec)
- >95% catch rate on attack vector test suite
