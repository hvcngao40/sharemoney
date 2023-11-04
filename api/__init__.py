from flask import jsonify
from werkzeug.exceptions import HTTPException

from config import app


class ApiException(HTTPException):
    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload
        self.response = self.get_response()

    def get_response(self):
        response = jsonify({'message': self.description, 'payload': self.payload})
        response.status_code = self.status_code
        return response
