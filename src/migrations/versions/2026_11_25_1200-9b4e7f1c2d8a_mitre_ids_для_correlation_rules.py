"""mitre_ids для correlation_rules

Revision ID: 9b4e7f1c2d8a
Revises: 7c1d2e9a4b3f
Create Date: 2026-11-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9b4e7f1c2d8a'
down_revision: Union[str, Sequence[str], None] = '7c1d2e9a4b3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('correlation_rules', sa.Column('mitre_ids', postgresql.JSONB(astext_type=sa.Text()),
                                                 server_default='[]', nullable=False,
                                                 comment='Техники MITRE ATT&CK'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('correlation_rules', 'mitre_ids')
