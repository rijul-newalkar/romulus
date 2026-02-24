import asyncio
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from romulus.agent.core import AgentCore
from romulus.agent.tools import calculate, get_system_info, get_time
from romulus.arena.monitor import FitnessMonitor
from romulus.chronicle.database import ChronicleDB
from romulus.chronicle.episodic import EpisodicStore
from romulus.chronicle.identity import IdentityStore
from romulus.chronicle.semantic import SemanticStore
from romulus.config import RomulusConfig
from romulus.dream.engine import DreamEngine
from romulus.llm.client import OllamaClient
from romulus.platform import detect_platform
from romulus.vigil.adaptive import AdaptiveLayer
from romulus.vigil.incidents import IncidentLogger
from romulus.vigil.innate import InnateLayer
from romulus.vigil.sentinel import Sentinel


class RomulusDaemon:
    def __init__(self, config: RomulusConfig):
        self.config = config
        self.running = False
        self.start_time: datetime | None = None

        self.db: ChronicleDB
        self.llm: OllamaClient
        self.episodic_store: EpisodicStore
        self.semantic_store: SemanticStore
        self.identity_store: IdentityStore
        self.sentinel: Sentinel
        self.incident_logger: IncidentLogger
        self.agent: AgentCore
        self.dream_engine: DreamEngine
        self.fitness_monitor: FitnessMonitor
        self.scheduler: AsyncIOScheduler

    async def boot(self):
        platform_info = detect_platform()
        print(f"  🐺 Romulus v{self.config.version}")
        print(f"  Platform: {platform_info.system} ({platform_info.machine})")
        print(f"  Python: {platform_info.python_version}")
        print()

        # 1. Chronicle
        db_path = f"{self.config.data_dir}/chronicle.db"
        self.db = ChronicleDB(db_path=db_path)
        await self.db.initialize()
        self.episodic_store = EpisodicStore(self.db)
        self.semantic_store = SemanticStore(self.db)
        self.identity_store = IdentityStore(self.db)
        print("  [+] Chronicle initialized")

        # 2. LLM
        self.llm = OllamaClient(
            base_url=self.config.ollama.base_url,
            model=self.config.ollama.model,
        )
        if not await self.llm.is_available():
            print(f"  [!] Ollama not available at {self.config.ollama.base_url}")
            print(f"      Model: {self.config.ollama.model}")
            print(f"      Run: ollama serve & ollama pull {self.config.ollama.model}")
            sys.exit(1)
        print(f"  [+] LLM connected: {self.config.ollama.model}")

        # 3. Vigil
        innate = InnateLayer(rules_path=self.config.vigil.innate_rules_path)
        adaptive = AdaptiveLayer(self.db)
        await adaptive.load_memory_cells()
        self.incident_logger = IncidentLogger(self.db)
        self.sentinel = Sentinel(innate, adaptive, self.incident_logger)
        print("  [+] Vigil armed")

        # 4. Soul spec
        soul_path = Path(self.config.soul_path)
        soul_spec = soul_path.read_text() if soul_path.exists() else ""

        # 5. Identity
        identity = await self.identity_store.get_or_create_identity(
            self.config.name, soul_spec
        )
        print(f"  [+] Identity: {identity.name} | Tasks: {identity.total_tasks} | Trust: {identity.trust_score:.0%}")

        # 6. Agent
        tools = {
            "get_time": get_time,
            "get_system_info": get_system_info,
            "calculate": calculate,
        }
        self.agent = AgentCore(
            llm=self.llm,
            episodic_store=self.episodic_store,
            semantic_store=self.semantic_store,
            identity_store=self.identity_store,
            sentinel=self.sentinel,
            tools=tools,
            soul_spec=soul_spec,
        )
        print("  [+] Agent core ready")

        # 7. Dream Engine
        self.dream_engine = DreamEngine(
            llm=self.llm,
            episodic_store=self.episodic_store,
            semantic_store=self.semantic_store,
            chronicle_db=self.db,
        )
        print("  [+] Dream Engine loaded")

        # 8. Arena
        self.fitness_monitor = FitnessMonitor(self.episodic_store, self.incident_logger)

        # 9. Scheduler
        self.scheduler = AsyncIOScheduler()
        if self.config.dream.enabled:
            parts = self.config.dream.schedule_cron.split()
            self.scheduler.add_job(
                self._run_dream_cycle,
                CronTrigger(
                    minute=parts[0], hour=parts[1], day=parts[2],
                    month=parts[3], day_of_week=parts[4],
                ),
                id="dream_cycle",
            )
        self.scheduler.start()

        self.start_time = datetime.utcnow()
        self.running = True

        rules_count = await self.semantic_store.count_rules()
        traces_count = await self.episodic_store.count_traces()
        print(f"  [+] Rules: {rules_count} | Traces: {traces_count}")
        print(f"  [+] Dream schedule: {self.config.dream.schedule_cron}")
        print()
        print("  Romulus is awake. The wolves are ready.")
        print()

    async def ask(self, task: str, context: dict = None) -> "TaskResult":
        return await self.agent.handle_task(task, context or {})

    async def trigger_dream(self):
        print("\n  🌙 Dream cycle starting...")
        report = await self.dream_engine.run_dream_cycle(
            hours_to_review=self.config.dream.hours_to_review
        )
        print(f"  🌙 Dream complete: {report.episodes_processed} episodes, "
              f"{len(report.new_rules_extracted)} new rules")
        return report

    async def get_status(self) -> dict:
        identity = await self.identity_store.get_identity()
        fitness = await self.fitness_monitor.compute_fitness()
        rules_count = await self.semantic_store.count_rules()
        traces_count = await self.episodic_store.count_traces()
        uptime = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0

        return {
            "name": identity.name if identity else self.config.name,
            "version": self.config.version,
            "running": self.running,
            "uptime_seconds": int(uptime),
            "total_tasks": identity.total_tasks if identity else 0,
            "successful_tasks": identity.successful_tasks if identity else 0,
            "trust_score": identity.trust_score if identity else 0.5,
            "success_rate_7d": fitness.success_rate_7d,
            "composite_fitness": fitness.composite_fitness,
            "rules_learned": rules_count,
            "total_traces": traces_count,
            "model": self.config.ollama.model,
            "platform": detect_platform().model_dump(),
        }

    async def _run_dream_cycle(self):
        await self.trigger_dream()

    async def shutdown(self):
        print("\n  Romulus is going to sleep. Goodnight.")
        self.running = False
        self.scheduler.shutdown(wait=False)
        await self.llm.close()


