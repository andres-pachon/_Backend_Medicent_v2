"""Link caregiver profiles to patient accounts and add one-time invitation codes."""

from alembic import op
import sqlalchemy as sa

revision = "f18a62c0d731"
down_revision = "c2f6a8d1e4b7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("cuidador", sa.Column("idPaciente", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_cuidador_paciente", "cuidador", "paciente", ["idPaciente"], ["idPaciente"])
    op.create_index("ix_cuidador_idPaciente", "cuidador", ["idPaciente"])
    op.add_column("paciente", sa.Column("codigoVinculacion", sa.String(length=24), nullable=True))
    op.add_column("paciente", sa.Column("codigoVinculacionExpira", sa.DateTime(), nullable=True))
    op.create_unique_constraint("uq_paciente_codigoVinculacion", "paciente", ["codigoVinculacion"])


def downgrade():
    op.drop_constraint("uq_paciente_codigoVinculacion", "paciente", type_="unique")
    op.drop_column("paciente", "codigoVinculacionExpira")
    op.drop_column("paciente", "codigoVinculacion")
    op.drop_index("ix_cuidador_idPaciente", table_name="cuidador")
    op.drop_constraint("fk_cuidador_paciente", "cuidador", type_="foreignkey")
    op.drop_column("cuidador", "idPaciente")
