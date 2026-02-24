import time

import httpx
from pydantic import BaseModel


class LLMResponse(BaseModel):
    text: str
    tokens_used: int
    latency_ms: int
    model: str


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:1.5b"):
        self.base_url = base_url
        self.model = model
        self._client = httpx.AsyncClient(base_url=base_url, timeout=120.0)

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> LLMResponse:
        start = time.monotonic()
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        resp = await self._client.post("/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed_ms = int((time.monotonic() - start) * 1000)
        tokens = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)

        return LLMResponse(
            text=data.get("response", "").strip(),
            tokens_used=tokens,
            latency_ms=elapsed_ms,
            model=self.model,
        )

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> LLMResponse:
        start = time.monotonic()
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        resp = await self._client.post("/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        elapsed_ms = int((time.monotonic() - start) * 1000)
        tokens = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)
        text = data.get("message", {}).get("content", "").strip()

        return LLMResponse(
            text=text,
            tokens_used=tokens,
            latency_ms=elapsed_ms,
            model=self.model,
        )

    async def is_available(self) -> bool:
        try:
            resp = await self._client.get("/api/tags")
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(self.model in m for m in models)
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    async def list_models(self) -> list[str]:
        try:
            resp = await self._client.get("/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except (httpx.ConnectError, httpx.TimeoutException):
            return []

    async def close(self):
        await self._client.aclose()
