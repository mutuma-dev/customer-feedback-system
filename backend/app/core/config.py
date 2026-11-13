"""All application settings in ONE place.

Spring equivalent: application.properties / @ConfigurationProperties.

Each setting is read from an environment variable with the same name in CAPITALS
(database_url <- DATABASE_URL). Values also come from the ".env" file in the folder you
start the app from. If a variable is missing, the default after "=" is used.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # env_file: also read ".env". extra="ignore": unknown variables in .env are not an error.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ---- Database ----
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/feedback"

    # ---- CORS: which website addresses may call this API from a browser (comma separated) ----
    frontend_origin: str = "http://localhost:3000"

    # ---- Who is told about unhappy customers ----
    care_rep_email: str = "care@companyx.example"
    care_rep_phone: str = ""  # empty = no SMS alert

    # ---- Email (SMTP) ----
    smtp_host: str = ""  # empty = emails are only written to the log
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "feedback@companyx.example"

    # ---- Africa's Talking (SMS) ----
    at_username: str = "sandbox"
    at_api_key: str = ""  # empty = SMS are only written to the log
    at_sender_id: str = ""

    # ---- AI: any provider that speaks the OpenAI "chat completions" format ----
    ai_api_key: str = ""  # empty = a built-in template reply is used
    ai_base_url: str = "https://api.groq.com/openai/v1"
    ai_model: str = "llama-3.3-70b-versatile"
    ai_timeout_seconds: float = 8.0

    @property
    def cors_origins(self) -> list[str]:
        """Turn "a.com, b.com" into ["a.com", "b.com"], ignoring spaces and empty parts."""
        return [o.strip() for o in self.frontend_origin.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Create Settings once and reuse it (like a Spring singleton bean).

    @lru_cache remembers the first result, so the .env file is only read one time.
    """
    return Settings()
