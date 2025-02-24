from functools import cached_property

from pydantic import AnyHttpUrl, PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # CORE SETTINGS
    ENV: str = "DEV"  # DEV, PROD
    PROJECT_NAME: str = "CV Parser API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "An API for an agentic CV Parser"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON_ENABLED: bool = False
    # CORS
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl]

    # OpenAI
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDINGS_MODEL: str = "text-embedding-3-small"

    # Embeddings
    PINECODE_API_KEY: str
    PINECODE_INDEX_NAME: str
    EMBEDDING_SEARCH_TYPE: str = ""
    EMBEDDING_SCORE_THRESHOLD: float = 0.1
    EMBEDDING_TOPK: int = 3

    # Database
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: int
    DATABASE_DB: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: int = 0

    # AWS S3
    # AWS_S3_BUCKET_NAME:str
    # AWS_S3_ACCESS_KEY_ID:str
    # AWS_S3_SECRET_ACCESS_KEY:str
    # AWS_S3_REGION_NAME:str
    # AWS_S3_BASE_FOLDER:str

    @computed_field
    @cached_property
    def DEFAULT_SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOSTNAME,
                port=self.DATABASE_PORT,
                path=self.DATABASE_DB,
            )
        )

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings: Settings = Settings()  # type: ignore
