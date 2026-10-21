from datetime import date, datetime, timedelta
import secrets

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.database.database import db
from app.models.cuidador import Cuidador
from app.models.paciente import Paciente, TipoSangreEnum
from app.models.usuario import Usuario


class PerfilController:
    @staticmethod
    def _usuario_actual():
        try:
            id_usuario = int(get_jwt_identity())
        except (TypeError, ValueError):
            return None
        return db.session.get(Usuario, id_usuario)

    @staticmethod
    @jwt_required()
    def obtener_perfil():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401

        perfil = "admin" if usuario.administrador is not None else (
            "paciente" if usuario.paciente is not None else (
                "cuidador" if usuario.cuidador is not None else None
            )
        )
        return jsonify({
            "user": {
                "idUsuario": usuario.idUsuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo,
                "telefono": usuario.telefono,
                "fechaNacimiento": usuario.fechaNacimiento.isoformat(),
                "rol": "admin" if usuario.administrador is not None else "usuario",
                "perfil": perfil,
                "contactoEmergencia": usuario.paciente.contactoEmergencia if usuario.paciente else None,
                "pacienteVinculado": bool(usuario.cuidador and usuario.cuidador.idPaciente),
                "experienciaAnios": usuario.cuidador.experienciaAnios if usuario.cuidador else None
            }
        }), 200

    @staticmethod
    @jwt_required()
    def actualizar_perfil():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401

        data = request.get_json(silent=True) or {}
        campos = ("nombre", "apellido", "correo", "telefono", "fechaNacimiento")
        valores = {}
        for campo in campos:
            if campo not in data:
                continue
            valor = str(data[campo] or "").strip()
            if campo in ("nombre", "apellido", "correo", "fechaNacimiento") and not valor:
                return jsonify({"message": f"El campo {campo} es obligatorio"}), 400
            valores[campo] = valor or None

        correo = valores.get("correo")
        if correo:
            valores["correo"] = correo.lower()
            duplicado = Usuario.query.filter(
                Usuario.correo == valores["correo"], Usuario.idUsuario != usuario.idUsuario
            ).first()
            if duplicado:
                return jsonify({"message": "El correo ya está registrado"}), 409

        if "fechaNacimiento" in valores:
            try:
                valores["fechaNacimiento"] = date.fromisoformat(valores["fechaNacimiento"])
            except (TypeError, ValueError):
                return jsonify({"message": "La fecha de nacimiento debe tener el formato AAAA-MM-DD"}), 400

        if "contactoEmergencia" in data:
            if usuario.paciente is None:
                return jsonify({"message": "Solo un perfil de paciente tiene contacto de emergencia"}), 409
            usuario.paciente.contactoEmergencia = str(data["contactoEmergencia"] or "").strip() or None

        for campo, valor in valores.items():
            setattr(usuario, campo, valor)
        for perfil_relacionado in (usuario.administrador, usuario.cuidador):
            if perfil_relacionado is None:
                continue
            for campo in ("nombre", "apellido", "correo", "telefono"):
                if campo in valores:
                    setattr(perfil_relacionado, campo, valores[campo])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se pudo actualizar el perfil; revisa el correo ingresado"}), 409

        perfil = "admin" if usuario.administrador is not None else (
            "paciente" if usuario.paciente is not None else (
                "cuidador" if usuario.cuidador is not None else None
            )
        )
        return jsonify({
            "message": "Perfil actualizado correctamente",
            "user": {
                "idUsuario": usuario.idUsuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo,
                "telefono": usuario.telefono,
                "fechaNacimiento": usuario.fechaNacimiento.isoformat(),
                "rol": "admin" if usuario.administrador is not None else "usuario",
                "perfil": perfil,
                "contactoEmergencia": usuario.paciente.contactoEmergencia if usuario.paciente else None,
                "pacienteVinculado": bool(usuario.cuidador and usuario.cuidador.idPaciente),
                "experienciaAnios": usuario.cuidador.experienciaAnios if usuario.cuidador else None
            }
        }), 200

    @staticmethod
    @jwt_required()
    def crear_perfil_paciente():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        if usuario.administrador is not None:
            return jsonify({"message": "Una cuenta administradora no puede crear un perfil de paciente"}), 403
        if usuario.paciente is not None or usuario.cuidador is not None:
            return jsonify({"message": "La cuenta ya tiene un perfil asignado"}), 409

        data = request.get_json(silent=True) or {}
        obligatorios = (
            "estatura",
            "peso",
            "tipoSangre",
            "contactoEmergencia",
            "eps",
            "alergias",
            "diagnostico"
        )
        faltantes = [campo for campo in obligatorios if not data.get(campo)]
        if faltantes:
            return jsonify({"message": "Faltan campos obligatorios", "campos": faltantes}), 400

        try:
            estatura = float(data["estatura"])
            peso = float(data["peso"])
            tipo_sangre = TipoSangreEnum(str(data["tipoSangre"]))
        except (TypeError, ValueError):
            return jsonify({"message": "Estatura, peso o tipo de sangre no son válidos"}), 400

        if estatura <= 0 or peso <= 0:
            return jsonify({"message": "La estatura y el peso deben ser mayores que cero"}), 400

        paciente = Paciente(
            estatura=estatura,
            peso=peso,
            tipoSangre=tipo_sangre,
            dieta=str(data.get("dieta", "")).strip() or None,
            contactoEmergencia=str(data["contactoEmergencia"]).strip(),
            eps=str(data["eps"]).strip(),
            alergias=str(data["alergias"]).strip(),
            diagnostico=str(data["diagnostico"]).strip(),
            idUsuario=usuario.idUsuario
        )
        try:
            db.session.add(paciente)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se pudo guardar el perfil del paciente"}), 409

        return jsonify({
            "message": "Perfil de paciente guardado",
            "perfil": "paciente",
            "idPaciente": paciente.idPaciente
        }), 201

    @staticmethod
    @jwt_required()
    def crear_perfil_cuidador():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        if usuario.administrador is not None:
            return jsonify({"message": "Una cuenta administradora no puede crear un perfil de cuidador"}), 403
        if usuario.paciente is not None or usuario.cuidador is not None:
            return jsonify({"message": "La cuenta ya tiene un perfil asignado"}), 409

        data = request.get_json(silent=True) or {}
        try:
            experiencia = int(data.get("experienciaAnios"))
        except (TypeError, ValueError):
            return jsonify({"message": "Los años de experiencia deben ser un número entero"}), 400
        if experiencia < 0:
            return jsonify({"message": "Los años de experiencia no pueden ser negativos"}), 400

        cuidador = Cuidador(
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            correo=usuario.correo,
            telefono=usuario.telefono,
            experienciaAnios=experiencia,
            idUsuario=usuario.idUsuario
        )
        try:
            db.session.add(cuidador)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se pudo guardar el perfil del cuidador"}), 409

        return jsonify({
            "message": "Perfil de cuidador guardado",
            "perfil": "cuidador",
            "idCuidador": cuidador.idCuidador
        }), 201


    @staticmethod
    @jwt_required()
    def generar_codigo_vinculacion():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        if usuario.paciente is None:
            return jsonify({"message": "Solo un paciente puede generar un código de invitación"}), 403

        paciente = usuario.paciente
        paciente.codigoVinculacion = secrets.token_hex(12).upper()
        paciente.codigoVinculacionExpira = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
        return jsonify({
            "codigo": paciente.codigoVinculacion,
            "expiraEn": paciente.codigoVinculacionExpira.isoformat() + "Z"
        }), 201

    @staticmethod
    @jwt_required()
    def obtener_vinculacion():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        if usuario.paciente is not None:
            return jsonify({
                "perfil": "paciente",
                "cuidadores": [{
                    "idCuidador": cuidador.idCuidador,
                    "nombre": cuidador.nombre,
                    "apellido": cuidador.apellido,
                    "correo": cuidador.correo
                } for cuidador in usuario.paciente.cuidadores]
            }), 200
        if usuario.cuidador is not None:
            paciente = usuario.cuidador.paciente
            return jsonify({
                "perfil": "cuidador",
                "paciente": ({
                    "idPaciente": paciente.idPaciente,
                    "nombre": paciente.usuario.nombre,
                    "apellido": paciente.usuario.apellido
                } if paciente is not None else None)
            }), 200
        return jsonify({"message": "La cuenta no tiene un perfil que pueda vincularse"}), 409

    @staticmethod
    @jwt_required()
    def canjear_codigo_vinculacion():
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        if usuario.cuidador is None:
            return jsonify({"message": "Solo un cuidador puede canjear un código"}), 403
        if usuario.cuidador.idPaciente is not None:
            return jsonify({"message": "Tu cuenta ya está vinculada a un paciente"}), 409

        data = request.get_json(silent=True) or {}
        codigo = str(data.get("codigo", "")).strip().upper()
        if not codigo:
            return jsonify({"message": "Ingresa el código de invitación"}), 400

        paciente = Paciente.query.filter_by(codigoVinculacion=codigo).first()
        ahora = datetime.utcnow()
        if paciente is None or paciente.codigoVinculacionExpira is None or paciente.codigoVinculacionExpira < ahora:
            return jsonify({"message": "El código no existe o ya venció"}), 404

        usuario.cuidador.paciente = paciente
        paciente.codigoVinculacion = None
        paciente.codigoVinculacionExpira = None
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se pudo completar la vinculación"}), 409

        return jsonify({
            "message": "Vinculación completada",
            "paciente": {
                "idPaciente": paciente.idPaciente,
                "nombre": paciente.usuario.nombre,
                "apellido": paciente.usuario.apellido
            }
        }), 200

    @staticmethod
    @jwt_required()
    def desvincular_cuidador(id_cuidador):
        usuario = PerfilController._usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        if usuario.paciente is None:
            return jsonify({"message": "Solo el paciente puede quitar a un cuidador"}), 403

        cuidador = next((c for c in usuario.paciente.cuidadores if c.idCuidador == id_cuidador), None)
        if cuidador is None:
            return jsonify({"message": "El cuidador no está vinculado a esta cuenta"}), 404
        cuidador.paciente = None
        db.session.commit()
        return jsonify({"message": "Cuidador desvinculado"}), 200
