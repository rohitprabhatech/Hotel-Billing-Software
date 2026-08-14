"""WhatsApp delivery webhook status columns."""

from alembic import op
import sqlalchemy as sa

revision = "20260814_wa_webhook_status"
down_revision = "20260814_users_email_unique"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("bill_deliveries", sa.Column("delivered_at", sa.DateTime(), nullable=True))
    op.add_column("bill_deliveries", sa.Column("read_at", sa.DateTime(), nullable=True))
    op.create_index(
        "ix_bill_deliveries_provider_message",
        "bill_deliveries",
        ["provider_message_id"],
    )


def downgrade():
    op.drop_index("ix_bill_deliveries_provider_message", table_name="bill_deliveries")
    op.drop_column("bill_deliveries", "read_at")
    op.drop_column("bill_deliveries", "delivered_at")
