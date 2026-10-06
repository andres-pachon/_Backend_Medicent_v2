from app.database.database import db

class Alerta(db.Model):
    __tablename__ = 'alerta'

    idAlerta = db.Column(db.Integer, primary_key=True)
    fechaAlerta = db.Column(db.Date, nullable=False)
    
    idPaciente = db.Column(db.Integer, db.ForeignKey('paciente.idPaciente'), nullable=False)
    idTipoAlerta = db.Column(db.Integer, db.ForeignKey('tipo_alerta.idTipoAlerta'), nullable=False)