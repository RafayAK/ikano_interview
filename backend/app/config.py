from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ikano_onboarding"
    )
    log_level: str = "INFO"
    # Local Astro dev server default; add production/staging origins via APP_CORS_ALLOW_ORIGINS.
    cors_allow_origins: list[str] = ["http://localhost:4321"]
    resume_token_ttl_days: int = 30
    # False for local http dev; set true once served over https in production.
    cookie_secure: bool = False
    # Path to compiled static frontend assets (e.g. Astro dist output)
    frontend_dist_dir: str | None = None


settings = Settings()

RESUME_COOKIE_NAME = "resume_token"
