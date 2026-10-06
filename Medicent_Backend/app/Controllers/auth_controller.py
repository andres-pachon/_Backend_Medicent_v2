from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.database.database import bcrypt
from app.models.usuario import Usuario
from app.Services.auth_service import AuthService


class AuthController:

    @staticmethod
    def login():
        data = request.get_json(silent=True) or {}

        correo = (data.get("correo") or data.get("email") or "").strip()
        password = data.get("password") or data.get("contrasena") or ""

        print("LOGIN llaves recibidas:", list(data.keys()))
        print("LOGIN correo:", correo)

        if not correo or not password:
            texto = "Falta correo o contraseña. El front mandó estas llaves: " + str(list(data.keys()))
            return jsonify({"error": texto, "message": texto, "mensaje": texto}), 400

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario is None:
            texto = "No existe un usuario con este correo: " + correo
            print("LOGIN 401:", texto)
            return jsonify({"error": texto, "message": texto, "mensaje": texto}), 401

        try:
            clave_ok = bcrypt.check_password_hash(usuario.password, password)
        except Exception as e:
            print("LOGIN error bcrypt:", e)
            clave_ok = False

        if not clave_ok:
            texto = "El correo SÍ existe. La contraseña no coincide."
            print("LOGIN 401:", texto)
            return jsonify({"error": texto, "message": texto, "mensaje": texto}), 401

        rol = "usuario"
        try:
            if AuthService.es_admin(usuario):
                rol = "admin"
        except Exception:
            rol = "usuario"

        token = create_access_token(
            identity=str(usuario.idUsuario),
            additional_claims={
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "rol": rol,
            },
        )

        user = {
            "id": usuario.idUsuario,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "correo": usuario.correo,
            "rol": rol,
        }

        print("LOGIN 200:", correo)
        return jsonify({
            "message": "Inicio de sesión exitoso",
            "accessToken": token,
            "access_token": token,
            "user": user,
            "usuario": user,
        }), 200

    @staticmethod
    def register():
        data = request.get_json(silent=True) or {}

        nuevo_usuario, error_msg = AuthService.register(
            nombre=data.get("nombre"),
            apellido=data.get("apellido"),
            documento=data.get("documento"),
            correo=(data.get("correo") or data.get("email") or "").strip() if (data.get("correo") or data.get("email")) else None,
            telefono=data.get("telefono"),
            fechaNacimiento=data.get("fechaNacimiento"),
            password=data.get("password") or data.get("contrasena"),
            idTipoDocumento=data.get("idTipoDocumento"),
        )

        if error_msg:
            return jsonify({"message": error_msg, "error": error_msg, "mensaje": error_msg}), 400

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": nuevo_usuario.idUsuario,
                "nombre": nuevo_usuario.nombre,
                "apellido": nuevo_usuario.apellido,
                "correo": nuevo_usuario.correo,
            },
        }), 201