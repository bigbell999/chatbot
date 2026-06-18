from pydantic_settings import BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    app_name: str = "chatbot"
    debug_mode: bool = False
    database_url: str
    secret_key: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Setting()