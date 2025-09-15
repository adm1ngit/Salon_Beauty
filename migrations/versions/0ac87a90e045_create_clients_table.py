"""create clients table

Revision ID: 0ac87a90e045
Revises: b75c65805142
Create Date: 2025-09-13 17:04:03.589058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ac87a90e045'
down_revision: Union[str, Sequence[str], None] = 'b75c65805142'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
