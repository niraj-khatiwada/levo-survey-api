from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv
from flask_injector import FlaskInjector


load_dotenv()

migrate = Migrate()
ma = Marshmallow()


def init_app():
    from src.database.db import init_db
    from src.api.api import init_api
    from src.config.config import Config
    from src.domain.modules import bind_modules
    from src.shared.error_handlers import register_error_handlers

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=["*"])

    db = init_db(app)
    migrate.init_app(app, db, directory="src/database/migrations")

    ma.init_app(app)

    init_api(app)

    register_error_handlers(app)

    FlaskInjector(app=app, modules=[bind_modules])

    return app
