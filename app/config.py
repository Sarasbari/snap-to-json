from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    APP_ENV: str = "development"
    MAX_FILE_SIZE_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
