"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "To-Do API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database configuration
    database_url: str = "postgresql://user:password@localhost:5432/todo_db"
    database_echo: bool = False

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: list[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    class Config:
        """Configuration class."""

        env_file = ".env"
        case_sensitive = False


settings = Settings()
