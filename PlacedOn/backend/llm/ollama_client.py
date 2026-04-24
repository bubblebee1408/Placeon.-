import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class OllamaError(Exception):
    pass


def call_ollama(prompt: str, model: str = "llama3", options: Optional[Dict[str, Any]] = None) -> str:
    logger.info("[OLLAMA] request sent")
    try:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        merged_options: dict[str, Any] = {"num_predict": 128}
        if options:
            merged_options.update(options)
            
        format_val = merged_options.pop("format", "json")
        if format_val:
            payload["format"] = format_val
            
        payload["options"] = merged_options

        timeout_seconds = float(merged_options.pop("timeout_seconds", 20))

        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=timeout_seconds,
        )

        if response.status_code != 200:
            raise OllamaError(f"HTTP {response.status_code}")

        logger.info("[OLLAMA] response received")
        return response.json()["response"].strip()
    except Exception as exc:  # noqa: BLE001
        logger.error("[OLLAMA ERROR] %s", exc)
        raise
