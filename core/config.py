from functools import cached_property

from pydantic import AnyHttpUrl, PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # CORE SETTINGS
    ENV: str = "dev"  # dev, prod 
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
    UNSTRUCTURED_API_KEY: str

    # Embeddings
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    EMBEDDING_SEARCH_TYPE: str = ""
    EMBEDDING_SCORE_THRESHOLD: float = 0.1
    EMBEDDING_TOPK: int = 3

    # Database
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    ECHO_SQL: bool = False

    # Redis
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: int = 0

    # AWS S3
    AWS_S3_BUCKET_NAME:str | None = None
    AWS_S3_ACCESS_KEY_ID:str | None = None
    AWS_S3_SECRET_ACCESS_KEY:str | None = None
    AWS_S3_REGION_NAME:str | None = None
    AWS_S3_BASE_FOLDER:str | None = None
    AWS_S3_BUCKET_NAME_PRIVATE:str | None = None
    
    
    @computed_field
    @cached_property
    def S3_ENABLED(self) -> bool:
        return all(
            [
                self.AWS_S3_BUCKET_NAME,
                self.AWS_S3_ACCESS_KEY_ID,
                self.AWS_S3_SECRET_ACCESS_KEY,
                self.AWS_S3_REGION_NAME,
                self.AWS_S3_BASE_FOLDER,
            ]
        )
    
    @computed_field
    @cached_property
    def DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOSTNAME,
                port=self.DATABASE_PORT,
                path=self.DATABASE_NAME,
            )
        )
    @computed_field
    @cached_property
    def SYNC_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOSTNAME,
                port=self.DATABASE_PORT,
                path=self.DATABASE_NAME,
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
