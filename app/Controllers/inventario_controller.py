from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.Services.inventario_service import InventarioService
from app.Services.paciente_service import obtener_paciente_actual, obtener_usuario_actual
from app.models.medicamento import Medicamento
from app.models.tratamiento import Tratamiento


class InventarioController:
    @staticmethod
    @jwt_required()
    def listar(id_usuario=None):
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409
        if id_usuario is not None and id_usuario not in (usuario.idUsuario, paciente.idUsuario):
            return jsonify({"message": "No puedes consultar el inventario de otra cuenta"}), 403

        resultado, status = InventarioService.obtener_inventario_usuario(paciente.idUsuario)
        return jsonify(resultado), status

    @staticmethod
    @jwt_required()
    def recargar():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        data = request.get_json(silent=True) or {}
        campos = ['cantidad']
        faltantes = [campo for campo in campos if campo not in data]
        id_medicamento_recibido = data.get('idMedicamento', data.get('id_medicamento'))
        if id_medicamento_recibido is None:
            faltantes.append('idMedicamento')
        if faltantes:
            return jsonify({"error": "Faltan campos requeridos", "campos": faltantes}), 400
        try:
            cantidad = int(data['cantidad'])
            id_medicamento = int(id_medicamento_recibido)
        except (TypeError, ValueError):
            return jsonify({"error": "El medicamento y la cantidad deben ser números enteros"}), 400
        if cantidad <= 0 or id_medicamento <= 0:
            return jsonify({"error": "El medicamento y la cantidad deben ser mayores a cero"}), 400

        medicamento = Medicamento.query.join(Tratamiento).filter(
            Medicamento.idMedicamento == id_medicamento,
            Tratamiento.idPaciente == paciente.idPaciente
        ).first()
        if medicamento is None:
            return jsonify({"error": "El medicamento no pertenece al tratamiento de esta cuenta"}), 404

        try:
            resultado, status = InventarioService.recargar_stock(
                id_usuario=paciente.idUsuario,
                id_medicamento=id_medicamento,
                cantidad_a_sumar=cantidad,
                fecha_vencimiento=data.get('fecha_vencimiento')
            )
        except ValueError:
            return jsonify({"error": "La fecha de vencimiento debe tener el formato AAAA-MM-DD"}), 400
        return jsonify(resultado), status
