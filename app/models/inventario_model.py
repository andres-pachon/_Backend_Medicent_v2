from datetime import date
from app.database.database import db

class InventarioPersonal(db.Model):
    __tablename__ = 'inventarios_personales'

    id_inventario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    id_medicamento = db.Column(db.Integer, db.ForeignKey('medicamento.idMedicamento'), nullable=False)
    cantidad_actual = db.Column(db.Integer, nullable=False, default=0)
    fecha_vencimiento_lote = db.Column(db.Date, nullable=True)
    alerta_stock_minimo = db.Column(db.Integer, default=5)

    def to_dict(self):
        return {
            'id_inventario': self.id_inventario,
            'id_paciente': self.id_paciente,
            'id_medicamento': self.id_medicamento,
            'cantidad_actual': self.cantidad_actual,
            'fecha_vencimiento_lote': self.fecha_vencimiento_lote.strftime('%Y-%m-%d') if self.fecha_vencimiento_lote else None,
            'alerta_stock_minimo': self.alerta_stock_minimo,
            'es_bajo_stock': self.cantidad_actual <= self.alerta_stock_minimo
        }