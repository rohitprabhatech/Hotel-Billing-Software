"""WhatsApp bill delivery: customer phone on bills + tenant WA config + deliveries."""

from alembic import op
import sqlalchemy as sa

revision = "20260814_whatsapp_bill"
down_revision = "20260814_stock_notifications"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("bills", sa.Column("customer_name", sa.String(120), nullable=True))
    op.add_column("bills", sa.Column("customer_phone_country_code", sa.String(8), nullable=True))
    op.add_column("bills", sa.Column("customer_phone_national", sa.String(20), nullable=True))
    op.add_column("bills", sa.Column("customer_phone_e164", sa.String(20), nullable=True))

    op.create_table(
        "tenant_whatsapp_configs",
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("phone_number_id", sa.String(64), nullable=True),
        sa.Column("waba_id", sa.String(64), nullable=True),
        sa.Column("display_phone_e164", sa.String(20), nullable=True),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("template_name", sa.String(120), nullable=True),
        sa.Column("template_language", sa.String(20), nullable=False, server_default="en"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("connected_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "bill_deliveries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("bill_id", sa.String(36), sa.ForeignKey("bills.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("delivery_method", sa.String(20), nullable=False),
        sa.Column("recipient_phone_e164", sa.String(20), nullable=True),
        sa.Column("recipient_phone_masked", sa.String(32), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("provider_message_id", sa.String(120), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempted_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_bill_deliveries_tenant_bill", "bill_deliveries", ["tenant_id", "bill_id"])
    op.create_index("ix_bill_deliveries_tenant_created", "bill_deliveries", ["tenant_id", "created_at"])


def downgrade():
    op.drop_index("ix_bill_deliveries_tenant_created", table_name="bill_deliveries")
    op.drop_index("ix_bill_deliveries_tenant_bill", table_name="bill_deliveries")
    op.drop_table("bill_deliveries")
    op.drop_table("tenant_whatsapp_configs")
    op.drop_column("bills", "customer_phone_e164")
    op.drop_column("bills", "customer_phone_national")
    op.drop_column("bills", "customer_phone_country_code")
    op.drop_column("bills", "customer_name")
