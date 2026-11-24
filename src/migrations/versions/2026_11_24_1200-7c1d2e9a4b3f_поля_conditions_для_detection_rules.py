"""поля conditions, condition_mode, enabled_reason, false_positive_notes для detection_rules

Revision ID: 7c1d2e9a4b3f
Revises: 4355008ac21b
Create Date: 2026-11-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7c1d2e9a4b3f'
down_revision: Union[str, Sequence[str], None] = '4355008ac21b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('detection_rules', sa.Column('condition_mode', sa.String(length=10), server_default='all', nullable=False))
    op.add_column('detection_rules', sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False))
    op.add_column('detection_rules', sa.Column('enabled_reason', sa.String(length=500), nullable=True))
    op.add_column('detection_rules', sa.Column('false_positive_notes', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('detection_rules', 'false_positive_notes')
    op.drop_column('detection_rules', 'enabled_reason')
    op.drop_column('detection_rules', 'conditions')
    op.drop_column('detection_rules', 'condition_mode')
