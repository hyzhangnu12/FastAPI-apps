from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_ENGINE: str
    DB_DRIVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    SQLALCHEMY_DATABASE_URL: str = ''
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    class Config:
        env_file = 'api/.api_env'

settings = Settings() # type: ignore