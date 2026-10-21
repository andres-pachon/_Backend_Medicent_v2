from datetime import time
from app.database.database import db

class Medicamento(db.Model):
    __tablename__ = 'medicamento'

    idMedicamento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    concentracion = db.Column(db.Float, nullable=False)
    unidadConcentracion = db.Column(db.String(20), nullable=True)
    frecuenciaDiaria = db.Column(db.Integer, nullable=False)
    horario = db.Column(db.Time, nullable=True)
    frecuencia = db.Column(db.String(50), nullable=True)
    dias = db.Column(db.String(100), nullable=True)
    fechaVencimiento = db.Column(db.Date, nullable=False)

    idTratamiento = db.Column(db.Integer, db.ForeignKey('tratamiento.idTratamiento'), nullable=False)
    idTipoMedicamento = db.Column(db.Integer, db.ForeignKey('tipo_medicamento.idTipoMedicamento'), nullable=False)
    idViaAdministracion = db.Column(db.Integer, db.ForeignKey('via_administracion.idViaAdministracion'), nullable=False)
    idStock = db.Column(db.Integer, db.ForeignKey('stock_disponible.idStock'), nullable=False)