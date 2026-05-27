"""empty message

Revision ID: 759abaca0b70
Revises: f1006ab1fd89
Create Date: 2026-05-27 16:41:07.600158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '759abaca0b70'
down_revision: Union[str, Sequence[str], None] = 'f1006ab1fd89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
