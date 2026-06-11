from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os
load_dotenv(override=True)
APP_ENV = os.getenv("APP_ENV", "dev")

class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str

    # API_HOST: str
    # API_PORT: int

    LLM_PROVIDER: str

    OLLAMA_MODEL: str | None = None
    OLLAMA_BASE_URL: str | None = None

    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str | None = None

    
    
    DATABASE_URL : str
    # JWT_SECRET_KEY : str
    # JWT_ALGORITHM : str
    # ACCESS_TOKEN_EXPIRE_MINUTES :int
    # REFRESS_TOKEN_EXPIRE_DAYS :int

    REDIS_HOST : str = "127.0.0.1"
    REDIS_PORT : int = 6379

    # MAIL_USERNAME: str
    # MAIL_PASSWORD: str
    # MAIL_FROM: str
    # MAIL_PORT: int
    # MAIL_SERVER: str
    # MAIL_FROM_NAME: str
    # MAIL_STARTTLS: bool = True   
    # MAIL_SSL_TLS: bool = False
    
    # RAZORPAY_KEY_ID : str
    # RAZORPAY_KEY_SECRET : str

    # model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    model_config = SettingsConfigDict(env_file=f".env.{APP_ENV}", extra="ignore")
    



settings = Settings()