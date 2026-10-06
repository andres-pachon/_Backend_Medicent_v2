from flask import request, jsonify
from app.Services.adherencia_service import AdherenciaService

class AdherenciaController:

    @staticmethod
    def generar_reporte():
        data = request.get_json() or {}

        # Validar campos obligatorios en el JSON
        campos = ['idTratamiento', 'fechaInicio', 'fechaFin']
        for campo in campos:
            if campo not in data:
                return jsonify({"error": f"El campo '{campo}' es requerido"}), 400

        resultado, status = AdherenciaService.calcular_adherencia_tratamiento(
            id_tratamiento=data['idTratamiento'],
            fecha_inicio_str=data['fechaInicio'],
            fecha_fin_str=data['fechaFin']
        )
        return jsonify(resultado), status

    @staticmethod
    def listar_por_tratamiento(id_tratamiento):
        resultado, status = AdherenciaService.listar_reportes_tratamiento(id_tratamiento)
        return jsonify(resultado), status

    @staticmethod
    def obtener_ultimo_paciente(id_paciente):
        resultado, status = AdherenciaService.obtener_ultimo_reporte_paciente(id_paciente)
        return jsonify(resultado), status
    