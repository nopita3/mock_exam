import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_base_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = _base_config
    

    @property
    def POSTGRES_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def REDIS_URL(self,db: str ) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"

class SecuritySettings(BaseSettings):
    JWT_SECRET :str
    JWT_ALGORITHM :str

    model_config = _base_config

class EmailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_FROM : str
    MAIL_PASSWORD : str
    MAIL_PORT : int
    MAIL_FROM_NAME : str
    MAIL_SERVER : str
    MAIL_STARTTLS : bool = True
    MAIL_SSL_TLS : bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    model_config = _base_config

class OauthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    model_config = _base_config

class AppSettings(BaseSettings):
    APP_NAME: str
    app_domain: str 
    frontend_app_domain: str
    ALLOWED_EMAIL_DOMAIN: str 
    TEACHER_CODE: str 
    ADMIN_CODE: str

    model_config = _base_config


db_settings = DatabaseSettings()
securuity_settings = SecuritySettings()
email_settings = EmailSettings()
oauth_settings = OauthSettings()
app_settings = AppSettings()