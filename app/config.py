"""
Centralized Configuration
Uses pydantic-settings for validated environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

    #LLM Configuration
    openai_api_key: str
    primary_model: str = "gpt-4o-mini"
    fallback_model: str = "gpt-4o-mini"

    #langSmith Configuration
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "langchain-project"

    #Application Configuration
    app_env: str = "development"
    log_level: str = "INFO"
    rate_linit: str = "20/minute"
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
    return Settings()