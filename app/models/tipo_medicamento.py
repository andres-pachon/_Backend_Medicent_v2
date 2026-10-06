from app.database.database import db

class TipoMedicamento(db.Model):
    __tablename__ = 'tipo_medicamento'

    idTipoMedicamento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)

    medicamentos = db.relationship('Medicamento', backref='tipo_medicamento', lazy=True)