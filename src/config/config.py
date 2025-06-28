from .app_config import AppConfig
from .database_config import DatabaseConfig


class Config(AppConfig, DatabaseConfig):
    pass
