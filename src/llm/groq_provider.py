"""PathMatch AI - Groq LLM Provider.

Integrates with Groq API high-speed endpoints (e.g. llama-3.3-70b-versatile, mixtral).
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any

from src.llm.base_provider import BaseLLMProvider, LLMResponse
from src.utils.logging_config import logger


class GroqProvider(BaseLLMProvider):
    """Groq API Provider implementation."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", timeout_seconds: int = 30, max_retries: int = 2):
        super().__init__(model=model, timeout_seconds=timeout_seconds, max_retries=max_retries)
        self.api_key = api_key
        self.provider_name = "groq"

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured.")

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> LLMResponse:
        """Call Groq chat completions endpoint."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.API_URL, data=data_bytes, headers=headers, method="POST")

        last_error = None
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    raw_body = response.read().decode("utf-8")
                    parsed = json.loads(raw_body)

                    content = parsed["choices"][0]["message"]["content"]
                    usage = parsed.get("usage", {})
                    p_tokens = usage.get("prompt_tokens", 0)
                    c_tokens = usage.get("completion_tokens", 0)
                    t_tokens = usage.get("total_tokens", p_tokens + c_tokens)
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

            except urllib.error.HTTPError as e:
                err_content = e.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {e.code}: {err_content}"
                logger.warning(f"Groq API attempt {attempt+1} failed: {last_error}")
                if e.code in (429, 500, 502, 503) and attempt < self.max_retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Groq API connection error: {last_error}")
                if attempt < self.max_retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                break

        exec_time = int((time.time() - start_time) * 1000)
        return LLMResponse(
            content="",
            model=self.model,
            provider=self.provider_name,
            execution_time_ms=exec_time,
            error=last_error or "Unknown error calling Groq API",
            is_demo_mode=False
        )

