from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://headlines:headlines@db:5432/headlines"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""
    ADMIN_PASSWORD: str = "change-me"
    BRIEFING_TIMEZONE: str = "America/New_York"
    SLACK_WEBHOOK_URL: str = ""
    CORS_ORIGINS: str = "http://localhost:3000"
    RUN_SCHEDULER: bool = False

    @property
    def async_database_url(self) -> str:
        """Normalize DATABASE_URL for asyncpg driver."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
