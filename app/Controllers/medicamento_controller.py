from datetime import date, datetime, timedelta
import re

from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.database.database import db
from app.models.inventario_model import InventarioPersonal
from app.models.adherencia import Adherencia
from app.models.toma import Toma
from app.models.medicamento import Medicamento
from app.models.stock_disponible import StockDisponible
from app.models.tratamiento import Tratamiento
from app.models.tipo_medicamento import TipoMedicamento
from app.models.via_administracion import ViaAdministracion
from app.Services.paciente_service import obtener_paciente_actual, obtener_usuario_actual


class MedicamentoController:
    @staticmethod
    def _serializar(medicamento):
        unidad = medicamento.unidadConcentracion or 'mg'
        return {
            "id": medicamento.idMedicamento,
            "idMedicamento": medicamento.idMedicamento,
            "nombre": medicamento.nombre,
            "dosis": f"{medicamento.concentracion:g}{unidad}",
            "frecuenciaDiaria": medicamento.frecuenciaDiaria,
            "horario": medicamento.horario.strftime('%H:%M') if medicamento.horario else None,
            "frecuencia": medicamento.frecuencia,
            "dias": medicamento.dias.split(',') if medicamento.dias else [],
            "via": medicamento.via_administracion.nombre if medicamento.via_administracion else None,
            "fechaInicio": medicamento.tratamiento.fechaInicio.isoformat() if medicamento.tratamiento else None,
            "fechaFin": medicamento.tratamiento.fechaFin.isoformat() if medicamento.tratamiento else None
        }

    @staticmethod
    @jwt_required()
    def get_opciones():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            if usuario.cuidador is not None:
                return jsonify({"tipos": [], "vias": []}), 200
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        return jsonify({
            "tipos": [{"id": tipo.idTipoMedicamento, "idTipoMedicamento": tipo.idTipoMedicamento, "nombre": tipo.nombre} for tipo in TipoMedicamento.query.order_by(TipoMedicamento.nombre).all()],
            "vias": [{"id": via.idViaAdministracion, "idViaAdministracion": via.idViaAdministracion, "nombre": via.nombre} for via in ViaAdministracion.query.order_by(ViaAdministracion.nombre).all()]
        }), 200

    @staticmethod
    @jwt_required()
    def get_medicamentos():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            if usuario.cuidador is not None:
                return jsonify([]), 200
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        medicamentos = Medicamento.query.join(Tratamiento).filter(
            Tratamiento.idPaciente == paciente.idPaciente
        ).order_by(Medicamento.nombre.asc()).all()
        return jsonify([MedicamentoController._serializar(medicamento) for medicamento in medicamentos]), 200

    @staticmethod
    @jwt_required()
    def crear_medicamento():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        data = request.get_json(silent=True) or {}
        requeridos = ('nombre', 'dosis', 'idTipoMedicamento', 'idViaAdministracion', 'fechaInicio', 'fechaFin', 'fechaVencimiento', 'horario', 'frecuencia')
        faltantes = [campo for campo in requeridos if not data.get(campo)]
        if faltantes:
            return jsonify({"message": "Faltan campos requeridos", "campos": faltantes}), 400

        match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*([a-zA-Zµ%]+)?\s*', str(data['dosis']))
        if not match:
            return jsonify({"message": "La dosis debe incluir un valor numérico y una unidad, por ejemplo 500 mg"}), 400

        try:
            concentracion = float(match.group(1))
            fecha_inicio = date.fromisoformat(data['fechaInicio'])
            fecha_fin = date.fromisoformat(data['fechaFin'])
            fecha_vencimiento = date.fromisoformat(data['fechaVencimiento'])
            horario = datetime.strptime(data['horario'], '%H:%M').time()
            id_tipo = int(data['idTipoMedicamento'])
            id_via = int(data['idViaAdministracion'])
            cantidad_inicial = int(data.get('cantidadInicial', 0))
        except (TypeError, ValueError):
            return jsonify({"message": "Revisa las fechas, dosis, horario, tipo, vía y cantidad"}), 400

        if concentracion <= 0 or fecha_inicio > fecha_fin or cantidad_inicial < 0:
            return jsonify({"message": "La dosis, el periodo o la cantidad no son válidos"}), 400
        frecuencia = str(data['frecuencia']).strip()
        frecuencias_diarias = {'Diario': 1, 'Cada 8 horas': 3, 'Cada 12 horas': 2, 'Días específicos': 1}
        if frecuencia not in frecuencias_diarias:
            return jsonify({"message": "La frecuencia seleccionada no es válida"}), 400
        dias = data.get('dias') or []
        if frecuencia == 'Días específicos' and not dias:
            return jsonify({"message": "Selecciona al menos un día para la frecuencia específica"}), 400
        if not isinstance(dias, list) or any(not isinstance(dia, str) for dia in dias):
            return jsonify({"message": "Los días seleccionados no son válidos"}), 400

        tipo = db.session.get(TipoMedicamento, id_tipo)
        via = db.session.get(ViaAdministracion, id_via)
        if tipo is None or via is None:
            return jsonify({"message": "El tipo o la vía de administración no existen"}), 400

        try:
            tratamiento = Tratamiento(
                fechaInicio=fecha_inicio,
                fechaFin=fecha_fin,
                idPaciente=paciente.idPaciente
            )
            stock = StockDisponible(
                fechaActualizacion=date.today(),
                cantidadFrascos=0,
                cantidadPastillas=0
            )
            db.session.add_all([tratamiento, stock])
            db.session.flush()

            medicamento = Medicamento(
                nombre=str(data['nombre']).strip(),
                concentracion=concentracion,
                unidadConcentracion=(match.group(2) or 'mg').lower(),
                frecuenciaDiaria=frecuencias_diarias[frecuencia],
                fechaVencimiento=fecha_vencimiento,
                horario=horario,
                frecuencia=frecuencia,
                dias=','.join(dias) if dias else None,
                idTratamiento=tratamiento.idTratamiento,
                idTipoMedicamento=tipo.idTipoMedicamento,
                idViaAdministracion=via.idViaAdministracion,
                idStock=stock.idStock
            )
            db.session.add(medicamento)
            db.session.flush()

            if cantidad_inicial:
                db.session.add(InventarioPersonal(
                    id_usuario=paciente.idUsuario,
                    id_medicamento=medicamento.idMedicamento,
                    cantidad_actual=cantidad_inicial,
                    fecha_vencimiento_lote=fecha_vencimiento
                ))
            db.session.commit()
            return jsonify(MedicamentoController._serializar(medicamento)), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({"message": f"No se pudo guardar el medicamento: {error}"}), 400

    @staticmethod
    @jwt_required()
    def actualizar_horario(id_medicamento):
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        medicamento = Medicamento.query.join(Tratamiento).filter(
            Medicamento.idMedicamento == id_medicamento,
            Tratamiento.idPaciente == paciente.idPaciente
        ).first()
        if medicamento is None:
            return jsonify({"message": "Medicamento no encontrado para esta cuenta"}), 404
        if medicamento.horario is not None and medicamento.frecuencia:
            return jsonify({"message": "El horario ya está configurado. Esta opción solo completa datos faltantes"}), 409

        data = request.get_json(silent=True) or {}
        frecuencia = str(data.get('frecuencia', '')).strip()
        frecuencias_diarias = {'Diario': 1, 'Cada 8 horas': 3, 'Cada 12 horas': 2, 'Días específicos': 1}
        if frecuencia not in frecuencias_diarias:
            return jsonify({"message": "La frecuencia seleccionada no es válida"}), 400

        try:
            horario = datetime.strptime(data.get('horario'), '%H:%M').time()
        except (TypeError, ValueError):
            return jsonify({"message": "La hora debe tener el formato HH:MM"}), 400

        dias = data.get('dias') or []
        dias_validos = {'lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom'}
        if not isinstance(dias, list) or any(dia not in dias_validos for dia in dias):
            return jsonify({"message": "Los días seleccionados no son válidos"}), 400
        if frecuencia == 'Días específicos' and not dias:
            return jsonify({"message": "Selecciona al menos un día"}), 400

        medicamento.horario = horario
        medicamento.frecuencia = frecuencia
        medicamento.frecuenciaDiaria = frecuencias_diarias[frecuencia]
        medicamento.dias = ','.join(dict.fromkeys(dias)) if frecuencia == 'Días específicos' else None
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({"message": "No se pudo actualizar el horario del medicamento"}), 400
        return jsonify(MedicamentoController._serializar(medicamento)), 200

    @staticmethod
    @jwt_required()
    def eliminar_medicamento(id_medicamento):
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        medicamento = Medicamento.query.join(Tratamiento).filter(
            Medicamento.idMedicamento == id_medicamento,
            Tratamiento.idPaciente == paciente.idPaciente
        ).first()
        if medicamento is None:
            return jsonify({"message": "Medicamento no encontrado para esta cuenta"}), 404

        tratamiento = medicamento.tratamiento
        stock = medicamento.stock_disponible
        tiene_registros = (
            Toma.query.filter_by(idMedicamento=id_medicamento).first() is not None
            or InventarioPersonal.query.filter_by(id_medicamento=id_medicamento).first() is not None
            or Adherencia.query.filter_by(idTratamiento=tratamiento.idTratamiento).first() is not None
        )
        if tiene_registros:
            return jsonify({"message": "No se puede eliminar un medicamento con tomas, inventario o reportes asociados"}), 409

        otros_medicamentos = Medicamento.query.filter(
            Medicamento.idTratamiento == tratamiento.idTratamiento,
            Medicamento.idMedicamento != id_medicamento
        ).count()
        db.session.delete(medicamento)
        db.session.flush()
        if tratamiento is not None and otros_medicamentos == 0:
            db.session.delete(tratamiento)
        if stock is not None:
            db.session.delete(stock)
        db.session.commit()
        return jsonify({"message": "Medicamento eliminado"}), 200
    @staticmethod
    @jwt_required()
    def proxima_toma():
        usuario = obtener_usuario_actual()
        if usuario is None:
            return jsonify({"message": "La cuenta no es válida"}), 401
        paciente = obtener_paciente_actual()
        if paciente is None:
            if usuario.cuidador is not None:
                return jsonify(None), 200
            return jsonify({"message": "La cuenta no tiene un perfil de paciente asociado"}), 409

        ahora = datetime.now()
        medicamentos = Medicamento.query.join(Tratamiento).filter(
            Tratamiento.idPaciente == paciente.idPaciente,
            Tratamiento.fechaFin >= ahora.date()
        ).all()
        candidatos = []
        abreviaturas = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']

        for medicamento in medicamentos:
            if medicamento.horario is None or medicamento.tratamiento is None:
                continue
            tratamiento = medicamento.tratamiento
            inicio = max(tratamiento.fechaInicio, ahora.date())
            limite = min(tratamiento.fechaFin, ahora.date() + timedelta(days=365))
            frecuencia = medicamento.frecuencia or 'Diario'

            if frecuencia in ('Cada 8 horas', 'Cada 12 horas'):
                intervalo = 8 if frecuencia == 'Cada 8 horas' else 12
                ancla = datetime.combine(tratamiento.fechaInicio, medicamento.horario)
                if ancla < ahora:
                    transcurrido = (ahora - ancla).total_seconds()
                    pasos = int(transcurrido // (intervalo * 3600)) + 1
                else:
                    pasos = 0
                proxima = ancla + timedelta(hours=pasos * intervalo)
                if proxima.date() <= limite:
                    candidatos.append((proxima, medicamento))
                continue

            dia = inicio
            while dia <= limite:
                if frecuencia != 'Días específicos' or abreviaturas[dia.weekday()] in (medicamento.dias or '').split(','):
                    proxima = datetime.combine(dia, medicamento.horario)
                    if proxima > ahora:
                        candidatos.append((proxima, medicamento))
                        break
                dia += timedelta(days=1)

        if not candidatos:
            return jsonify(None), 200
        proxima, medicamento = min(candidatos, key=lambda item: item[0])
        return jsonify({
            "medicamento": medicamento.nombre,
            "dosis": f"{medicamento.concentracion:g}{medicamento.unidadConcentracion or 'mg'}",
            "hora": proxima.strftime('%H:%M'),
            "fecha": proxima.date().isoformat(),
            "via": medicamento.via_administracion.nombre if medicamento.via_administracion else None
        }), 200
