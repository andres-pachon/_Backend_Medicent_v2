from app.database.database import db

class Tratamiento(db.Model):
    __tablename__ = 'tratamiento'

    idTratamiento = db.Column(db.Integer, primary_key=True)
    fechaInicio = db.Column(db.Date, nullable=False)
    fechaFin = db.Column(db.Date, nullable=False)
    
    idPaciente = db.Column(db.Integer, db.ForeignKey('paciente.idPaciente'), nullable=False)
    
    # Un tratamiento engloba medicamentos
    medicamentos = db.relationship('Medicamento', backref='tratamiento', cascade='all, delete-orphan', lazy=True)