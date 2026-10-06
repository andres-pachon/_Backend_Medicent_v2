from app import create_app
from app.database.database import db, bcrypt
from app.models.usuario import Usuario
from app.models.tipo_documento import TipoDocumento # Importamos para la FK obligatoria
from datetime import date

app = create_app()

with app.app_context():
    tipo_cc = TipoDocumento.query.filter_by(nombre='Cédula de Ciudadanía').first()
    if tipo_cc is None:
        tipo_cc = TipoDocumento(nombre='Cédula de Ciudadanía')
        db.session.add(tipo_cc)
        db.session.commit()

    
    admin_existente = Usuario.query.filter_by(correo='adminmedicent@gmail.com').first()

    if admin_existente is None:
        admin = Usuario(
            nombre='Admin',
            apellido='Admin',
            documento='123456789',
            correo='adminmedicent@gmail.com', 
            telefono='3001234567',
            fechaNacimiento=date(2000, 1, 1),  
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            idTipoDocumento=tipo_cc.idTipoDocumento 
        )

        db.session.add(admin)
        db.session.commit()
        print("Usuario Admin creado exitosamente.")
    else:
        print("El usuario Admin ya existe en la base de datos.")