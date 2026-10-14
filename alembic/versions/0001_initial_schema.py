
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing = set(sa.inspect(op.get_bind()).get_table_names())

    if "categories" not in existing:
        op.create_table(
            "categories",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint("id", name="pk_categories"),
            sa.UniqueConstraint("name", name="uq_categories_name"),
        )

    if "suppliers" not in existing:
        op.create_table(
            "suppliers",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=150), nullable=False),
            sa.Column("email", sa.String(length=150), nullable=True),
            sa.PrimaryKeyConstraint("id", name="pk_suppliers"),
            sa.UniqueConstraint("email", name="uq_suppliers_email"),
        )

    if "products" not in existing:
        op.create_table(
            "products",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("name", sa.String(length=150), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column(
                "quantity", sa.Integer(), server_default=sa.text("0"), nullable=False
            ),
            sa.Column("category_id", sa.Integer(), nullable=False),
            sa.Column("supplier_id", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
            sa.CheckConstraint(
                "quantity >= 0", name="ck_products_quantity_non_negative"
            ),
            sa.ForeignKeyConstraint(
                ["category_id"],
                ["categories.id"],
                name="fk_products_category_id_categories",
                ondelete="RESTRICT",
            ),
            sa.ForeignKeyConstraint(
                ["supplier_id"],
                ["suppliers.id"],
                name="fk_products_supplier_id_suppliers",
                ondelete="SET NULL",
            ),
            sa.PrimaryKeyConstraint("id", name="pk_products"),
        )


def downgrade() -> None:
    op.drop_table("products")
    op.drop_table("suppliers")
    op.drop_table("categories")
