from flask import request, jsonify
from app.models.medicamento import Medicamento
from app.database.database import db
from datetime import date

class MedicamentoController:

    @staticmethod
    def get_medicamentos():
        medicamentos = Medicamento.query.all()
        return jsonify([
            {
                "id": m.idMedicamento,
                "nombre": m.nombre,
                "dosis": f"{m.concentracion}mg",
                "frecuenciaDiaria": m.frecuenciaDiaria,
            }
            for m in medicamentos
        ]), 200

    @staticmethod
    def crear_medicamento():
        data = request.get_json()
        try:
            # Extraer número de la dosis (ej: "500mg" -> 500)
            dosis_str = data.get('dosis', '0')
            concentracion = float(''.join(filter(lambda x: x.isdigit() or x == '.', dosis_str)) or 0)

            nuevo = Medicamento(
                nombre=data.get('nombre'),
                concentracion=concentracion,
                frecuenciaDiaria=1,
                fechaVencimiento=date(2027, 12, 31),  # fecha por defecto
                idTratamiento=1,      # por ahora fijo
                idTipoMedicamento=1,  # por ahora fijo
                idViaAdministracion=1, # por ahora fijo
                idStock=1             # por ahora fijo
            )
            db.session.add(nuevo)
            db.session.commit()
            return jsonify({
                "id": nuevo.idMedicamento,
                "nombre": nuevo.nombre,
                "dosis": f"{nuevo.concentracion}mg"
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": str(e)}), 400