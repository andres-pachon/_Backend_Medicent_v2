from flask import Blueprint

from app.Controllers.perfil_controller import PerfilController


perfil_bp = Blueprint("perfil", __name__)

perfil_bp.route("", methods=["GET"])(PerfilController.obtener_perfil)
perfil_bp.route("", methods=["PUT"])(PerfilController.actualizar_perfil)
perfil_bp.route("/paciente", methods=["POST"])(PerfilController.crear_perfil_paciente)
perfil_bp.route("/cuidador", methods=["POST"])(PerfilController.crear_perfil_cuidador)
perfil_bp.route("/vinculacion", methods=["GET"])(PerfilController.obtener_vinculacion)
perfil_bp.route("/vinculacion/codigo", methods=["POST"])(PerfilController.generar_codigo_vinculacion)
perfil_bp.route("/vinculacion/canjear", methods=["POST"])(PerfilController.canjear_codigo_vinculacion)
perfil_bp.route("/vinculacion/cuidadores/<int:id_cuidador>", methods=["DELETE"])(PerfilController.desvincular_cuidador)
