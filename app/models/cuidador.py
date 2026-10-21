from app.database.database import db

class Cuidador(db.Model):
    __tablename__ = 'cuidador'

    idCuidador = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    experienciaAnios = db.Column(db.Integer, nullable=True)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    idPaciente = db.Column(db.Integer, db.ForeignKey('paciente.idPaciente'), nullable=True, index=True)
    paciente = db.relationship('Paciente', back_populates='cuidadores')
