import enum
from app.database.database import db

class TipoSangreEnum(enum.Enum):
    A_POSITIVO = "A+"
    A_NEGATIVO = "A-"
    B_POSITIVO = "B+"
    B_NEGATIVO = "B-"
    O_POSITIVO = "O+"
    O_NEGATIVO = "O-"
    AB_POSITIVO = "AB+"
    AB_NEGATIVO = "AB-"

class Paciente(db.Model):
    __tablename__ = 'paciente'

    idPaciente = db.Column(db.Integer, primary_key=True)
    estatura = db.Column(db.Float, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    tipoSangre = db.Column(db.Enum(TipoSangreEnum), nullable=False)
    dieta = db.Column(db.String(150), nullable=True)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    # Relaciones del paciente
    tratamientos = db.relationship('Tratamiento', backref='paciente', cascade='all, delete-orphan', lazy=True)
    adherencias = db.relationship('Adherencia', backref='paciente', cascade='all, delete-orphan', lazy=True)
    alertas = db.relationship('Alerta', backref='paciente', cascade='all, delete-orphan', lazy=True)