from flask import request, jsonify
from app.Middlewares.auth_middleware import admin_required
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.medicamento import Medicamento
from app.models.biomarcador import Biomarcador
from app.database.database import db, bcrypt
from datetime import datetime, date

class AdminController:

    # ==========================================
    # USUARIOS
    # ==========================================

    @staticmethod
    @admin_required
    def get_usuarios():
        usuarios = Usuario.query.all()
        lista = []
        for u in usuarios:
            es_admin = Administrador.query.filter_by(idUsuario=u.idUsuario).first() is not None
            lista.append({
                "id": u.idUsuario,
                "nombre": u.nombre,
                "apellido": u.apellido,
                "documento": u.documento,
                "correo": u.correo,
                "telefono": u.telefono,
                "fechaNacimiento": str(u.fechaNacimiento) if u.fechaNacimiento else None,
                "rol": "admin" if es_admin else "usuario"
            })
        return jsonify(lista), 200

    @staticmethod
    @admin_required
    def get_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"message": "Usuario no encontrado"}), 404

        es_admin = Administrador.query.filter_by(idUsuario=usuario.idUsuario).first() is not None
        return jsonify({
            "id": usuario.idUsuario,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "documento": usuario.documento,
            "correo": usuario.correo,
            "telefono": usuario.telefono,
            "fechaNacimiento": str(usuario.fechaNacimiento) if usuario.fechaNacimiento else None,
            "rol": "admin" if es_admin else "usuario"
        }), 200

    @staticmethod
    @admin_required
    def actualizar_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"message": "Usuario no encontrado"}), 404

        data = request.get_json()

        if "nombre" in data:
            usuario.nombre = data["nombre"]
        if "apellido" in data:
            usuario.apellido = data["apellido"]
        if "correo" in data:
            usuario.correo = data["correo"]
        if "telefono" in data:
            usuario.telefono = data["telefono"]
        if "documento" in data:
            usuario.documento = data["documento"]
        if "password" in data and data["password"]:
            usuario.password = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

        try:
            db.session.commit()
            return jsonify({"message": "Usuario actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400

    @staticmethod
    @admin_required
    def eliminar_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"message": "Usuario no encontrado"}), 404

        # No permitir eliminar al propio admin principal (opcional de seguridad)
        if usuario.correo == "adminmedicent@gmail.com":
            return jsonify({"message": "No se puede eliminar al administrador principal"}), 403

        try:
            db.session.delete(usuario)
            db.session.commit()
            return jsonify({"message": "Usuario eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400

    # ==========================================
    # MEDICAMENTOS
    # ==========================================

    @staticmethod
    @admin_required
    def get_medicamentos():
        medicamentos = Medicamento.query.all()
        lista = []
        for m in medicamentos:
            lista.append({
                "id": m.idMedicamento,
                "nombre": m.nombre,
                "concentracion": m.concentracion,
                "frecuenciaDiaria": m.frecuenciaDiaria,
                "fechaVencimiento": str(m.fechaVencimiento) if m.fechaVencimiento else None
            })
        return jsonify(lista), 200

    @staticmethod
    @admin_required
    def actualizar_medicamento(id):
        medicamento = Medicamento.query.get(id)
        if not medicamento:
            return jsonify({"message": "Medicamento no encontrado"}), 404

        data = request.get_json()

        if "nombre" in data:
            medicamento.nombre = data["nombre"]
        if "concentracion" in data:
            medicamento.concentracion = float(data["concentracion"])
        if "frecuenciaDiaria" in data:
            medicamento.frecuenciaDiaria = int(data["frecuenciaDiaria"])
        if "fechaVencimiento" in data:
            medicamento.fechaVencimiento = date.fromisoformat(data["fechaVencimiento"])

        try:
            db.session.commit()
            return jsonify({"message": "Medicamento actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400

    @staticmethod
    @admin_required
    def eliminar_medicamento(id):
        medicamento = Medicamento.query.get(id)
        if not medicamento:
            return jsonify({"message": "Medicamento no encontrado"}), 404

        try:
            db.session.delete(medicamento)
            db.session.commit()
            return jsonify({"message": "Medicamento eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400

    # ==========================================
    # BIOMARCADORES
    # ==========================================

    @staticmethod
    @admin_required
    def get_biomarcadores():
        bios = Biomarcador.query.all()
        lista = []
        for b in bios:
            lista.append({
                "id": b.idBiomarcador,
                "tipo": b.tipo,
                "nombre": b.nombre,
                "valor": b.valor,
                "unidad": b.unidad,
                "fecha": str(b.fecha),
                "hora": str(b.hora),
                "estado": b.estado,
                "notas": b.notas,
                "idPaciente": b.idPaciente
            })
        return jsonify(lista), 200

    @staticmethod
    @admin_required
    def actualizar_biomarcador(id):
        bio = Biomarcador.query.get(id)
        if not bio:
            return jsonify({"message": "Biomarcador no encontrado"}), 404

        data = request.get_json()

        if "tipo" in data:
            bio.tipo = data["tipo"]
        if "nombre" in data:
            bio.nombre = data["nombre"]
        if "valor" in data:
            bio.valor = float(data["valor"])
        if "unidad" in data:
            bio.unidad = data["unidad"]
        if "estado" in data:
            bio.estado = data["estado"]
        if "notas" in data:
            bio.notas = data["notas"]
        if "fecha" in data:
            bio.fecha = date.fromisoformat(data["fecha"])
        if "hora" in data:
            bio.hora = datetime.strptime(data["hora"], "%H:%M").time()

        try:
            db.session.commit()
            return jsonify({"message": "Biomarcador actualizado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400

    @staticmethod
    @admin_required
    def eliminar_biomarcador(id):
        bio = Biomarcador.query.get(id)
        if not bio:
            return jsonify({"message": "Biomarcador no encontrado"}), 404

        try:
            db.session.delete(bio)
            db.session.commit()
            return jsonify({"message": "Biomarcador eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400