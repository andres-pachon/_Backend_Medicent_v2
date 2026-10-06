from app.database.database import db

class TipoAlerta(db.Model):
    __tablename__ = 'tipo_alerta'

    idTipoAlerta = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)

    alertas = db.relationship('Alerta', backref='tipo_alerta', lazy=True)