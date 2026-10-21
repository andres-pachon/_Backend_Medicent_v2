from datetime import date, datetime

from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.database.database import db
from app.models.biomarcador import Biomarcador
from app.Services.paciente_service import obtener_paciente_actual, obtener_usuario_actual


class BiomarcadorController:
    @staticmethod
    @jwt_required()
    def get_biomarcadores():
        paciente = obtener_paciente_actual()
        if paciente is None:
            usuario = obtener_usuario_actual()
            if usuario is not None and usuario.cuidador is not None:
                return jsonify([]), 200
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        consulta = Biomarcador.query.filter_by(idPaciente=paciente.idPaciente)
        fecha = request.args.get('fecha')
        if fecha:
            try:
                consulta = consulta.filter_by(fecha=date.fromisoformat(fecha))
            except ValueError:
                return jsonify({"message": "La fecha debe tener el formato AAAA-MM-DD"}), 400

        biomarcadores = consulta.order_by(Biomarcador.fecha.desc(), Biomarcador.hora.desc()).all()
        return jsonify([
            {
                "id": biomarcador.idBiomarcador,
                "idBiomarcador": biomarcador.idBiomarcador,
                "tipo": biomarcador.tipo,
                "nombre": biomarcador.nombre,
                "valor": biomarcador.valor,
                "unidad": biomarcador.unidad,
                "fecha": str(biomarcador.fecha),
                "hora": str(biomarcador.hora),
                "estado": biomarcador.estado,
                "notas": biomarcador.notas
            }
            for biomarcador in biomarcadores
        ]), 200

    @staticmethod
    @jwt_required()
    def crear_biomarcador():
        data = request.get_json(silent=True) or {}
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        try:
            nuevo = Biomarcador(
                tipo=data.get('tipo'),
                nombre=data.get('nombre'),
                valor=float(data.get('valor')),
                unidad=data.get('unidad', ''),
                fecha=date.fromisoformat(data.get('fecha')),
                hora=datetime.strptime(data.get('hora'), '%H:%M').time(),
                estado=data.get('estado', 'bueno'),
                notas=data.get('notas', ''),
                idPaciente=paciente.idPaciente
            )
            db.session.add(nuevo)
            db.session.commit()
            return jsonify({"message": "Biomarcador registrado"}), 201
        except (TypeError, ValueError) as error:
            db.session.rollback()
            return jsonify({"message": f"Los datos del biomarcador no son válidos: {error}"}), 400
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": str(error)}), 400