async def main():
    config = RomulusConfig.load("config.yaml")
    daemon = RomulusDaemon(config)
    await daemon.boot()

    if config.interfaces.dashboard_enabled:
        import uvicorn
        from romulus.api import create_api

        app = create_api(daemon)

        server_config = uvicorn.Config(
            app,
            host=config.interfaces.dashboard_host,
            port=config.interfaces.dashboard_port,
            log_level="warning",
        )
        server = uvicorn.Server(server_config)

        async def run_server():
            await server.serve()

        async def run_repl():
            print(f"  Dashboard: http://localhost:{config.interfaces.dashboard_port}")
            print()
            print("  Commands: type a task, 'dream', 'status', 'rules', 'fitness', or 'quit'")
            print("  " + "─" * 60)
            print()

            while daemon.running:
                try:
                    task = await asyncio.get_event_loop().run_in_executor(
                        None, input, "  You: "
                    )
                    if not task.strip():
                        continue
                    if task.strip().lower() == "quit":
                        break
                    if task.strip().lower() == "dream":
                        report = await daemon.trigger_dream()
                        print(f"\n  📝 {report.summary}\n")
                        continue
                    if task.strip().lower() == "status":
                        s = await daemon.get_status()
                        print(f"\n  🐺 {s['name']} v{s['version']}")
                        print(f"  Uptime: {s['uptime_seconds']}s | Tasks: {s['total_tasks']}")
                        print(f"  Trust: {s['trust_score']:.0%} | Success: {s['success_rate_7d']:.0%}")
                        print(f"  Rules: {s['rules_learned']} | Model: {s['model']}\n")
                        continue
                    if task.strip().lower() == "rules":
                        rules = await daemon.semantic_store.get_all_rules()
                        if not rules:
                            print("\n  No rules learned yet.\n")
                        else:
                            print(f"\n  Learned Rules ({len(rules)}):")
                            for r in rules:
                                print(f"  • {r.rule} ({r.confidence:.0%})")
                            print()
                        continue
                    if task.strip().lower() == "fitness":
                        f = await daemon.fitness_monitor.compute_fitness()
                        print(f"\n  Fitness: {f.composite_fitness:.0%}")
                        print(f"  Success: {f.success_rate_7d:.0%} | Latency: {f.avg_latency_ms:.0f}ms")
                        print(f"  Calibration: {f.avg_confidence_calibration:.0%}")
                        print(f"  Vigil incidents: {f.vigil_incident_rate:.0%}\n")
                        continue

                    result = await daemon.ask(task)
                    print(f"\n  Romulus: {result.response}")
                    print(f"  [{result.confidence:.0%} confident | {result.tokens_used} tokens | {result.latency_ms}ms]")
                    if result.vigil_flags:
                        print(f"  🛡️ Vigil: {result.vigil_flags}")
                    print()

                except (KeyboardInterrupt, EOFError):
                    break

            await daemon.shutdown()
            server.should_exit = True

        await asyncio.gather(run_server(), run_repl())
    else:
        print("  Commands: type a task, 'dream', 'status', 'rules', or 'quit'")
        print("  " + "─" * 60)
        print()

        while daemon.running:
            try:
                task = await asyncio.get_event_loop().run_in_executor(
                    None, input, "  You: "
                )
                if task.strip().lower() == "quit":
                    break
                result = await daemon.ask(task)
                print(f"\n  Romulus: {result.response}\n")
            except (KeyboardInterrupt, EOFError):
                break

        await daemon.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
