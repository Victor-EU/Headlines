from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://headlines:headlines@db:5432/headlines"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""
    ADMIN_PASSWORD: str = "change-me"
    BRIEFING_TIMEZONE: str = "America/New_York"
    SLACK_WEBHOOK_URL: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
