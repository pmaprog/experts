from werkzeug.exceptions import BadRequest
from flask import json


# todo
class QuestionNotFound(Exception):
    def __init__(self, id):
        self.id = id


class JSONBadRequest(BadRequest):
    def get_body(self, environ=None):
        """Get the JSON body."""
        return json.dumps({
            'code': self.code,
            'name': self.name,
            'description': self.description,
        })

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]


class WrongDataError(Exception):
    pass
