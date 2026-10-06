from flask import Blueprint
from app.Controllers.auth_controller import AuthController
from app.Controllers.medicamento_controller import MedicamentoController
from app.Controllers.toma_controller import TomaController
from app.Controllers.biomarcador_controller import BiomarcadorController

auth_bp = Blueprint(
    "auth",
    __name__
)

auth_bp.route("/login", methods=["POST"])(AuthController.login)

auth_bp.route("/register", methods=["POST"])(AuthController.register)
auth_bp.route("/medicamentos", methods=["GET"])(MedicamentoController.get_medicamentos)
auth_bp.route("/medicamentos", methods=["POST"])(MedicamentoController.crear_medicamento) 

auth_bp.route("/tomas", methods=["GET"])(TomaController.get_tomas)        
auth_bp.route("/tomas", methods=["POST"])(TomaController.crear_toma) 

auth_bp.route("/biomarcadores", methods=["GET"])(BiomarcadorController.get_biomarcadores)
auth_bp.route("/biomarcadores", methods=["POST"])(BiomarcadorController.crear_biomarcador)