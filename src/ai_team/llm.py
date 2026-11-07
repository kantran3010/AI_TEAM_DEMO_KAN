import os
import time
import logging
import warnings
from typing import List, Dict, Any, Optional
import litellm
from ai_team.config import Config

# Suppress litellm noisy logs and deprecation warnings
litellm.suppress_debug_info = True
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

class LLMClient:
    def __init__(self, model: Optional[str] = None, temperature: float = 0.2):
        self.model = model or Config.DEFAULT_MODEL
        self.temperature = temperature
        self._setup_env()

    def _setup_env(self):
        """Map config keys to environment for litellm."""
        if Config.GEMINI_API_KEY and not os.getenv("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = Config.GEMINI_API_KEY
        if Config.OPENAI_API_KEY and not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        if Config.GROQ_API_KEY and not os.getenv("GROQ_API_KEY"):
            os.environ["GROQ_API_KEY"] = Config.GROQ_API_KEY
        if Config.ANTHROPIC_API_KEY and not os.getenv("ANTHROPIC_API_KEY"):
            os.environ["ANTHROPIC_API_KEY"] = Config.ANTHROPIC_API_KEY

    def generate(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None) -> str:
        """Call the LLM with messages, automatic retry, and fallback on 503/high-demand."""
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        # Fallback candidate models if primary model hits 503/high demand
        fallback_models = [self.model]
        if "gemini" in self.model:
            for alt in ["gemini/gemini-flash-latest", "gemini/gemini-3.5-flash", "gemini/gemini-3.7-flash"]:
                if alt not in fallback_models:
                    fallback_models.append(alt)

        last_error = None
        for current_model in fallback_models:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    # For Gemini 3+, avoid passing temperature as recommended by Google API
                    kwargs = {}
                    if "gemini" not in current_model.lower():
                        kwargs["temperature"] = self.temperature

                    response = litellm.completion(
                        model=current_model,
                        messages=full_messages,
                        **kwargs,
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    err_msg = str(e).lower()
                    last_error = e
                    # If high demand, 503, or rate limit: retry after short backoff
                    if "503" in err_msg or "high demand" in err_msg or "rate" in err_msg or "unavailable" in err_msg:
                        time.sleep(1.5 * (attempt + 1))
                        continue
                    # If 404 / model not found, immediately break to try next fallback
                    if "404" in err_msg or "not_found" in err_msg:
                        break
                    # Other unknown fatal error, break to fallback
                    break

        raise RuntimeError(f"Lỗi khi gọi mô hình {self.model}: {str(last_error)}") from last_error

