from app.database.database import db

class TipoDocumento(db.Model):
    __tablename__ = 'tipo_documento'

    idTipoDocumento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(150), nullable=True)

    # Relación inversa hacia usuarios
    usuarios = db.relationship('Usuario', backref='tipo_documento', lazy=True)