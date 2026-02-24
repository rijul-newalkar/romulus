from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class AskRequest(BaseModel):
    task: str
    context: dict = {}


def create_api(daemon) -> FastAPI:
    app = FastAPI(title="Romulus", version="0.1.0", description="Agent Operating System")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/status")
    async def status():
        return await daemon.get_status()

    @app.post("/api/ask")
    async def ask(request: AskRequest):
        result = await daemon.ask(request.task, request.context)
        return result.model_dump()

    @app.post("/api/dream")
    async def trigger_dream():
        report = await daemon.trigger_dream()
        return report.model_dump(mode="json")

    @app.get("/api/rules")
    async def get_rules():
        rules = await daemon.semantic_store.get_all_rules()
        return [r.model_dump(mode="json") for r in rules]

    @app.get("/api/fitness")
    async def get_fitness():
        fitness = await daemon.fitness_monitor.compute_fitness()
        return fitness.model_dump()

    @app.get("/api/traces")
    async def get_traces(limit: int = 50):
        traces = await daemon.episodic_store.get_traces(limit=limit)
        return [t.model_dump(mode="json") for t in traces]

    @app.get("/api/dream-reports")
    async def get_dream_reports():
        rows = await daemon.db.execute(
            "SELECT * FROM dream_reports ORDER BY date DESC LIMIT 10"
        )
        return rows

    @app.get("/api/vigil/incidents")
    async def get_vigil_incidents(hours: int = 24):
        return await daemon.incident_logger.get_recent_incidents(hours=hours)

    return app
