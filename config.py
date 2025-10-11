"""Application configuration loading and defaults"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    """Base configuration loader"""

    # Bluesky credentials (Required)
    BSKY_HANDLE: str
    BSKY_APP_PASSWORD: str
    BSKY_TARGET_HANDLE: str
    
    # API settings (with defaults)
    REPORT_LIMIT: int = Field(default=100, gt=0, le=100, description="Number of followers to fetch per request")
    RATE_LIMIT_DELAY: float = Field(default=0.05, ge=0, description="Delay between API requests in seconds, to avoid rate limiting")
    MAX_RETRIES: int = Field(default=3, gt=0, description="API request maximum number of retries on failure")
    RETRY_DELAY: float = Field(default=1.0, ge=0, description="Maximum delay between API request retries, in seconds")

    # Activity settings
    ACTIVITY_WINDOW_DAYS: int = Field(default=31, gt=0, description="Days to consider for active users")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Ignore extra fields in .env
    )

# Singleton instance
config = Config()