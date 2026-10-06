from flask import request, jsonify
from app.Services.inventario_service import InventarioService

class InventarioController:

    @staticmethod
    def listar(id_paciente):
        resultado, status = InventarioService.obtener_inventario_paciente(id_paciente)
        return jsonify(resultado), status

    @staticmethod
    def recargar():
        data = request.get_json() or {}
        campos = ['id_paciente', 'id_medicamento', 'cantidad']
        for c in campos:
            if c not in data:
                return jsonify({"error": f"El campo '{c}' es requerido"}), 400

        resultado, status = InventarioService.recargar_stock(
            id_paciente=data['id_paciente'],
            id_medicamento=data['id_medicamento'],
            cantidad_a_sumar=int(data['cantidad']),
            fecha_vencimiento=data.get('fecha_vencimiento')
        )
        return jsonify(resultado), status