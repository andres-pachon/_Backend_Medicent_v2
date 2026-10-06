from datetime import datetime
from app.database.database import db
from app.models.adherencia import Adherencia
from app.models.toma import Toma
from app.models.tratamiento import Tratamiento


class AdherenciaService:

    @staticmethod
    def calcular_adherencia_tratamiento(id_tratamiento, fecha_inicio_str, fecha_fin_str):
        """
        Calcula el porcentaje de adherencia de un tratamiento en un rango de fechas
        y persiste el reporte histórico en la base de datos.
        """
        # 1. Validar que el tratamiento exista
        tratamiento = Tratamiento.query.get(id_tratamiento)
        if not tratamiento:
            return {"error": "Tratamiento no encontrado"}, 404

        # 2. Parsear el rango de fechas
        try:
            periodo_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            periodo_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except ValueError:
            return {"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD"}, 400

        if periodo_inicio > periodo_fin:
            return {"error": "La fecha de inicio no puede ser posterior a la fecha de fin"}, 400

        # 3. Consultar las tomas registradas en el rango de fechas para el paciente
        tomas = Toma.query.filter(
            Toma.idPaciente == tratamiento.idPaciente,
            Toma.fecha >= periodo_inicio,
            Toma.fecha <= periodo_fin
        ).all()

        total_programadas = len(tomas)
        if total_programadas == 0:
            return {
                "error": "No existen tomas programadas en el periodo seleccionado"
            }, 404

        # 4. Contar cuántas tomas están marcadas como completadas
        total_realizadas = sum(1 for t in tomas if t.estado and t.estado.lower() == 'tomada')

        # 5. Calcular porcentaje
        porcentaje = round((total_realizadas / total_programadas) * 100, 2)

        # 6. Generar diagnóstico clínico según el umbral
        if porcentaje >= 80.0:
            observacion = "Adherencia óptima al tratamiento"
        elif porcentaje >= 50.0:
            observacion = "Adherencia moderada con riesgo de desfase"
        else:
            observacion = "Riesgo crítico de abandono de tratamiento"

        # 7. Crear el registro en la tabla adherencia
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
        """
        Retorna la lista cronológica de reportes calculados para un tratamiento.
        """
        reportes = Adherencia.query.filter_by(idTratamiento=id_tratamiento)\
            .order_by(Adherencia.fechaGeneracion.desc()).all()
            
        return [r.to_dict() for r in reportes], 200

    @staticmethod
    def obtener_ultimo_reporte_paciente(id_paciente):
        """
        Obtiene el reporte más reciente generado para un paciente.
        """
        reporte = Adherencia.query.filter_by(idPaciente=id_paciente)\
            .order_by(Adherencia.fechaGeneracion.desc()).first()
            
        if not reporte:
            return {"mensaje": "No hay reportes de adherencia registrados para este paciente"}, 404

        return reporte.to_dict(), 200