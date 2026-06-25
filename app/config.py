from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # 火山引擎方舟 API (即梦AI 图片生成)
    ark_api_key: str
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"

    # Database
    database_url: str = "sqlite+aiosqlite:///./vision_of_scale.db"

    # Generated images storage
    generated_images_dir: str = "app/static/generated"

    # Default model
    default_model: str = "doubao-seedream-4-0-250828"

    # App info
    app_name: str = "Vision of Scale"
    app_version: str = "0.1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore deprecated/unknown env vars


@lru_cache()
def get_settings() -> Settings:
    return Settings()
