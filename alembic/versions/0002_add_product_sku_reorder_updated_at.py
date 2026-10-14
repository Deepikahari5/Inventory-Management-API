
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("sku", sa.String(length=50), nullable=True))
    op.add_column(
        "products",
        sa.Column(
            "reorder_level", sa.Integer(), server_default=sa.text("10"), nullable=False
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.execute(
        "UPDATE products SET sku = CONCAT('SKU-', LPAD(id, 5, '0')) WHERE sku IS NULL"
    )

    op.alter_column(
        "products", "sku", existing_type=sa.String(length=50), nullable=False
    )
    op.create_unique_constraint("uq_products_sku", "products", ["sku"])
    op.create_check_constraint(
        "ck_products_reorder_level_non_negative", "products", "reorder_level >= 0"
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_products_reorder_level_non_negative", "products", type_="check"
    )
    op.drop_constraint("uq_products_sku", "products", type_="unique")
    op.drop_column("products", "updated_at")
    op.drop_column("products", "reorder_level")
    op.drop_column("products", "sku")
