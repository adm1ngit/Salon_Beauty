"""make email nullable

Revision ID: 2d02f0f4c469
Revises: 
Create Date: 2025-09-10 13:43:48.808850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '2d02f0f4c469'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(100), nullable=False, unique=True),
        # boshqa ustunlar...
    )

def downgrade():
    op.drop_table('clients')
