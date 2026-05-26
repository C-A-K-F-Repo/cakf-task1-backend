"""empty message

Revision ID: 2ac6045c839d
Revises: 1875dc4da330, a08aaf9d185e
Create Date: 2026-05-26 14:23:49.989223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ac6045c839d'
down_revision: Union[str, Sequence[str], None] = ('1875dc4da330', 'a08aaf9d185e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
