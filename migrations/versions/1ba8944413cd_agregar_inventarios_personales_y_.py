"""Create personal inventory and complete adherence records.

Revision ID: 1ba8944413cd
Revises: 3933209b1d19
Create Date: 2026-10-06 17:03:20.050955
"""
from alembic import op
import sqlalchemy as sa


revision = "1ba8944413cd"
down_revision = "3933209b1d19"
branch_labels = None
depends_on = None


def upgrade():
    # The table was referenced by the previous revision but was never created.
    op.create_table(
        "inventarios_personales",
        sa.Column("id_inventario", sa.Integer(), autoincrement=True, nullable=False),
        # Keep the historical database column name; it stores usuario.idUsuario.
        sa.Column("id_paciente", sa.Integer(), nullable=False),
        sa.Column("id_medicamento", sa.Integer(), nullable=False),
        sa.Column("cantidad_actual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fecha_vencimiento_lote", sa.Date(), nullable=True),
        sa.Column("alerta_stock_minimo", sa.Integer(), nullable=True, server_default="5"),
        sa.ForeignKeyConstraint(
            ["id_paciente"], ["usuario.idUsuario"], name="fk_inventario_paciente"
        ),
        sa.ForeignKeyConstraint(
            ["id_medicamento"], ["medicamento.idMedicamento"], name="fk_inventario_medicamento"
        ),
        sa.PrimaryKeyConstraint("id_inventario"),
    )

    # Preserve legacy adherence rows: treatment and period fields stay nullable
    # for historical records that predate treatment-specific reports.
    op.add_column("adherencia", sa.Column("idTratamiento", sa.Integer(), nullable=True))
    op.add_column("adherencia", sa.Column("periodoInicio", sa.Date(), nullable=True))
    op.add_column("adherencia", sa.Column("periodoFin", sa.Date(), nullable=True))
    op.add_column(
        "adherencia",
        sa.Column("totalProgramadas", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "adherencia",
        sa.Column("totalRealizadas", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("adherencia", sa.Column("observaciones", sa.String(length=255), nullable=True))
    op.create_foreign_key(
        "fk_adherencia_tratamiento",
        "adherencia",
        "tratamiento",
        ["idTratamiento"],
        ["idTratamiento"],
    )

    # The original schema used DATE; some existing installations already have
    # DATETIME. Requesting DATETIME is safe for either starting type.
    op.alter_column(
        "adherencia",
        "fechaGeneracion",
        existing_type=sa.Date(),
        type_=sa.DateTime(),
        existing_nullable=False,
    )


def downgrade():
    op.drop_constraint("fk_adherencia_tratamiento", "adherencia", type_="foreignkey")
    op.drop_column("adherencia", "observaciones")
    op.drop_column("adherencia", "totalRealizadas")
    op.drop_column("adherencia", "totalProgramadas")
    op.drop_column("adherencia", "periodoFin")
    op.drop_column("adherencia", "periodoInicio")
    op.drop_column("adherencia", "idTratamiento")
    op.alter_column(
        "adherencia",
        "fechaGeneracion",
        existing_type=sa.DateTime(),
        type_=sa.Date(),
        existing_nullable=False,
    )
    op.drop_table("inventarios_personales")
