from datetime import date

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.database.database import bcrypt, db
from app.models.administrador import Administrador
from app.models.biomarcador import Biomarcador
from app.models.medicamento import Medicamento
from app.models.tratamiento import Tratamiento
from app.models.tipo_medicamento import TipoMedicamento
from app.models.via_administracion import ViaAdministracion
from app.models.tipo_documento import TipoDocumento
from app.models.usuario import Usuario


class AdminController:
    @staticmethod
    def _solicitud_admin():
        try:
            id_usuario = int(get_jwt_identity())
        except (TypeError, ValueError):
            return None

        usuario = db.session.get(Usuario, id_usuario)
        if usuario is None or usuario.administrador is None:
            return None
        return usuario

    @staticmethod
    @jwt_required()
    def listar_usuarios():
        if AdminController._solicitud_admin() is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403

        usuarios = Usuario.query.order_by(Usuario.idUsuario.asc()).all()
        return jsonify([
            {
                "id": usuario.idUsuario,
                "idUsuario": usuario.idUsuario,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "correo": usuario.correo,
                "telefono": usuario.telefono,
                "documento": usuario.documento,
                "rol": "admin" if usuario.administrador is not None else "usuario",
                "perfil": "paciente" if usuario.paciente is not None else ("cuidador" if usuario.cuidador is not None else None),
                "activo": bool(usuario.activo)
            }
            for usuario in usuarios
        ]), 200

    @staticmethod
    @jwt_required()
    def crear_administrador():
        if AdminController._solicitud_admin() is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403

        data = request.get_json(silent=True) or {}
        campos_requeridos = (
            "nombre",
            "apellido",
            "correo",
            "documento",
            "password",
            "fechaNacimiento",
            "idTipoDocumento"
        )
        faltantes = [campo for campo in campos_requeridos if not data.get(campo)]
        if faltantes:
            return jsonify({
                "message": "Faltan campos obligatorios",
                "campos": faltantes
            }), 400

        correo = str(data["correo"]).strip().lower()
        documento = str(data["documento"]).strip()
        password = str(data["password"])
        if len(password) < 6:
            return jsonify({"message": "La contraseña debe tener al menos 6 caracteres"}), 400

        try:
            fecha_nacimiento = date.fromisoformat(str(data["fechaNacimiento"]))
            id_tipo_documento = int(data["idTipoDocumento"])
        except (TypeError, ValueError):
            return jsonify({"message": "La fecha o el tipo de documento no son válidos"}), 400

        if Usuario.query.filter_by(correo=correo).first():
            return jsonify({"message": "El correo ya está registrado"}), 409
        if Usuario.query.filter_by(documento=documento).first():
            return jsonify({"message": "El documento ya está registrado"}), 409
        if db.session.get(TipoDocumento, id_tipo_documento) is None:
            return jsonify({"message": "El tipo de documento no existe"}), 400

        nuevo_usuario = Usuario(
            nombre=str(data["nombre"]).strip(),
            apellido=str(data["apellido"]).strip(),
            correo=correo,
            documento=documento,
            telefono=str(data.get("telefono", "")).strip() or None,
            fechaNacimiento=fecha_nacimiento,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            idTipoDocumento=id_tipo_documento
        )
        try:
            db.session.add(nuevo_usuario)
            db.session.flush()

            perfil_admin = Administrador(
                nombre=nuevo_usuario.nombre,
                apellido=nuevo_usuario.apellido,
                correo=nuevo_usuario.correo,
                telefono=nuevo_usuario.telefono,
                idUsuario=nuevo_usuario.idUsuario
            )
            db.session.add(perfil_admin)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se pudo crear el administrador; revisa los datos ingresados"}), 409
        except Exception:
            db.session.rollback()
            return jsonify({"message": "Ocurrió un error al crear el administrador"}), 500

        return jsonify({
            "message": "Administrador creado correctamente",
            "user": {
                "id": nuevo_usuario.idUsuario,
                "idUsuario": nuevo_usuario.idUsuario,
                "nombre": nuevo_usuario.nombre,
                "apellido": nuevo_usuario.apellido,
                "correo": nuevo_usuario.correo,
                "rol": "admin"
            }
        }), 201

    @staticmethod
    @jwt_required()
    def resumen():
        if AdminController._solicitud_admin() is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403

        return jsonify({
            "usuarios": Usuario.query.count(),
            "medicamentos": Medicamento.query.count(),
            "biomarcadores": Biomarcador.query.count()
        }), 200

    @staticmethod
    @jwt_required()
    def resumen_medicamentos():
        if AdminController._solicitud_admin() is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403

        tipos = db.session.query(
            TipoMedicamento.nombre, db.func.count(Medicamento.idMedicamento)
        ).outerjoin(Medicamento, Medicamento.idTipoMedicamento == TipoMedicamento.idTipoMedicamento).group_by(
            TipoMedicamento.idTipoMedicamento, TipoMedicamento.nombre
        ).order_by(TipoMedicamento.nombre).all()
        vias = db.session.query(
            ViaAdministracion.nombre, db.func.count(Medicamento.idMedicamento)
        ).outerjoin(Medicamento, Medicamento.idViaAdministracion == ViaAdministracion.idViaAdministracion).group_by(
            ViaAdministracion.idViaAdministracion, ViaAdministracion.nombre
        ).order_by(ViaAdministracion.nombre).all()

        return jsonify({
            "total": Medicamento.query.count(),
            "tratamientosActivos": Tratamiento.query.filter(Tratamiento.fechaFin >= date.today()).count(),
            "porTipo": [{"nombre": nombre, "cantidad": cantidad} for nombre, cantidad in tipos],
            "porVia": [{"nombre": nombre, "cantidad": cantidad} for nombre, cantidad in vias]
        }), 200

    @staticmethod
    @jwt_required()
    def resumen_biomarcadores():
        if AdminController._solicitud_admin() is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403

        tipos = db.session.query(
            Biomarcador.tipo, db.func.count(Biomarcador.idBiomarcador)
        ).group_by(Biomarcador.tipo).order_by(Biomarcador.tipo).all()
        return jsonify({
            "total": Biomarcador.query.count(),
            "porTipo": [{"tipo": tipo, "cantidad": cantidad} for tipo, cantidad in tipos]
        }), 200

    @staticmethod
    @jwt_required()
    def actualizar_usuario(id_usuario):
        if AdminController._solicitud_admin() is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403

        usuario = db.session.get(Usuario, id_usuario)
        if usuario is None:
            return jsonify({"message": "Usuario no encontrado"}), 404

        data = request.get_json(silent=True) or {}
        campos = ("nombre", "apellido", "correo", "telefono", "documento")
        valores = {}
        for campo in campos:
            if campo not in data:
                continue
            valor = str(data[campo] or "").strip()
            if campo != "telefono" and not valor:
                return jsonify({"message": f"El campo {campo} es obligatorio"}), 400
            valores[campo] = valor or None

        correo = valores.get("correo")
        if correo:
            valores["correo"] = correo.lower()
            duplicado = Usuario.query.filter(
                Usuario.correo == valores["correo"], Usuario.idUsuario != id_usuario
            ).first()
            if duplicado:
                return jsonify({"message": "El correo ya está registrado"}), 409

        documento = valores.get("documento")
        if documento:
            duplicado = Usuario.query.filter(
                Usuario.documento == documento, Usuario.idUsuario != id_usuario
            ).first()
            if duplicado:
                return jsonify({"message": "El documento ya está registrado"}), 409

        password = data.get("password")
        if password:
            if len(str(password)) < 6:
                return jsonify({"message": "La contraseña debe tener al menos 6 caracteres"}), 400
            usuario.password = bcrypt.generate_password_hash(str(password)).decode("utf-8")

        for campo, valor in valores.items():
            setattr(usuario, campo, valor)

        for perfil in (usuario.administrador, usuario.cuidador):
            if perfil is not None:
                for campo in ("nombre", "apellido", "correo", "telefono"):
                    if campo in valores:
                        setattr(perfil, campo, valores[campo])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se pudo actualizar el usuario; revisa correo y documento"}), 409

        return jsonify({"message": "Usuario actualizado correctamente"}), 200

    @staticmethod
    @jwt_required()
    def cambiar_estado_usuario(id_usuario):
        administrador_solicitante = AdminController._solicitud_admin()
        if administrador_solicitante is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403
        if administrador_solicitante.idUsuario == id_usuario:
            return jsonify({"message": "No puedes cambiar el estado de la cuenta con la que has iniciado sesión"}), 409

        usuario = db.session.get(Usuario, id_usuario)
        if usuario is None:
            return jsonify({"message": "Usuario no encontrado"}), 404
        if usuario.administrador is not None:
            return jsonify({"message": "No se permite cambiar el estado de otra cuenta administradora"}), 409

        data = request.get_json(silent=True) or {}
        activo = data.get("activo")
        if not isinstance(activo, bool):
            return jsonify({"message": "El campo activo debe ser verdadero o falso"}), 400

        usuario.activo = activo
        db.session.commit()
        return jsonify({
            "message": "Cuenta reactivada" if activo else "Cuenta desactivada",
            "activo": usuario.activo
        }), 200

    @staticmethod
    @jwt_required()
    def eliminar_usuario(id_usuario):
        administrador_solicitante = AdminController._solicitud_admin()
        if administrador_solicitante is None:
            return jsonify({"message": "Se requieren permisos de administrador"}), 403
        if administrador_solicitante.idUsuario == id_usuario:
            return jsonify({"message": "No puedes eliminar la cuenta con la que has iniciado sesión"}), 409

        usuario = db.session.get(Usuario, id_usuario)
        if usuario is None:
            return jsonify({"message": "Usuario no encontrado"}), 404
        if usuario.administrador is not None:
            return jsonify({"message": "No se permite eliminar cuentas de administrador desde esta pantalla"}), 409
        if usuario.paciente is not None or usuario.cuidador is not None:
            return jsonify({"message": "No se puede eliminar una cuenta que ya tiene un perfil de salud. Conserva su historial"}), 409

        try:
            db.session.delete(usuario)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "No se puede eliminar esta cuenta porque tiene información asociada"}), 409
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
