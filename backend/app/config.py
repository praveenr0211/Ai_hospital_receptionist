import os
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "hospital_receptionist"
    DATABASE_URL: str | None = None

    # Exotel Telephony Configuration
    EXOTEL_API_KEY: str = ""
    EXOTEL_API_TOKEN: str = ""
    EXOTEL_ACCOUNT_SID: str = ""
    EXOTEL_PHONE_NUMBER: str = ""
    EXOTEL_API_BASE_URL: str = "https://api.in.exotel.com"

    # Gemini Live Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_LIVE_MODEL: str = "gemini-3.8-live"

    # Voice / Audio Settings
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    VOICE_WS_URL: str = "ws://localhost:8000/api/v1/voice/stream"
    VOICE_INPUT_SAMPLE_RATE: int = 16000
    VOICE_OUTPUT_SAMPLE_RATE: int = 24000
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @computed_field
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            # If user provided a raw DATABASE_URL with @ in password, check if valid or use encoded components
            return self.DATABASE_URL
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{encoded_password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()
