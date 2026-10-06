from app.models.usuario import Usuario
from app.database.database import db, bcrypt

class AuthService:

    @staticmethod
    def login(email, password):
        usuario = Usuario.query.filter_by(correo=email).first()

        if not usuario:
            return None
            
        if not bcrypt.check_password_hash(usuario.password, password):
            return None
        
        return usuario

    @staticmethod
    def register(nombre, apellido, documento, correo, telefono, fechaNacimiento, password, idTipoDocumento):
        
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
            fechaNacimiento=fechaNacimiento,
            password=password_encriptada,
            idTipoDocumento=idTipoDocumento
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        return nuevo_usuario, None