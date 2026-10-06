from flask import Blueprint
from app.Controllers.adherencia_controller import AdherenciaController

adherencia_bp = Blueprint('adherencia_bp', __name__)

# POST: Calcular y guardar un reporte
adherencia_bp.route('/generar', methods=['POST'])(AdherenciaController.generar_reporte)

# GET: Listar reportes de un tratamiento específico
adherencia_bp.route('/tratamiento/<int:id_tratamiento>', methods=['GET'])(AdherenciaController.listar_por_tratamiento)

# GET: Obtener el reporte más reciente de un paciente
adherencia_bp.route('/paciente/<int:id_paciente>/ultimo', methods=['GET'])(AdherenciaController.obtener_ultimo_paciente)