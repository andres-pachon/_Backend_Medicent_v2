from flask import Blueprint
from app.Controllers.auth_controller import AuthController
from app.Controllers.medicamento_controller import MedicamentoController
from app.Controllers.toma_controller import TomaController
from app.Controllers.biomarcador_controller import BiomarcadorController
from app.Controllers.tratamiento_controller import TratamientoController
from app.Controllers.password_reset_controller import PasswordResetController

auth_bp = Blueprint(
    "auth",
    __name__
)

auth_bp.route("/login", methods=["POST"])(AuthController.login)

auth_bp.route("/register", methods=["POST"])(AuthController.register)
auth_bp.route("/password/solicitar-restablecimiento", methods=["POST"])(PasswordResetController.solicitar)
auth_bp.route("/password/restablecer", methods=["POST"])(PasswordResetController.restablecer)
auth_bp.route("/medicamentos", methods=["GET"])(MedicamentoController.get_medicamentos)
auth_bp.route("/medicamentos/opciones", methods=["GET"])(MedicamentoController.get_opciones)
auth_bp.route("/medicamentos", methods=["POST"])(MedicamentoController.crear_medicamento)
auth_bp.route("/proximaToma", methods=["GET"])(MedicamentoController.proxima_toma)
auth_bp.route("/tratamientos", methods=["GET"])(TratamientoController.listar)
auth_bp.route("/medicamentos/<int:id_medicamento>", methods=["PUT"])(MedicamentoController.actualizar_horario)
auth_bp.route("/medicamentos/<int:id_medicamento>", methods=["DELETE"])(MedicamentoController.eliminar_medicamento)

auth_bp.route("/tomas", methods=["GET"])(TomaController.get_tomas)        
auth_bp.route("/tomas", methods=["POST"])(TomaController.crear_toma)
auth_bp.route("/tomas/<int:id_toma>", methods=["DELETE"])(TomaController.eliminar_toma)

auth_bp.route("/biomarcadores", methods=["GET"])(BiomarcadorController.get_biomarcadores)
auth_bp.route("/biomarcadores", methods=["POST"])(BiomarcadorController.crear_biomarcador)
