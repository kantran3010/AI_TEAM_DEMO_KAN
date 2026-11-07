import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    # Default model: Gemini 2.5 Flash / 1.5 Flash or OpenAI GPT-4o-mini
    # litellm supports "gemini/gemini-2.5-flash", "gemini/gemini-1.5-pro", "gpt-4o-mini", etc.
    DEFAULT_MODEL = os.getenv("AI_MODEL", "gemini/gemini-flash-latest")
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Execution Settings
    MAX_RETRY_ROUNDS = int(os.getenv("MAX_RETRY_ROUNDS", "3"))
    WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "workspace")).resolve()
    
    @classmethod
    def validate_keys(cls):
        """Check if at least one common API key is present."""
        if any([cls.GEMINI_API_KEY, cls.OPENAI_API_KEY, cls.GROQ_API_KEY, cls.ANTHROPIC_API_KEY]):
            return True
        return False
