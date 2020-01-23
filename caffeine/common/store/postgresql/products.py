import sqlalchemy as sa

from caffeine.common.store.postgresql.db import metadata

product_category_table = sa.Table(
    "product_categories",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("title", sa.String(1024)),
    sa.Column("slug", sa.String(1024), index=True, unique=True),
    sa.Column("parent_id", sa.BigInteger),
    sa.Column("is_active", sa.Boolean, default=False),
)

product_table = sa.Table(
    "products",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("title", sa.String(1024)),
    sa.Column("slug", sa.String(1024), index=True, unique=True),
    sa.Column("status", sa.String),
    sa.Column("price", sa.Integer),
    sa.Column("description", sa.Text),
    sa.Column("long_description", sa.Text),
    sa.Column("image", sa.Text),
    sa.Column("type", sa.String),
)

product_options_table = sa.Table(
    "product_options",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
    sa.Column("product_id", sa.BigInteger, index=True),
    sa.Column("name", sa.String(1024), index=True, unique=True),
    sa.Column("value", sa.Text),
)
