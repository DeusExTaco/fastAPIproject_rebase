from functools import lru_cache
from typing import List, Literal
from pathlib import Path

import pydantic_settings
from pydantic import Field, ValidationError, computed_field


class Settings(pydantic_settings.BaseSettings):
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment (development, staging, production)"
    )
    DEBUG: bool = Field(default=False, description="Debug mode flag")

    # API Settings
    API_VERSION: str = Field(default="1.0.0", description="API version")
    PROJECT_NAME: str = Field(default="FastAPI Base", description="Project name")
    PROJECT_DESCRIPTION: str = Field(
        default="API for authentication and user management",
        description="Project description"
    )

    # Server Settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, ge=1, le=65535, description="Server port")

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    SQLALCHEMY_LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="WARNING",
        description="SQLAlchemy logging level"
    )

    # Security Settings
    JWT_ALGORITHM: str = Field(default="RS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT expiration time in minutes")
    CORS_ORIGINS: str = Field(default="*", description="Allowed CORS origins")
    CORS_CREDENTIALS: bool = Field(default=True, description="Allow CORS credentials")
    CORS_METHODS: str = Field(default="*", description="Allowed CORS methods")
    CORS_HEADERS: str = Field(default="*", description="Allowed CORS headers")

    # Auth0 Settings
    AUTH0_DOMAIN: str = Field(default=None, description="Auth0 domain")
    AUTH0_AUDIENCE: str = Field(default=None, description="Auth0 API identifier")
    AUTH0_CLIENT_ID: str = Field(default=None, description="Auth0 application client ID")
    AUTH0_CLIENT_SECRET: str = Field(default=None, description="Auth0 application client secret")
    APP_URL: str = Field(default="http://localhost:8000", description="Backend API URL")
    FRONTEND_URL: str = Field(default="http://localhost:5173", description="Frontend application URL")

    # Database Settings
    DB_USER: str = Field(default=None, description="Database user")
    DB_PASSWORD: str = Field(default=None, description="Database password")
    DB_HOST: str = Field(default=None, description="Database host")
    DB_PORT: int = Field(default=None, description="Database port")
    DB_NAME: str = Field(default=None, description="Database name")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Model config using SettingsConfigDict
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=str(Path(__file__).parents[2] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        validate_default=True
    )

    # Properties
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def cors_methods_list(self) -> List[str]:
        if self.CORS_METHODS == "*":
            return ["*"]
        return [method.strip() for method in self.CORS_METHODS.split(",")]

    @property
    def cors_headers_list(self) -> List[str]:
        if self.CORS_HEADERS == "*":
            return ["*"]
        return [header.strip() for header in self.CORS_HEADERS.split(",")]

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def validate_required_settings(self) -> List[str]:
        """Validate all required settings and return list of missing ones."""
        missing = []
        required_fields = [
            'AUTH0_DOMAIN', 'AUTH0_AUDIENCE', 'AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET',
            'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME'
        ]

        for field in required_fields:
            if not getattr(self, field):
                missing.append(field)

        return missing


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    try:
        settings = Settings()
        # Check for missing required values
        missing_fields = settings.validate_required_settings()
        if missing_fields:
            print("\nError: The following required environment variables are missing or empty in .env file:")
            for field in missing_fields:
                print(f"- {field}")
            print("\nPlease check your .env file and ensure all required variables are set.")
            print("\nCurrent .env file location:", Path(__file__).parents[2] / ".env")
            raise SystemExit(1)
        return settings
    except ValidationError as e:
        env_file = Path(__file__).parents[2] / ".env"
        if not env_file.exists():
            print(f"\nError: .env file not found at {env_file}!")
            print("Please create one using .env.template as a guide.\n")
        print("Validation errors:")
        for error in e.errors():
            print(f"- {error['loc'][0]}: {error['msg']}")
        raise SystemExit(1)
    except Exception as e:
        print(f"\nError loading settings: {str(e)}")
        raise SystemExit(1)