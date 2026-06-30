from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o"
    servio_api_base_url: str = "https://servio-uat.amnapps.com/backend/api"
    servio_api_token: str = ""
    max_tokens: int = 4096

    # WhatsApp Business Cloud API (Meta Graph API)
    whatsapp_phone_number_id: str = ""   # from Meta Developer Console
    whatsapp_access_token: str = ""      # permanent system-user token
    whatsapp_verify_token: str = ""      # secret you choose for webhook verification

    model_config = ConfigDict(env_file=".env")


settings = Settings()
