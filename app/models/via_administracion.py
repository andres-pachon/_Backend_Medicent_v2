from app.database.database import db

class ViaAdministracion(db.Model):
    __tablename__ = 'via_administracion'

    idViaAdministracion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)

    medicamentos = db.relationship('Medicamento', backref='via_administracion', lazy=True)