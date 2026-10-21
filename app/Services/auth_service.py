from datetime import date

from sqlalchemy.exc import IntegrityError

from app.models.usuario import Usuario
from app.models.tipo_documento import TipoDocumento
from app.database.database import db, bcrypt

class AuthService:

    @staticmethod
    def login(email, password):
        usuario = Usuario.query.filter_by(correo=email).first()

        if not usuario or not usuario.activo:
            return None
            
        if not bcrypt.check_password_hash(usuario.password, password):
            return None
        
        return usuario

    @staticmethod
    def register(nombre, apellido, documento, correo, telefono, fechaNacimiento, password, idTipoDocumento):
        nombre = str(nombre or "").strip()
        apellido = str(apellido or "").strip()
        documento = str(documento or "").strip()
        correo = str(correo or "").strip().lower()
        password = str(password or "")

        if not all((nombre, apellido, documento, correo, fechaNacimiento, password, idTipoDocumento)):
            return None, "Faltan campos obligatorios"
        if len(password) < 6:
            return None, "La contraseña debe tener al menos 6 caracteres"

        try:
            fecha_nacimiento = date.fromisoformat(str(fechaNacimiento))
            id_tipo_documento = int(idTipoDocumento)
        except (TypeError, ValueError):
            return None, "La fecha de nacimiento o el tipo de documento no son válidos"

        if db.session.get(TipoDocumento, id_tipo_documento) is None:
            return None, "El tipo de documento no existe"

        existe_documento = Usuario.query.filter_by(documento=documento).first()
        if existe_documento:
            return None, "El documento ya está registrado"

        existe_email = Usuario.query.filter_by(correo=correo).first()
        if existe_email:
            return None, "El correo ya está registrado"

        password_encriptada = bcrypt.generate_password_hash(password).decode('utf-8')

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            documento=documento,
            correo=correo,
            telefono=telefono,
            fechaNacimiento=fecha_nacimiento,
            password=password_encriptada,
            idTipoDocumento=id_tipo_documento
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None, "El correo o el documento ya están registrados"
        except Exception:
            db.session.rollback()
            return None, "No se pudo registrar el usuario"

        return nuevo_usuario, None
