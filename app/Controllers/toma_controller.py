from flask import request, jsonify
from app.models.toma import Toma
from app.database.database import db
from datetime import datetime, date
from app.Services.inventario_service import InventarioService


class TomaController:

    @staticmethod
    def crear_toma():
        data = request.get_json() or {}
        try:
            estado_toma = data.get('estado', 'tomado')
            id_medicamento = data.get('idMedicamento')
            id_paciente = data.get('idPaciente')

            nueva_toma = Toma(
                fecha=date.fromisoformat(data.get('fecha')),
                hora=datetime.strptime(data.get('hora'), '%H:%M').time(),
                dosis=data.get('dosis'),
                nota=data.get('nota', ''),
                estado=estado_toma,
                idMedicamento=id_medicamento,
                idPaciente=id_paciente
            )
            db.session.add(nueva_toma)

            detalle_inventario = None
            if estado_toma.lower() in ['tomado', 'tomada']:
                exito, detalle = InventarioService.descontar_stock(
                    id_paciente=id_paciente,
                    id_medicamento=id_medicamento,
                    cantidad=1
                )
                if exito:
                    detalle_inventario = detalle

            db.session.commit()

            respuesta = {"message": "Toma registrada exitosamente"}
            if detalle_inventario:
                respuesta["inventario"] = detalle_inventario

            return jsonify(respuesta), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400

    @staticmethod
    def get_tomas():
        fecha = request.args.get('fecha')
        if fecha:
            tomas = Toma.query.filter_by(fecha=date.fromisoformat(fecha)).all()
        else:
            tomas = Toma.query.all()

        return jsonify([
            {
                "id": t.idToma,
                "fecha": str(t.fecha),
                "hora": str(t.hora),
                "dosis": t.dosis,
                "nota": t.nota,
                "estado": t.estado,
                "medicamento": t.medicamento.nombre if t.medicamento else '',
                "via": t.medicamento.idViaAdministracion if t.medicamento else ''
            }
            for t in tomas
        ]), 200