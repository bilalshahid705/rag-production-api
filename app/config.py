"""
Centralized Configuration
Uses pydantic-settings for validated environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):

    #LLM Configuration
    openai_api_key: str
    primary_model: str = "gpt-4o-mini"
    fallback_model: str = "gpt-4o-mini"

    #langSmith Configuration
    langsmith_api_key: str
    langsmith_tracing: bool = True
    langsmith_project: str = "langchain-project"

    #Application Configuration
    app_env: str = "development"
    log_level: str = "INFO"
    rate_limit: str = "20/minute"
    cache_ttl_seconds: int = 300
    max_retries: int = 3

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


""""The Settings class is used once and used everywhere. No reading data is required. That why we use @lru_cache to cache the settings instance."""
@lru_cache
def get_settings() -> Settings:
    """Cached settings instance = loaded once, reused everywhere"""
    settings = Settings()

    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_TRACING"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    return Settings()
