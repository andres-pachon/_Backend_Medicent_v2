from flask import request, jsonify
from flask_jwt_extended import jwt_required
from app.Middlewares.auth_middleware import token_required
from app.models.biomarcador import Biomarcador
from app.database.database import db
from datetime import datetime, date

class BiomarcadorController:

    @staticmethod
    def get_biomarcadores():
        fecha = request.args.get('fecha')
        if fecha:
            bios = Biomarcador.query.filter_by(fecha=date.fromisoformat(fecha)).all()
        else:
            bios = Biomarcador.query.all()

        return jsonify([
            {
                "id": b.idBiomarcador,
                "tipo": b.tipo,
                "nombre": b.nombre,
                "valor": b.valor,
                "unidad": b.unidad,
                "fecha": str(b.fecha),
                "hora": str(b.hora),
                "estado": b.estado,
                "notas": b.notas
            }
            for b in bios
        ]), 200

    @staticmethod
    @jwt_required()
    def crear_biomarcador():
        data = request.get_json()
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
                idPaciente=1
            )
            db.session.add(nuevo)
            db.session.commit()
            return jsonify({"message": "Biomarcador registrado"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400