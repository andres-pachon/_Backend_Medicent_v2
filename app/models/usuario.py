from app.database.database import db

class Usuario(db.Model):
    __tablename__ = 'usuario'

    idUsuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    fechaNacimiento = db.Column(db.Date, nullable=False)

    password = db.Column(db.String(255), nullable=False)
    
    
    idTipoDocumento = db.Column(db.Integer, db.ForeignKey('tipo_documento.idTipoDocumento'), nullable=False)

    
    administrador = db.relationship('Administrador', backref='usuario', uselist=False, cascade='all, delete-orphan')
    cuidador = db.relationship('Cuidador', backref='usuario', uselist=False, cascade='all, delete-orphan')
    paciente = db.relationship('Paciente', backref='usuario', uselist=False, cascade='all, delete-orphan')