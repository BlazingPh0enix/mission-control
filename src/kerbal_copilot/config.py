from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = str(os.getenv("OPENROUTER_API_KEY"))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openrouter_api_key: str
    groq_api_key: str | None = None
    tavily_api_key: str | None = None
    turso_database_url: str | None = None
    turso_auth_token: str | None = None
    hf_token: str | None = None
    hf_data_repo: str = "you/kerbal-copilot-data"
    preferred_models: list[str] = [
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
    ]
    vision_models: list[str] = [
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3.5-super-vl:free"
    ]
    max_agent_steps: int = 4
    daily_request_budget: int = 45

settings = Settings(openrouter_api_key=OPENROUTER_API_KEY)