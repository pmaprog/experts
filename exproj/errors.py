import json
from werkzeug.exceptions import HTTPException, BadRequest
from schema import SchemaError

from exproj import app, logger


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    original_exc = getattr(e, 'original_exception', None)
    logger.warning(str(e))  # i think it's not necessary

    response = e.get_response()

    response.data = json.dumps({
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(SchemaError)
def handle_schema_error(e):
    return handle_http_exception(BadRequest(str(e)))
