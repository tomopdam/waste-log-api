import os


class Settings:
    """
    Global application configuration settings. Mostly taken from environment variables.
    """

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "myuser")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "mypassword")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "mydb")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))

    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    API_KEY: str = os.getenv("API_KEY", "mysecretapikey")
    DEBUG: bool = (
        os.getenv("DEBUG", "false").lower() == "true"
    )  # convert to boolean to avoid string literal, i.e. DEBUG = "FALSE"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@test.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    # ACCESS_TOKEN_EXPIRE_MINUTES=60*24*31
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 31)
    )  # 31 days

    ALGORITHM: str = "HS256"


settings = Settings()
