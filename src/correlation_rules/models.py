from datetime import datetime

from src.rules.models import SeverityHintEnum, severity_hint_enum_type
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class CorrelationRuleModel(Base):
    """
    Модель правила корреляции инцидентов безопасности (SIEM/SOC).
    """
    __tablename__ = "correlation_rules"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Уникальный идентификатор правила",
    )
    correlation_id: Mapped[str | None]
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Включено ли правило",
    )

    scenario_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Тип сценария, который формируется этим правилом",
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Описание логики правила",
    )

    window_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Максимальное временное окно между инцидентами (в секундах)",
    )

    sequence: Mapped[List[str]] = mapped_column(
        JSONB,  # Можно использовать ARRAY(String), если работаете строго в PostgreSQL
        nullable=False,
        comment="Последовательность типов инцидентов/атак, которые должны связаться",
    )

    group_by: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Поля, по которым инциденты считаются связанными",
    )

    min_unique_categories: Mapped[int | None] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Минимальное число уникальных категорий для срабатывания",
    )

    severity: Mapped[SeverityHintEnum] = mapped_column(
        severity_hint_enum_type,
        nullable=False,
        comment="Итоговая критичность сценария",
    )

    confidence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Уверенность правила, 0–100",
    )

    recommendations: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Рекомендации аналитику",
    )

    tags: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Теги правила",
    )
    created_by: Mapped[str]
    updated_by: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # func.now() в PostgreSQL возвращает TIMESTAMPTZ
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )