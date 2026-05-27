"""empty message

Revision ID: 24ecc34c0423
Revises: 9c1d2e3f4a5b
Create Date: 2026-05-27 16:35:57.653925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24ecc34c0423'
down_revision: Union[str, Sequence[str], None] = '9c1d2e3f4a5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
