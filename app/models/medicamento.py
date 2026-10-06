from app.database.database import db

class Medicamento(db.Model):
    __tablename__ = 'medicamento'

    idMedicamento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    concentracion = db.Column(db.Float, nullable=False)
    frecuenciaDiaria = db.Column(db.Integer, nullable=False)
    fechaVencimiento = db.Column(db.Date, nullable=False)
    
    # Llaves foráneas según las conexiones del diagrama
    idTratamiento = db.Column(db.Integer, db.ForeignKey('tratamiento.idTratamiento'), nullable=False)
    idTipoMedicamento = db.Column(db.Integer, db.ForeignKey('tipo_medicamento.idTipoMedicamento'), nullable=False)
    idViaAdministracion = db.Column(db.Integer, db.ForeignKey('via_administracion.idViaAdministracion'), nullable=False)
    idStock = db.Column(db.Integer, db.ForeignKey('stock_disponible.idStock'), nullable=False)