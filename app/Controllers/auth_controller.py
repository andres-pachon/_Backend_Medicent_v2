from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app.Services.auth_service import AuthService

class AuthController:

    @staticmethod
    def login():
        data = request.get_json()
        email = (data.get("correo") or data.get("email") or "").strip()
        password = data.get("password") or data.get("contrasena") or ""

        usuario = AuthService.login(email, password)

        if usuario is None:
            return jsonify({"message": "Credenciales Incorrectas"}), 401

        token = create_access_token(
            identity=str(usuario.idUsuario),
            additional_claims={
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "rol": "admin" if usuario.administrador else "usuario"
            }
        )

        return jsonify({
            "accessToken": token,
            "user": {
                "id": usuario.idUsuario,
                "idUsuario": usuario.idUsuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "rol": "admin" if usuario.administrador else "usuario",
                "correo": usuario.correo,
                "documento": usuario.documento,
                "telefono": usuario.telefono,
                "fechaNacimiento": str(usuario.fechaNacimiento),
                "perfil": "paciente" if usuario.paciente is not None else ("cuidador" if usuario.cuidador is not None else None),
                "pacienteVinculado": bool(usuario.cuidador and usuario.cuidador.idPaciente),
                "activo": bool(usuario.activo)
            }
        }), 200

    @staticmethod
    def register():
        data = request.get_json(silent=True) or {}

        nuevo_usuario, error_msg = AuthService.register(
            nombre=data.get("nombre"),
            apellido=data.get("apellido"),
            documento=data.get("documento"),
            correo=data.get("correo"),
            telefono=data.get("telefono"),
            fechaNacimiento=data.get("fechaNacimiento"),
            password=data.get("password"),
            idTipoDocumento=data.get("idTipoDocumento")
        )

        if error_msg:
            return jsonify({"message": error_msg}), 400

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": nuevo_usuario.idUsuario,
                "idUsuario": nuevo_usuario.idUsuario,
                "nombre": nuevo_usuario.nombre,
                "apellido": nuevo_usuario.apellido,
                "correo": nuevo_usuario.correo,
                "rol": "usuario"
            }
        }), 201
