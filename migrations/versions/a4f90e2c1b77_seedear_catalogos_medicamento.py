"""Seed the medication type and administration route catalogs."""
from alembic import op
import sqlalchemy as sa


revision = "a4f90e2c1b77"
down_revision = "f18a62c0d731"
branch_labels = None
depends_on = None


TIPOS_MEDICAMENTO = (
    "Tableta",
    "Cápsula",
    "Jarabe",
    "Gotas",
    "Inyección",
    "Crema",
    "Inhalador",
)
VIAS_ADMINISTRACION = (
    "Oral",
    "Intravenosa",
    "Subcutánea",
    "Tópica",
    "Inhalatoria",
    "Sublingual",
)


def _insertar_faltantes(nombre_tabla, nombre_columna, nombres):
    bind = op.get_bind()
    tabla = sa.table(nombre_tabla, sa.column(nombre_columna, sa.String(length=100)))
    existentes = set(bind.execute(sa.select(tabla.c[nombre_columna])).scalars())
    for nombre in nombres:
        if nombre not in existentes:
            bind.execute(tabla.insert().values({nombre_columna: nombre}))


def upgrade():
    _insertar_faltantes("tipo_medicamento", "nombre", TIPOS_MEDICAMENTO)
    _insertar_faltantes("via_administracion", "nombre", VIAS_ADMINISTRACION)


def downgrade():
    bind = op.get_bind()
    tipos = sa.table(
        "tipo_medicamento",
        sa.column("idTipoMedicamento", sa.Integer),
        sa.column("nombre", sa.String(length=100)),
    )
    medicamentos = sa.table("medicamento", sa.column("idTipoMedicamento", sa.Integer))
    vias = sa.table(
        "via_administracion",
        sa.column("idViaAdministracion", sa.Integer),
        sa.column("nombre", sa.String(length=100)),
    )
    medicamentos_con_via = sa.table("medicamento", sa.column("idViaAdministracion", sa.Integer))

    bind.execute(sa.delete(tipos).where(
        tipos.c.nombre.in_(TIPOS_MEDICAMENTO),
        ~sa.exists(sa.select(medicamentos.c.idTipoMedicamento).where(
            medicamentos.c.idTipoMedicamento == tipos.c.idTipoMedicamento
        )),
    ))
    bind.execute(sa.delete(vias).where(
        vias.c.nombre.in_(VIAS_ADMINISTRACION),
        ~sa.exists(sa.select(medicamentos_con_via.c.idViaAdministracion).where(
            medicamentos_con_via.c.idViaAdministracion == vias.c.idViaAdministracion
        )),
    ))