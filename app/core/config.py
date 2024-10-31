from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:LocalPass@localhost/coding_challenge_db"
    # Add other configuration variables here
    SECRET_KEY: str = "GasStationSecret"  # Change this!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
