"""empty message

Revision ID: b219f19e7132
Revises: 24ecc34c0423
Create Date: 2026-05-27 16:39:51.409552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b219f19e7132'
down_revision: Union[str, Sequence[str], None] = '24ecc34c0423'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
