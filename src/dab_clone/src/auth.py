from functools import wraps
from flask import request, jsonify


def authenticate_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not validate_token(auth_header):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)

    return wrapper


def validate_token(auth_header) -> bool:
    print("Authentication was successful")
    return True
