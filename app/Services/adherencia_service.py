from datetime import datetime, time, timedelta
import math

from app.database.database import db
from app.models.adherencia import Adherencia
from app.models.toma import Toma
from app.models.tratamiento import Tratamiento


class AdherenciaService:
    @staticmethod
    def _contar_tomas_programadas(tratamiento, medicamentos, fecha_inicio, fecha_fin):
        inicio = max(fecha_inicio, tratamiento.fechaInicio)
        fin = min(fecha_fin, tratamiento.fechaFin)
        if inicio > fin:
            return 0

        cantidad = 0
        abreviaturas = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']
        for medicamento in medicamentos:
            frecuencia = medicamento.frecuencia or 'Diario'
            if frecuencia == 'Días específicos' and medicamento.dias:
                dias_seleccionados = medicamento.dias.split(',')
                dia = inicio
                while dia <= fin:
                    if abreviaturas[dia.weekday()] in dias_seleccionados:
                        cantidad += 1
                    dia += timedelta(days=1)
                continue

            if frecuencia in ('Cada 8 horas', 'Cada 12 horas') and medicamento.horario:
                intervalo = 8 if frecuencia == 'Cada 8 horas' else 12
                ancla = datetime.combine(tratamiento.fechaInicio, medicamento.horario)
                limite_inferior = datetime.combine(inicio, time.min)
                limite_superior = datetime.combine(fin, time.max)
                intervalo_delta = timedelta(hours=intervalo)
                pasos = max(0, math.ceil((limite_inferior - ancla).total_seconds() / intervalo_delta.total_seconds()))
                ocurrencia = ancla + pasos * intervalo_delta
                while ocurrencia <= limite_superior:
                    cantidad += 1
                    ocurrencia += intervalo_delta
                continue

            cantidad += ((fin - inicio).days + 1) * max(1, medicamento.frecuenciaDiaria or 1)
        return cantidad

    @staticmethod
    def calcular_adherencia_tratamiento(id_tratamiento, fecha_inicio_str, fecha_fin_str):
        tratamiento = db.session.get(Tratamiento, id_tratamiento)
        if not tratamiento:
            return {"error": "Tratamiento no encontrado"}, 404

        try:
            periodo_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            periodo_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return {"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD"}, 400

        if periodo_inicio > periodo_fin:
            return {"error": "La fecha de inicio no puede ser posterior a la fecha de fin"}, 400

        medicamentos = tratamiento.medicamentos
        if not medicamentos:
            return {"error": "El tratamiento no tiene medicamentos registrados"}, 404

        total_programadas = AdherenciaService._contar_tomas_programadas(
            tratamiento, medicamentos, periodo_inicio, periodo_fin
        )
        if total_programadas == 0:
            return {"error": "No hay tomas programadas en el periodo seleccionado"}, 404

        ids_medicamentos = [medicamento.idMedicamento for medicamento in medicamentos]
        tomas = Toma.query.filter(
            Toma.idPaciente == tratamiento.idPaciente,
            Toma.idMedicamento.in_(ids_medicamentos),
            Toma.fecha >= max(periodo_inicio, tratamiento.fechaInicio),
            Toma.fecha <= min(periodo_fin, tratamiento.fechaFin)
        ).all()
        registradas_completadas = sum(
            1 for toma in tomas if toma.estado and toma.estado.lower() in ('tomada', 'tomado')
        )
        total_realizadas = min(registradas_completadas, total_programadas)
        porcentaje = round((total_realizadas / total_programadas) * 100, 2)

        if porcentaje >= 80.0:
            observacion = "Adherencia óptima al tratamiento"
        elif porcentaje >= 50.0:
            observacion = "Adherencia moderada con riesgo de desfase"
        else:
            observacion = "Riesgo crítico de abandono de tratamiento"

        nuevo_reporte = Adherencia(
            idPaciente=tratamiento.idPaciente,
            idTratamiento=id_tratamiento,
            fechaGeneracion=datetime.utcnow(),
            periodoInicio=periodo_inicio,
            periodoFin=periodo_fin,
            totalProgramadas=total_programadas,
            totalRealizadas=total_realizadas,
            porcentaje=porcentaje,
            observaciones=observacion
        )
        db.session.add(nuevo_reporte)
        db.session.commit()
        return nuevo_reporte.to_dict(), 201

    @staticmethod
    def listar_reportes_tratamiento(id_tratamiento):
        reportes = Adherencia.query.filter_by(idTratamiento=id_tratamiento).order_by(
            Adherencia.fechaGeneracion.desc()
        ).all()
        return [reporte.to_dict() for reporte in reportes], 200

    @staticmethod
    def obtener_ultimo_reporte_paciente(id_paciente):
        reporte = Adherencia.query.filter_by(idPaciente=id_paciente).order_by(
            Adherencia.fechaGeneracion.desc()
        ).first()
        if not reporte:
            return {"mensaje": "No hay reportes de adherencia registrados para este paciente"}, 404
        return reporte.to_dict(), 200