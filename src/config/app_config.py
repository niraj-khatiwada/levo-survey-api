import os


class AppConfig:
    APP_TITLE = os.environ.get("APP_TITLE")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = (
        os.getenv("DEBUG").lower() if os.getenv("DEBUG") is not None else None
    ) == "true"
