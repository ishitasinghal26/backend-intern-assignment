from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB_NAME: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
