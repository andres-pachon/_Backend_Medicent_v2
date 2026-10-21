"""Store medication schedule and concentration unit.

Revision ID: c2f6a8d1e4b7
Revises: e6d6a52b8c24
Create Date: 2026-10-17
"""

from alembic import op
import sqlalchemy as sa


revision = "c2f6a8d1e4b7"
down_revision = "e6d6a52b8c24"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("medicamento", sa.Column("unidadConcentracion", sa.String(length=20), nullable=True))
    op.add_column("medicamento", sa.Column("horario", sa.Time(), nullable=True))
    op.add_column("medicamento", sa.Column("frecuencia", sa.String(length=50), nullable=True))
    op.add_column("medicamento", sa.Column("dias", sa.String(length=100), nullable=True))


def downgrade():
    op.drop_column("medicamento", "dias")
    op.drop_column("medicamento", "frecuencia")
    op.drop_column("medicamento", "horario")
    op.drop_column("medicamento", "unidadConcentracion")