from app.database.database import db

class Toma(db.Model):
    __tablename__ = 'toma'

    idToma = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    dosis = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.String(255))
    estado = db.Column(db.String(50), default='tomado')
    idMedicamento = db.Column(db.Integer, db.ForeignKey('medicamento.idMedicamento'), nullable=False)
    idPaciente = db.Column(db.Integer, db.ForeignKey('paciente.idPaciente'), nullable=False)

    medicamento = db.relationship('Medicamento', backref='tomas')