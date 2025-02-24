from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # CORE SETTINGS
    ENV: str = "DEV" # DEV, PROD
    PROJECT_NAME: str = "Agentic Researcher API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "An API for a fullstack agentic researcher"

    OPENAI_API_KEY: str
    CORE_API_KEY: str
    
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True
    )


settings: Settings = Settings()