"""name для correlation_rules

Revision ID: 8d3a6f2b9c4e
Revises: 5e2b9d4c7a1f
Create Date: 2026-11-26 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d3a6f2b9c4e'
down_revision: Union[str, Sequence[str], None] = '5e2b9d4c7a1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('correlation_rules', sa.Column('name', sa.String(length=200), nullable=True,
                                                 comment='Отображаемое название правила'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('correlation_rules', 'name')
