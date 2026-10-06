from app.database.database import db

class StockDisponible(db.Model):
    __tablename__ = 'stock_disponible'

    idStock = db.Column(db.Integer, primary_key=True)
    fechaActualizacion = db.Column(db.Date, nullable=False)
    cantidadFrascos = db.Column(db.Integer, nullable=False, default=0)
    cantidadPastillas = db.Column(db.Integer, nullable=False, default=0)

    medicamentos = db.relationship('Medicamento', backref='stock_disponible', lazy=True)