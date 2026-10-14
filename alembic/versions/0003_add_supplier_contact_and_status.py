
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("suppliers", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column(
        "suppliers", sa.Column("address", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "suppliers",
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("suppliers", "is_active")
    op.drop_column("suppliers", "address")
    op.drop_column("suppliers", "phone")
