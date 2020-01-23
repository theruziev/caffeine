"""initials

Revision ID: bc321cb22cc7
Revises: 
Create Date: 2020-01-21 18:13:47.032056

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bc321cb22cc7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "product_categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=True),
        sa.Column("slug", sa.String(length=1024), nullable=True),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_categories_slug"), "product_categories", ["slug"], unique=True)
    op.create_table(
        "product_options",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=1024), nullable=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_options_name"), "product_options", ["name"], unique=True)
    op.create_index(
        op.f("ix_product_options_product_id"), "product_options", ["product_id"], unique=False
    )
    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=True),
        sa.Column("slug", sa.String(length=1024), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("long_description", sa.Text(), nullable=True),
        sa.Column("image", sa.Text(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_slug"), "products", ["slug"], unique=True)
    op.create_table(
        "pubsub",
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("channel", sa.String(length=256), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.Integer(), nullable=True),
        sa.Column("is_done", sa.Boolean(), nullable=True),
    )
    op.create_index(op.f("ix_pubsub_uuid"), "pubsub", ["uuid"], unique=True)
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
        sa.Column("ref_id", sa.Integer(), nullable=True),
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
    op.drop_index(op.f("ix_products_slug"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_product_options_product_id"), table_name="product_options")
    op.drop_index(op.f("ix_product_options_name"), table_name="product_options")
    op.drop_table("product_options")
    op.drop_index(op.f("ix_product_categories_slug"), table_name="product_categories")
    op.drop_table("product_categories")
    # ### end Alembic commands ###