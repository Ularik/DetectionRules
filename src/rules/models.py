from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from sqlalchemy import String, Boolean, DateTime, Enum as SAEnum, Integer, CheckConstraint, func, ARRAY
from datetime import datetime
from enum import Enum

class SeverityHintEnum(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionRuleModel(Base):
    __tablename__ = "detection_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # Неизменяемый ID
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    rule_type: Mapped[str | None] = mapped_column(String(100))
    scope: Mapped[str | None] = mapped_column(String(50))
    match_type: Mapped[str | None] = mapped_column(String(50))
    pattern: Mapped[str] = mapped_column(String(500))
    fields: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
        default=list)
    case_sensitive: Mapped[bool] = mapped_column(default=False)
    category: Mapped[str | None] = mapped_column(String(100))
    attack_type: Mapped[str | None] = mapped_column(String(100))
    scenario_type: Mapped[str | None] = mapped_column(String(100))
    mitre_ids: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
        default=list
    )   # T1190
    tactics:Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
        default=list
    )     # Initial Access
    severity_hint: Mapped[SeverityHintEnum] = mapped_column(
        SAEnum(SeverityHintEnum, name="severity_hint_enum"),
        nullable=False
    )
    confidence: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="check_confidence_range"),
    )
    description: Mapped[str | None] = mapped_column(String(500))
    explanation_template: Mapped[str | None] = mapped_column(String(500))
    recommendations: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)),
        nullable=True,
        default=list
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
        default=list
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.timezone('Asia/Bishkek', func.now()))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        server_default=func.now())
    created_by: Mapped[str] = mapped_column(String(50))
    updated_by: Mapped[str] = mapped_column(String(50))
