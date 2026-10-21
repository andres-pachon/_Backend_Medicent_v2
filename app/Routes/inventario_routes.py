from flask import Blueprint
from app.Controllers.inventario_controller import InventarioController

inventario_bp = Blueprint('inventario_bp', __name__)

# El inventario pertenece a la cuenta autenticada.
inventario_bp.route('', methods=['GET'])(InventarioController.listar)
# Ruta de compatibilidad: valida que el ID solicitado sea el de la cuenta autenticada.
inventario_bp.route('/<int:id_usuario>', methods=['GET'])(InventarioController.listar)
inventario_bp.route('/recargar', methods=['POST'])(InventarioController.recargar)
