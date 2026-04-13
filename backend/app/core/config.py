from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    SIMULATOR_INTERVAL_SECONDS: int = 35

    class Config:
        env_file = ".env"

settings = Settings()