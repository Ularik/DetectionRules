from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, func, ForeignKey
from src.database import Base
from datetime import datetime


class Audit(Base):
    __tablename__ = "audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(50), default="create")
    resource_type: Mapped[str | None] = mapped_column(String(70))
    rule_general_id: Mapped[str]
    rule_unique_id: Mapped[str] = mapped_column(ForeignKey("detection_rules.unique_id", ondelete="CASCADE"))
    before_id: Mapped[int | None] = mapped_column(ForeignKey("audit.id", ondelete="SET NULL"))
    after_id: Mapped[int | None] = mapped_column(ForeignKey("audit.id", ondelete="SET NULL"))

    author: Mapped["Users"] = relationship("Users")
    rule: Mapped["DetectionRuleModel"] = relationship("DetectionRuleModel")

    before: Mapped["Audit | None"] = relationship(
        "Audit",
        foreign_keys=[before_id],
        remote_side=[id]
    )
    after: Mapped["Audit | None"] = relationship(
        "Audit",
        foreign_keys=[after_id],
        remote_side=[id]
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.timezone('Asia/Bishkek', func.now()))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone('Asia/Bishkek', func.now()),
        onupdate=func.timezone('Asia/Bishkek', func.now())
    )