"""Every setting in one place (Spring: application.properties / @ConfigurationProperties).

Values come from environment variables or the `.env` file in the folder you start the app from.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = ""

    # Which website origins may call the API from a browser (CORS), comma separated.
    frontend_origin: str = "http://localhost:3000"

    # Who gets told about unhappy customers.
    care_rep_email: str = "care@companyx.example"
    care_rep_phone: str = ""

    # Email (SMTP)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "feedback@companyx.example"

    # Africa's Talking (SMS)
    at_username: str = "sandbox"
    at_api_key: str = ""
    at_sender_id: str = ""

    # AI provider: any service that speaks the OpenAI "chat completions" format
    ai_api_key: str = ""
    ai_base_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "llama-3.3-70b-versatile"
    ai_timeout_seconds: float = 8.0

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.frontend_origin.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Build Settings once and share it (like a Spring singleton bean)."""
    return Settings()
