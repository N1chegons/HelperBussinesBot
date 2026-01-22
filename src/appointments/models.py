import datetime
import enum

from sqlalchemy import text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Status(enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str]
    title: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[Status] = mapped_column(default=Status.pending)
    appointment_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text(
            "TIMEZONE('utc', now())")
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    user = relationship("User", back_populates="appointments")