from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    from src.config.database_config import DatabaseConfig

    app.config.from_object(DatabaseConfig)
    db.init_app(app)
    return db
