from datetime import date, datetime

from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.database.database import db
from app.models.inventario_model import InventarioPersonal
from app.models.medicamento import Medicamento
from app.models.toma import Toma
from app.models.tratamiento import Tratamiento
from app.Services.inventario_service import InventarioService
from app.Services.paciente_service import obtener_paciente_actual, obtener_usuario_actual


class TomaController:
    @staticmethod
    @jwt_required()
    def crear_toma():
        data = request.get_json(silent=True) or {}
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        try:
            id_medicamento = int(data.get('idMedicamento'))
        except (TypeError, ValueError):
            return jsonify({"message": "El medicamento indicado no es válido"}), 400

        medicamento = Medicamento.query.join(Tratamiento).filter(
            Medicamento.idMedicamento == id_medicamento,
            Tratamiento.idPaciente == paciente.idPaciente
        ).first()
        if medicamento is None:
            return jsonify({"message": "El medicamento no pertenece al tratamiento de esta cuenta"}), 404

        try:
            nueva_toma = Toma(
                fecha=date.fromisoformat(data.get('fecha')),
                hora=datetime.strptime(data.get('hora'), '%H:%M').time(),
                dosis=data.get('dosis'),
                nota=data.get('nota', ''),
                estado=data.get('estado', 'tomado'),
                idMedicamento=id_medicamento,
                idPaciente=paciente.idPaciente
            )
            db.session.add(nueva_toma)

            detalle_inventario = None
            if nueva_toma.estado.lower() in ('tomado', 'tomada'):
                exito, detalle = InventarioService.descontar_stock(
                    id_usuario=paciente.idUsuario,
                    id_medicamento=nueva_toma.idMedicamento,
                    cantidad=1
                )
                if exito:
                    detalle_inventario = detalle

            db.session.commit()
            respuesta = {"message": "Toma registrada exitosamente"}
            if detalle_inventario:
                respuesta["inventario"] = detalle_inventario
            return jsonify(respuesta), 201
        except (TypeError, ValueError) as error:
            db.session.rollback()
            return jsonify({"message": f"Los datos de la toma no son válidos: {error}"}), 400
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": str(error)}), 400

    @staticmethod
    @jwt_required()
    def eliminar_toma(id_toma):
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        toma = Toma.query.filter_by(idToma=id_toma, idPaciente=paciente.idPaciente).first()
        if toma is None:
            return jsonify({"message": "Toma no encontrada para esta cuenta"}), 404

        try:
            if toma.estado and toma.estado.lower() in ('tomado', 'tomada'):
                inventario = InventarioPersonal.query.filter_by(
                    id_usuario=paciente.idUsuario,
                    id_medicamento=toma.idMedicamento
                ).first()
                if inventario is not None:
                    inventario.cantidad_actual += 1
            db.session.delete(toma)
            db.session.commit()
            return jsonify({"message": "Toma eliminada"}), 200
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": f"No se pudo eliminar la toma: {error}"}), 400

    @staticmethod
    @jwt_required()
    def get_tomas():
        paciente = obtener_paciente_actual()
        if paciente is None:
            usuario = obtener_usuario_actual()
            if usuario is not None and usuario.cuidador is not None:
                return jsonify([]), 200
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        consulta = Toma.query.filter_by(idPaciente=paciente.idPaciente)
        fecha = request.args.get('fecha')
        if fecha:
            try:
                consulta = consulta.filter_by(fecha=date.fromisoformat(fecha))
            except ValueError:
                return jsonify({"message": "La fecha debe tener el formato AAAA-MM-DD"}), 400

        tomas = consulta.order_by(Toma.fecha.desc(), Toma.hora.desc()).all()
        return jsonify([
            {
                "id": toma.idToma,
                "idToma": toma.idToma,
                "fecha": str(toma.fecha),
                "hora": str(toma.hora),
                "dosis": toma.dosis,
                "nota": toma.nota,
                "estado": toma.estado,
                "medicamento": toma.medicamento.nombre if toma.medicamento else '',
                "via": toma.medicamento.via_administracion.nombre if toma.medicamento and toma.medicamento.via_administracion else ''
            }
            for toma in tomas
        ]), 200
