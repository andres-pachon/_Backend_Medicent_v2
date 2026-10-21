from flask import Blueprint
from app.Controllers.adherencia_controller import AdherenciaController

adherencia_bp = Blueprint('adherencia_bp', __name__)

adherencia_bp.route('/generar', methods=['POST'])(AdherenciaController.generar_reporte)
adherencia_bp.route('/tratamiento/<int:id_tratamiento>', methods=['GET'])(AdherenciaController.listar_por_tratamiento)
adherencia_bp.route('/ultimo', methods=['GET'])(AdherenciaController.obtener_ultimo_paciente)
# Compatibilidad con clientes antiguos; el controlador compara el ID con el usuario autenticado.
adherencia_bp.route('/paciente/<int:id_paciente>/ultimo', methods=['GET'])(AdherenciaController.obtener_ultimo_paciente)