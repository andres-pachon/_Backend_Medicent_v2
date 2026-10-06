from flask import Blueprint
from app.Controllers.auth_controller import AuthController
from app.Controllers.medicamento_controller import MedicamentoController
from app.Controllers.toma_controller import TomaController
from app.Controllers.biomarcador_controller import BiomarcadorController
from app.Controllers.admin_controller import AdminController

auth_bp = Blueprint("auth", __name__)

# ========== AUTENTICACIÓN ==========
auth_bp.route("/login", methods=["POST"])(AuthController.login)
auth_bp.route("/register", methods=["POST"])(AuthController.register)

# ========== RUTAS NORMALES ==========
auth_bp.route("/medicamentos", methods=["GET"])(MedicamentoController.get_medicamentos)
auth_bp.route("/medicamentos", methods=["POST"])(MedicamentoController.crear_medicamento)

auth_bp.route("/tomas", methods=["GET"])(TomaController.get_tomas)
auth_bp.route("/tomas", methods=["POST"])(TomaController.crear_toma)

auth_bp.route("/biomarcadores", methods=["GET"])(BiomarcadorController.get_biomarcadores)
auth_bp.route("/biomarcadores", methods=["POST"])(BiomarcadorController.crear_biomarcador)

# ========== RUTAS DE ADMINISTRADOR ==========
# Usuarios
auth_bp.route("/admin/usuarios", methods=["GET"], endpoint="admin_get_usuarios")(AdminController.get_usuarios)
auth_bp.route("/admin/usuarios/<int:id>", methods=["GET"], endpoint="admin_get_usuario")(AdminController.get_usuario)
auth_bp.route("/admin/usuarios/<int:id>", methods=["PUT"], endpoint="admin_actualizar_usuario")(AdminController.actualizar_usuario)
auth_bp.route("/admin/usuarios/<int:id>", methods=["DELETE"], endpoint="admin_eliminar_usuario")(AdminController.eliminar_usuario)

# Medicamentos
auth_bp.route("/admin/medicamentos", methods=["GET"], endpoint="admin_get_medicamentos")(AdminController.get_medicamentos)
auth_bp.route("/admin/medicamentos/<int:id>", methods=["PUT"], endpoint="admin_actualizar_medicamento")(AdminController.actualizar_medicamento)
auth_bp.route("/admin/medicamentos/<int:id>", methods=["DELETE"], endpoint="admin_eliminar_medicamento")(AdminController.eliminar_medicamento)

# Biomarcadores
auth_bp.route("/admin/biomarcadores", methods=["GET"], endpoint="admin_get_biomarcadores")(AdminController.get_biomarcadores)
auth_bp.route("/admin/biomarcadores/<int:id>", methods=["PUT"], endpoint="admin_actualizar_biomarcador")(AdminController.actualizar_biomarcador)
auth_bp.route("/admin/biomarcadores/<int:id>", methods=["DELETE"], endpoint="admin_eliminar_biomarcador")(AdminController.eliminar_biomarcador)