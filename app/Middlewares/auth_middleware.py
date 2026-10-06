from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return func(*args, **kwargs)
        except Exception:
            return jsonify({"message": "Token inválido o expirado"}), 401
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            rol = claims.get("rol")
            if rol != "admin":
                return jsonify({"message": "No tiene permisos para realizar esta acción"}), 403
            return func(*args, **kwargs)
        except Exception:
            return jsonify({"message": "Token inválido o expirado"}), 401
    return wrapper