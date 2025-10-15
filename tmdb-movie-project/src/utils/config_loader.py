from dotenv import load_dotenv
import os
from pathlib import Path

def load_config():
    env_path = Path(__file__).resolve().parents[2] / "env" / ".env"
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("TMDB_API_KEY")

    if not api_key:
        raise ValueError("TMDB_API_KEY not found in env/.env file.")
    return api_key
