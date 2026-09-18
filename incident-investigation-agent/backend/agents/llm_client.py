import json
import logging
import re
from typing import Dict, Any, List, Optional
import httpx

from config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

logger = logging.getLogger("llm_client")

class LLMClient:
    """Provider-agnostic LLM interface with resilient offline fallback."""

    def __init__(self):
        self.provider = LLM_PROVIDER
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL
        self.base_url = LLM_BASE_URL

    def is_configured(self) -> bool:
        return bool(self.api_key and self.provider not in ("heuristic", "offline"))

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Optional[str]:
        """Attempts to call configured LLM. Returns None if unconfigured or failed."""
        if not self.is_configured():
            return None

        try:
            if "openai" in self.provider or (self.api_key and self.provider == "auto"):
                url = self.base_url or "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model or "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature
                }
                with httpx.Client(timeout=20.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        logger.warning(f"OpenAI API call returned status {resp.status_code}: {resp.text}")

            elif "gemini" in self.provider:
                # Direct Gemini REST API call
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model or 'gemini-1.5-flash'}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{system_prompt}\n\nUser Question:\n{user_prompt}"}]
                    }],
                    "generationConfig": {"temperature": temperature}
                }
                with httpx.Client(timeout=20.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates and candidates[0].get("content", {}).get("parts"):
                            return candidates[0]["content"]["parts"][0]["text"]
                    else:
                        logger.warning(f"Gemini API returned {resp.status_code}: {resp.text}")

        except Exception as e:
            logger.error(f"Error calling LLM provider {self.provider}: {e}")

        return None
