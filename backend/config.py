from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o"
    servio_api_base_url: str = "https://servio-uat.amnapps.com/backend/api"
    servio_api_token: str = ""
    max_tokens: int = 4096

    model_config = ConfigDict(env_file=".env")


settings = Settings()
