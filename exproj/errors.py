import json
from werkzeug.exceptions import HTTPException, BadRequest
from schema import SchemaError

from . import app, logger


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    logger.warning(f'{e.code} - [{e}]')  # i think it's not necessary

    response = e.get_response()

    response.data = json.dumps({
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(SchemaError)
def handle_schema_error(e):
    return handle_http_exception(BadRequest(str(e)))