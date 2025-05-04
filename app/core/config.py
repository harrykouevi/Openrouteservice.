import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "FastAPI Project")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    ORS_API_KEY: str = os.getenv("ORS_API_KEY")

settings = Settings()
