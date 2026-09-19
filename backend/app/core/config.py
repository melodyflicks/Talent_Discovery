from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate backend and root directories for .env discovery
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BACKEND_DIR.parent

env_files = []
# Prioritize backend/.env, then root .env
if (BACKEND_DIR / ".env").exists():
    env_files.append(str(BACKEND_DIR / ".env"))
if (ROOT_DIR / ".env").exists():
    env_files.append(str(ROOT_DIR / ".env"))
if not env_files:
    env_files = [str(BACKEND_DIR / ".env"), str(ROOT_DIR / ".env"), ".env"]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/talent_discovery"
    jwt_secret: str = "CHANGE_THIS_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"

    # Seed credentials
    default_admin_password: str = "CHANGE_ADMIN_PASSWORD"
    default_hr_password: str = "CHANGE_HR_PASSWORD"

    # AI & Integrations
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=tuple(env_files),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def sync_database_url(self) -> str:
        """Ensure standard postgresql:// is compatible with psycopg 3 driver."""
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
