from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Research Workspace API"
    jwt_secret: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/research_workspace"
    cors_origins: str = "http://localhost:3000"
    notes_encryption_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    embeddable_url_allowlist: str = "arxiv.org,observablehq.com,docs.google.com,notion.so"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
