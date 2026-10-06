from flask import Blueprint
from app.Controllers.inventario_controller import InventarioController

inventario_bp = Blueprint('inventario_bp', __name__)

# Listar inventario de un paciente
inventario_bp.route('/<int:id_paciente>', methods=['GET'])(InventarioController.listar)

# Recargar stock de medicamento
inventario_bp.route('/recargar', methods=['POST'])(InventarioController.recargar)