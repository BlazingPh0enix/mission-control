"""Settings from environment variables or the repo's .env file."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root (this file is src/kerbal_copilot/config.py), so paths work from any folder
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")

    openrouter_api_key: str = ""
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-120b"
    tavily_api_key: str | None = None
    turso_database_url: str | None = None
    turso_auth_token: str | None = None
    hf_token: str | None = None
    hf_data_repo: str = "TheMaskedOne/kerbal-copilot-data"
    app_username: str | None = None
    app_password: str | None = None
    data_dir: Path = ROOT / "data"
    knowledge_dir: Path = ROOT / "knowledge"

    # Preference order. Anything not currently live on OpenRouter is skipped at startup.
    preferred_models: list[str] = [
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
    ]
    vision_models: list[str] = [
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3.5-super-vl:free",
    ]
    max_agent_steps: int = 4
    max_tokens: int = 3000
    # 45 leaves headroom under OpenRouter's 50/day free cap. Set ~950 after buying 10 credits.
    daily_request_budget: int = 45


settings = Settings()
