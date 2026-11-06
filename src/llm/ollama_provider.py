"""PathMatch AI - Ollama Local LLM Provider.

Integrates with local Ollama instances (e.g. llama3, mistral) via REST endpoints.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any

from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.utils.logging_config import logger


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider implementation."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3", timeout_seconds: int = 60, max_retries: int = 1):
        super().__init__(model=model, timeout_seconds=timeout_seconds, max_retries=max_retries)
        self.base_url = base_url.rstrip("/")
        self.provider_name = "ollama"

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> LLMResponse:
        """Call Ollama /api/chat endpoint."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        headers = {"Content-Type": "application/json"}
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        last_error = None
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    raw_body = response.read().decode("utf-8")
                    parsed = json.loads(raw_body)

                    content = parsed.get("message", {}).get("content", "")
                    p_tokens = parsed.get("prompt_eval_count", 0)
                    c_tokens = parsed.get("eval_count", 0)
                    t_tokens = p_tokens + c_tokens
                    exec_time = int((time.time() - start_time) * 1000)

                    return LLMResponse(
                        content=content,
                        prompt_tokens=p_tokens,
                        completion_tokens=c_tokens,
                        total_tokens=t_tokens,
                        model=self.model,
                        provider=self.provider_name,
                        execution_time_ms=exec_time,
                        is_demo_mode=False
                    )

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Ollama connection attempt {attempt+1} failed: {last_error}")
                if attempt < self.max_retries:
                    time.sleep(1.0)
                    continue
                break

        exec_time = int((time.time() - start_time) * 1000)
        return LLMResponse(
            content="",
            model=self.model,
            provider=self.provider_name,
            execution_time_ms=exec_time,
            error=last_error or "Could not connect to Ollama local instance.",
            is_demo_mode=False
        )

