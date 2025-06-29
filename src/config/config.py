from .app_config import AppConfig
from .database_config import DatabaseConfig
from .mail_config import MailConfig


class Config(AppConfig, DatabaseConfig, MailConfig):
    pass
