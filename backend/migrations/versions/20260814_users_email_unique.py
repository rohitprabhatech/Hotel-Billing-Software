"""Global users.email unique constraint."""

from alembic import op

revision = "20260814_users_email_unique"
down_revision = "20260814_whatsapp_bill"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_users_email", "users", ["email"])


def downgrade():
    op.drop_constraint("uq_users_email", "users", type_="unique")
