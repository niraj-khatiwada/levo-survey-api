import traceback
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    def handle_traceback():
        if app.config.get("DEBUG"):
            traceback.print_exc()

    # Catch Flask-Smorest specific validation errors
    @app.errorhandler(422)
    def handle_unprocessable_entity(error):
        messages = getattr(error, "data", {}).get("messages", ["Invalid request."])
        print(dir(error), error.data)
        return (
            {
                "code": getattr(error, "name", error.__class__.__name__),
                "errors": messages,
            },
            422,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        handle_traceback()
        return {
            "code": getattr(error, "name", "Unknown"),
            "message": error.description,
        }, getattr(error, "code", 400)

    @app.errorhandler(Exception)
    def fallback(error):
        handle_traceback()
        return (
            {
                "code": getattr(error, "name", error.__class__.__name__) or "Unknown",
                "message": str(error),
            },
            getattr(error, "code", 500),
        )
