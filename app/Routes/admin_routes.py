from flask import Blueprint

from app.Controllers.admin_controller import AdminController


admin_bp = Blueprint("admin", __name__)

admin_bp.route("/usuarios", methods=["GET"])(AdminController.listar_usuarios)
admin_bp.route("/administradores", methods=["POST"])(AdminController.crear_administrador)
admin_bp.route("/resumen", methods=["GET"])(AdminController.resumen)
admin_bp.route("/medicamentos/resumen", methods=["GET"])(AdminController.resumen_medicamentos)
admin_bp.route("/biomarcadores/resumen", methods=["GET"])(AdminController.resumen_biomarcadores)
admin_bp.route("/usuarios/<int:id_usuario>", methods=["PUT"])(AdminController.actualizar_usuario)
admin_bp.route("/usuarios/<int:id_usuario>/estado", methods=["PATCH"])(AdminController.cambiar_estado_usuario)
admin_bp.route("/usuarios/<int:id_usuario>", methods=["DELETE"])(AdminController.eliminar_usuario)
