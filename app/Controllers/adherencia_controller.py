from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.Services.adherencia_service import AdherenciaService
from app.Services.paciente_service import obtener_paciente_actual, obtener_usuario_actual
from app.models.tratamiento import Tratamiento


class AdherenciaController:
    @staticmethod
    @jwt_required()
    def generar_reporte():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        data = request.get_json(silent=True) or {}
        campos = ['idTratamiento', 'fechaInicio', 'fechaFin']
        faltantes = [campo for campo in campos if not data.get(campo)]
        if faltantes:
            return jsonify({"error": "Faltan campos requeridos", "campos": faltantes}), 400
        try:
            id_tratamiento = int(data['idTratamiento'])
        except (TypeError, ValueError):
            return jsonify({"error": "El tratamiento indicado no es válido"}), 400

        tratamiento = Tratamiento.query.filter_by(
            idTratamiento=id_tratamiento,
            idPaciente=paciente.idPaciente
        ).first()
        if tratamiento is None:
            return jsonify({"error": "Tratamiento no encontrado para esta cuenta"}), 404

        resultado, status = AdherenciaService.calcular_adherencia_tratamiento(
            id_tratamiento=id_tratamiento,
            fecha_inicio_str=data['fechaInicio'],
            fecha_fin_str=data['fechaFin']
        )
        return jsonify(resultado), status

    @staticmethod
    @jwt_required()
    def listar_por_tratamiento(id_tratamiento):
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        tratamiento = Tratamiento.query.filter_by(
            idTratamiento=id_tratamiento,
            idPaciente=paciente.idPaciente
        ).first()
        if tratamiento is None:
            return jsonify({"error": "Tratamiento no encontrado para esta cuenta"}), 404

        resultado, status = AdherenciaService.listar_reportes_tratamiento(id_tratamiento)
        return jsonify(resultado), status

    @staticmethod
    @jwt_required()
    def obtener_ultimo_paciente(id_paciente=None):
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409
        if id_paciente is not None and id_paciente != paciente.idPaciente:
            return jsonify({"error": "No puedes consultar reportes de otro paciente"}), 403

        resultado, status = AdherenciaService.obtener_ultimo_reporte_paciente(paciente.idPaciente)
        return jsonify(resultado), status