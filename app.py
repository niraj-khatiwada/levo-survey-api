from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from flask_injector import FlaskInjector
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from src.config.database_config import DatabaseConfig


load_dotenv()

migrate = Migrate()
mallow = Marshmallow()
mail = Mail()
scheduler = BackgroundScheduler(
    jobstores={
        "default": SQLAlchemyJobStore(url=DatabaseConfig.SQLALCHEMY_DATABASE_URI)
    },
    job_defaults={
        "coalesce": False,
        "max_instances": 3,
        "misfire_grace_time": 60,
    },
    timezone="UTC",
)


def init_app():
    from src.database.db import init_db
    from src.api.api import init_api
    from src.modules import bind_modules
    from src.shared.error_handlers import register_error_handlers
    from src.config.config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["*"])

    db = init_db(app)
    migrate.init_app(app, db, directory="src/database/migrations")

    mail.init_app(app)

    mallow.init_app(app)

    init_api(app)

    register_error_handlers(app)

    if not scheduler.running:
        scheduler.start()

    FlaskInjector(app=app, modules=[bind_modules])

    return app
