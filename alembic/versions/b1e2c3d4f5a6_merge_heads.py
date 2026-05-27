"""merge order_deletion and product/order-items heads

Revision ID: b1e2c3d4f5a6
Revises: 586abff80514, 2ac6045c839d
Create Date: 2026-05-27 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1e2c3d4f5a6'
down_revision: Union[str, Sequence[str], None] = ('586abff80514', '2ac6045c839d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
