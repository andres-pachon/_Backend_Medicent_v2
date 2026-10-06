from app.database.database import db

class Biomarcador(db.Model):
    __tablename__ = 'biomarcador'

    idBiomarcador = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20))
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    estado = db.Column(db.String(20), default='bueno')
    notas = db.Column(db.String(255))
    idPaciente = db.Column(db.Integer, db.ForeignKey('paciente.idPaciente'), nullable=False)