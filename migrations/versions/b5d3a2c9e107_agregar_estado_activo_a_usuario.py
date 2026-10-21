"""Add reversible account deactivation flag.

Revision ID: b5d3a2c9e107
Revises: a4f90e2c1b77
Create Date: 2026-10-20
"""

from alembic import op
import sqlalchemy as sa


revision = "b5d3a2c9e107"
down_revision = "a4f90e2c1b77"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "usuario",
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )


def downgrade():
    op.drop_column("usuario", "activo")
