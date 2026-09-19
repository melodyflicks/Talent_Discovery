from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://talent:talent@localhost:5432/talent_discovery"
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
