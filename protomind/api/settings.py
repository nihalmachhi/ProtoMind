from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROTOMIND_", env_file=".env", extra="ignore")
    database: str = "data/protomind.sqlite3"
    capture_dir: str = "data/captures"
    run_dir: str = "data/runs"
    max_upload_mb: int = Field(default=50, ge=1, le=250)
    cors_origin: str = "http://localhost:5173"

    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origin.split(",") if origin.strip()]
