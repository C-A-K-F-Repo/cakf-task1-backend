"""empty message

Revision ID: f1006ab1fd89
Revises: b219f19e7132
Create Date: 2026-05-27 16:40:27.859310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1006ab1fd89'
down_revision: Union[str, Sequence[str], None] = 'b219f19e7132'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
