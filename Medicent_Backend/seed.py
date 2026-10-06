from app import create_app
from app.database.database import db, bcrypt
from app.models.usuario import Usuario
from app.models.administrador import Administrador
from app.models.tipo_documento import TipoDocumento
from datetime import date

app = create_app()

with app.app_context():
    #  Crear tipo de documento si no existe
    tipo_cc = TipoDocumento.query.filter_by(nombre='Cédula de Ciudadanía').first()
    if tipo_cc is None:
        tipo_cc = TipoDocumento(nombre='Cédula de Ciudadanía')
        db.session.add(tipo_cc)
        db.session.commit()
        print("Tipo de documento creado.")

    #  Crear el usuario Admin si no existe
    admin_existente = Usuario.query.filter_by(correo='adminmedicent@gmail.com').first()

    if admin_existente is None:
        admin_usuario = Usuario(
            nombre='Admin',
            apellido='Medicent',
            documento='123456789',
            correo='adminmedicent@gmail.com',
            telefono='3001234567',
            fechaNacimiento=date(2000, 1, 1),
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            idTipoDocumento=tipo_cc.idTipoDocumento
        )
        db.session.add(admin_usuario)
        db.session.commit()
        print("Usuario Admin creado exitosamente.")
    else:
        admin_usuario = admin_existente
        print("El usuario Admin ya existe.")

    # Crear el registro en la tabla Administrador (esto faltaba)
    admin_rol = Administrador.query.filter_by(idUsuario=admin_usuario.idUsuario).first()

    if admin_rol is None:
        nuevo_admin = Administrador(
            nombre='Admin',
            apellido='Medicent',
            correo='adminmedicent@gmail.com',
            telefono='3001234567',
            idUsuario=admin_usuario.idUsuario
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        print("Rol de Administrador asignado correctamente.")
    else:
        print("El rol de Administrador ya estaba asignado.")