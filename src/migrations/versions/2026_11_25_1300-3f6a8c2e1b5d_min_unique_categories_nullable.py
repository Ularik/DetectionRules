"""min_unique_categories в correlation_rules необязательное

Revision ID: 3f6a8c2e1b5d
Revises: 9b4e7f1c2d8a
Create Date: 2026-11-25 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f6a8c2e1b5d'
down_revision: Union[str, Sequence[str], None] = '9b4e7f1c2d8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('correlation_rules', 'min_unique_categories',
                    existing_type=sa.Integer(), nullable=True,
                    existing_comment='Минимальное число уникальных категорий для срабатывания')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE correlation_rules SET min_unique_categories = 1 WHERE min_unique_categories IS NULL")
    op.alter_column('correlation_rules', 'min_unique_categories',
                    existing_type=sa.Integer(), nullable=False,
                    existing_comment='Минимальное число уникальных категорий для срабатывания')
