from flask import jsonify
from flask_jwt_extended import jwt_required

from app.models.tratamiento import Tratamiento
from app.Services.paciente_service import obtener_paciente_actual, obtener_usuario_actual


class TratamientoController:
    @staticmethod
    @jwt_required()
    def listar():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            if usuario.cuidador is not None:
                return jsonify([]), 200
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        tratamientos = Tratamiento.query.filter_by(
            idPaciente=paciente.idPaciente
        ).order_by(Tratamiento.fechaInicio.desc()).all()
        return jsonify([
            {
                "id": tratamiento.idTratamiento,
                "idTratamiento": tratamiento.idTratamiento,
                "fechaInicio": tratamiento.fechaInicio.isoformat(),
                "fechaFin": tratamiento.fechaFin.isoformat(),
                "medicamentos": [medicamento.nombre for medicamento in tratamiento.medicamentos]
            }
            for tratamiento in tratamientos
        ]), 200
