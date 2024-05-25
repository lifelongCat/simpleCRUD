from asyncpg.pool import Pool
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    POSTGRES_POOL: Pool | None = None

    FASTAPI_PORT: int

    @property
    def POSTGRES_URL(self):
        return (f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
