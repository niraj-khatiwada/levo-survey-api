from flask_smorest import Api

from .v1.distribution_api import distribution_api as distribution_api_v1
from .v1.questions_api import questions_api as questions_api_v1
from .v1.responses_api import responses_api as responses_api_v1
from .v1.surveys_api import surveys_api as surveys_api_v1


def init_api(app):
    app.config["API_TITLE"] = app.config["APP_TITLE"]
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    # v1 API Routes
    api_v1 = Api(
        app,
        spec_kwargs={
            "version": "v1",
        },
    )
    api_v1.register_blueprint(distribution_api_v1)
    api_v1.register_blueprint(questions_api_v1)
    api_v1.register_blueprint(surveys_api_v1)
    api_v1.register_blueprint(responses_api_v1)
