from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and optional .env files."""

    application_name: str = "AccessGuard"
    host: str = "127.0.0.1"
    port: int = 8472
    cors_origins: str = "http://127.0.0.1:43123,http://localhost:43123"
    database_url: str = "sqlite:///./accessguard.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
