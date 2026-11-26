"""auto в severity_hint правил обнаружения

Revision ID: 5e2b9d4c7a1f
Revises: 3f6a8c2e1b5d
Create Date: 2026-11-26 12:00:00.000000

detection_rules.severity_hint переводится на отдельный тип rule_severity_hint_enum (с auto).
Общий severity_hint_enum остаётся у correlation_rules.severity без изменений.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e2b9d4c7a1f'
down_revision: Union[str, Sequence[str], None] = '3f6a8c2e1b5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


rule_severity_hint_enum = sa.Enum(
    'auto', 'info', 'low', 'medium', 'high', 'critical', name='rule_severity_hint_enum'
)


def upgrade() -> None:
    """Upgrade schema."""
    rule_severity_hint_enum.create(op.get_bind(), checkfirst=True)
    op.execute(
        "ALTER TABLE detection_rules ALTER COLUMN severity_hint "
        "TYPE rule_severity_hint_enum USING severity_hint::text::rule_severity_hint_enum"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # В старом типе нет auto: такие версии правил становятся medium (прежнее значение по умолчанию)
    op.execute(
        "ALTER TABLE detection_rules ALTER COLUMN severity_hint "
        "TYPE severity_hint_enum USING (CASE WHEN severity_hint::text = 'auto' "
        "THEN 'medium' ELSE severity_hint::text END)::severity_hint_enum"
    )
    rule_severity_hint_enum.drop(op.get_bind(), checkfirst=True)
