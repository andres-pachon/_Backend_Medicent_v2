from flask_jwt_extended import get_jwt_identity

from app.database.database import db
from app.models.usuario import Usuario


def obtener_usuario_actual():
    try:
        id_usuario = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    return db.session.get(Usuario, id_usuario)


def obtener_paciente_actual():
    usuario = obtener_usuario_actual()
    if usuario is None:
        return None
    if usuario.paciente is not None:
        return usuario.paciente
    if usuario.cuidador is not None:
        return usuario.cuidador.paciente
    return None
