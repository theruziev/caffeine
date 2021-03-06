"""initials

Revision ID: 0e927be6fb98
Revises: 
Create Date: 2020-01-24 16:19:59.627508

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0e927be6fb98"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pubsub",
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("channel", sa.String(length=256), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.Integer(), nullable=True),
        sa.Column("is_done", sa.Boolean(), nullable=True),
    )
    op.create_index(op.f("ix_pubsub_uuid"), "pubsub", ["uuid"], unique=False)
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("password", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=256), nullable=True),
        sa.Column("type", sa.String(length=256), nullable=True),
        sa.Column("role", sa.String(length=256), nullable=True),
        sa.Column("activation_code", sa.String(length=1024), nullable=True),
        sa.Column("reset_password_code", sa.String(length=256), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_pubsub_uuid"), table_name="pubsub")
    op.drop_table("pubsub")
    # ### end Alembic commands ###
