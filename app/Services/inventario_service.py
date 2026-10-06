from datetime import datetime
from app.database.database import db
from app.models.inventario_model import InventarioPersonal

class InventarioService:

    @staticmethod
    def obtener_inventario_paciente(id_paciente):
        items = InventarioPersonal.query.filter_by(id_paciente=id_paciente).all()
        return [item.to_dict() for item in items], 200

    @staticmethod
    def recargar_stock(id_paciente, id_medicamento, cantidad_a_sumar, fecha_vencimiento=None):
        if cantidad_a_sumar <= 0:
            return {"error": "La cantidad a recargar debe ser mayor a cero"}, 400

        item = InventarioPersonal.query.filter_by(
            id_paciente=id_paciente,
            id_medicamento=id_medicamento
        ).first()

        if item:
            item.cantidad_actual += cantidad_a_sumar
            if fecha_vencimiento:
                item.fecha_vencimiento_lote = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
        else:
            vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date() if fecha_vencimiento else None
            item = InventarioPersonal(
                id_paciente=id_paciente,
                id_medicamento=id_medicamento,
                cantidad_actual=cantidad_a_sumar,
                fecha_vencimiento_lote=vencimiento
            )
            db.session.add(item)

        db.session.commit()
        return {
            "mensaje": "Stock actualizado exitosamente",
            "inventario": item.to_dict()
        }, 200

    @staticmethod
    def descontar_stock(id_paciente, id_medicamento, cantidad=1):
        """
        Método interno reutilizable: descuenta unidades cuando se registra una toma.
        """
        item = InventarioPersonal.query.filter_by(
            id_paciente=id_paciente,
            id_medicamento=id_medicamento
        ).first()

        if not item or item.cantidad_actual <= 0:
            return False, "Stock insuficiente o no registrado para este medicamento"

        item.cantidad_actual = max(0, item.cantidad_actual - cantidad)
        db.session.commit()

        alerta = item.cantidad_actual <= item.alerta_stock_minimo
        return True, {
            "stock_restante": item.cantidad_actual,
            "alerta_stock_bajo": alerta
        }