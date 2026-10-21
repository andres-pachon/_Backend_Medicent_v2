from datetime import datetime
from app.database.database import db

class Adherencia(db.Model):
    __tablename__ = 'adherencia'

    idAdherencia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPaciente = db.Column(db.Integer, db.ForeignKey('paciente.idPaciente'), nullable=False)
    idTratamiento = db.Column(db.Integer, db.ForeignKey('tratamiento.idTratamiento'), nullable=True)
    fechaGeneracion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    periodoInicio = db.Column(db.Date, nullable=True)
    periodoFin = db.Column(db.Date, nullable=True)
    totalProgramadas = db.Column(db.Integer, nullable=False, default=0)
    totalRealizadas = db.Column(db.Integer, nullable=False, default=0)
    porcentaje = db.Column(db.Float, nullable=False)
    observaciones = db.Column(db.String(255), nullable=True)

    # Serializador para devolver JSON en las respuestas de la API
    def to_dict(self):
        return {
            'idAdherencia': self.idAdherencia,
            'idPaciente': self.idPaciente,
            'idTratamiento': self.idTratamiento,
            # AdherenciaService stores this timestamp in UTC; include the timezone
            # so clients can render it in the patient's local time.
            'fechaGeneracion': self.fechaGeneracion.strftime('%Y-%m-%dT%H:%M:%SZ') if self.fechaGeneracion else None,
            'periodoInicio': self.periodoInicio.strftime('%Y-%m-%d') if self.periodoInicio else None,
            'periodoFin': self.periodoFin.strftime('%Y-%m-%d') if self.periodoFin else None,
            'totalProgramadas': self.totalProgramadas,
            'totalRealizadas': self.totalRealizadas,
            'porcentaje': self.porcentaje,
            'observaciones': self.observaciones
        }
