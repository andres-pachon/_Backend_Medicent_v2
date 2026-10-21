"""Add patient profile details and caregiver experience.

Revision ID: e6d6a52b8c24
Revises: 1ba8944413cd
Create Date: 2026-10-17
"""

from alembic import op
import sqlalchemy as sa


revision = "e6d6a52b8c24"
down_revision = "1ba8944413cd"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("paciente", sa.Column("contactoEmergencia", sa.String(length=150), nullable=True))
    op.add_column("paciente", sa.Column("eps", sa.String(length=150), nullable=True))
    op.add_column("paciente", sa.Column("alergias", sa.Text(), nullable=True))
    op.add_column("paciente", sa.Column("diagnostico", sa.Text(), nullable=True))
    op.add_column("cuidador", sa.Column("experienciaAnios", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("cuidador", "experienciaAnios")
    op.drop_column("paciente", "diagnostico")
    op.drop_column("paciente", "alergias")
    op.drop_column("paciente", "eps")
    op.drop_column("paciente", "contactoEmergencia")